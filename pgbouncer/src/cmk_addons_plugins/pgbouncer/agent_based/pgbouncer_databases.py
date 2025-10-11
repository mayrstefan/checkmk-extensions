#!/usr/bin/env python3
from collections.abc import Mapping
from typing import Any
from cmk.agent_based.v2 import (
    AgentSection,
    check_levels,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State,
    StringTable
)

Section = Mapping[str, Any]

def parse_pgbouncer_databases(string_table: StringTable) -> Section:
    databases = {}
    instance_name = ""
    instance_linecount = 0
    instance_columns = []
    for line in string_table:
        if line[0].startswith("[[[") and line[0].endswith("]]]"):
            instance_name = line[0][3:-3]
            instance_linecount = 0
            continue
        instance_linecount += 1
        # First line has column names
        if instance_linecount == 1:
            instance_columns = line
            continue
        # regular line represents a database
        database = {}
        for i in range(0, len(instance_columns)):
            database[instance_columns[i]] = line[i]
        database_name = "%s/%s" % (instance_name, database["name"])
        databases[database_name] = database
    return databases

def discover_pgbouncer_databases(section: Section) -> DiscoveryResult:
    for database in section.keys():
        yield Service(item=database)

def check_pgbouncer_databases(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    database = section.get(item)
    if not database:
        yield Result(state=State.UNKNOWN, summary="database has been deleted")
        return

    max_connections = float(database["max_connections"])
    if max_connections == 0:
        # fallback, use pool size if max_connections is not set
        if "reserve_pool" in database:
            max_connections = float(database["pool_size"]) + float(database["reserve_pool"])
        else:
            max_connections = float(database["pool_size"]) + float(database["reserve_pool_size"])
    connection_usage = float(database["current_connections"]) / max_connections

    yield Result(
               state=State.OK,
               summary="Connection usage: %.0f%%" % (100.0 * connection_usage),
               details="Host: %s, Port: %s, Database: %s, Mode: %s" % (database["host"], database["port"], database["database"], database["pool_mode"])
               )

    yield from check_levels(
            100.0 * connection_usage,
            levels_upper=(params["connection_usage_warn_crit"]),
            metric_name="connection_usage",
            label="Connection usage in %",
            boundaries=(0.0, 100.0),
            notice_only=True
            )

    for metric_name in ("pool_size", "reserve_pool", "reserve_pool_size", "max_connections", "current_connections"):
        if metric_name in database:
            yield Metric(name=metric_name, value=float(database[metric_name]), boundaries=(0.0, None))

agent_section_pgbouncer = AgentSection(
    name="pgbouncer_databases",
    parse_function=parse_pgbouncer_databases,
)

check_plugin_pgbouncer = CheckPlugin(
    name="pgbouncer_databases",
    service_name="PgBouncer Database connections %s",
    discovery_function=discover_pgbouncer_databases,
    check_function=check_pgbouncer_databases,
    check_default_parameters={ "connection_usage_warn_crit": ("fixed", (90.0, 95.0)) },
    check_ruleset_name="pgbouncer_databases"
)
