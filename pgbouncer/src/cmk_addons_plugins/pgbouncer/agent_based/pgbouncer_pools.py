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

def parse_pgbouncer_pools(string_table: StringTable) -> Section:
    pools = {}
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
        # regular line represents a pool
        pool = {}
        for i in range(0, len(instance_columns)):
            pool[instance_columns[i]] = line[i]
        pool_name = "%s/%s/%s" % (instance_name, pool["database"], pool["user"])
        pools[pool_name] = pool
    return pools

def discover_pgbouncer_pools(section: Section) -> DiscoveryResult:
    for pool in section.keys():
        yield Service(item=pool)

def check_pgbouncer_pools(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    pool = section.get(item)
    if not pool:
        yield Result(state=State.UNKNOWN, summary="pool has been deleted")
        return
    maxwait = float(pool["maxwait_us"])/1000000
    yield Result(state=State.OK, summary="%.2f seconds" % (maxwait), details="Mode: %s" % (pool["pool_mode"]))

    yield from check_levels(
            maxwait,
            levels_upper=(params["maxwait_warn_crit"]),
            metric_name="maxwait",
            label="Maximum waiting time in seconds",
            boundaries=(0.0, None),
            notice_only=True
            )

    for metric_name in ("cl_active", "cl_waiting", "sv_active", "sv_idle", "sv_used", "sv_tested", "sv_login"):
        yield Metric(name=metric_name, value=float(pool[metric_name]), boundaries=(0.0, None))

agent_section_pgbouncer_pools = AgentSection(
    name="pgbouncer_pools",
    parse_function=parse_pgbouncer_pools,
)

check_plugin_pgbouncer_pools = CheckPlugin(
    name="pgbouncer_pools",
    service_name="PgBouncer Pool maxwait %s",
    discovery_function=discover_pgbouncer_pools,
    check_function=check_pgbouncer_pools,
    check_default_parameters={ "maxwait_warn_crit": ("fixed", (5, 10)) },
    check_ruleset_name="pgbouncer_pools"
)
