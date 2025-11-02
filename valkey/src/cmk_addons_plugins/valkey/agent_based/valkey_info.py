#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.


from collections.abc import Mapping
from typing import Any

from cmk.agent_based.v2 import CheckPlugin, CheckResult, DiscoveryResult, Result, Service, State
from cmk.plugins.lib.uptime import check as check_uptime_seconds
from cmk.plugins.lib.uptime import Section as UptimeSection
from cmk_addons.plugins.valkey.agent_based.valkey_base import Section

# <<<valkey_info>>>
# [[[MY_FIRST_VALKEY|127.0.0.1|6380]]]
# ...

#   .--Server--------------------------------------------------------------.
#   |                   ____                                               |
#   |                  / ___|  ___ _ ____   _____ _ __                     |
#   |                  \___ \ / _ \ '__\ \ / / _ \ '__|                    |
#   |                   ___) |  __/ |   \ V /  __/ |                       |
#   |                  |____/ \___|_|    \_/ \___|_|                       |
#   |                                                                      |
#   +----------------------------------------------------------------------+
#   |                                                                      |
#   '----------------------------------------------------------------------'

# ...
# Server
# valkey_version:8.1.1
# redis_git_sha1:00000000
# redis_git_dirty:0
# redis_build_id:fa41aec701bdce55
# server_mode:standalone
# os:Linux 6.1.0-37-amd64 x86_64
# arch_bits:64
# multiplexing_api:epoll
# gcc_version:14.2.0
# process_id:1029
# run_id:27bb4e37e85094b590b4693d6c6e11d07cd6400a
# tcp_port:6380
# uptime_in_seconds:29349
# uptime_in_days:0
# hz:10
# lru_clock:15193378
# executable:/usr/bin/valkey-server
# config_file:/etc/valkey/valkey2.conf
#
# Description of possible output:
# valkey_version: Version of the Valkey server
# valkey_git_sha1: Git SHA1
# valkey_git_dirty: Git dirty flag
# valkey_build_id: The build id
# server_mode: The server's mode ("standalone", "sentinel" or "cluster")
# os: Operating system hosting the Valkey server
# arch_bits: Architecture (32 or 64 bits)
# multiplexing_api: Event loop mechanism used by Valkey
# gcc_version: Version of the GCC compiler used to compile the Valkey server
# process_id: PID of the server process
# run_id: Random value identifying the Valkey server (to be used by Sentinel and Cluster)
# tcp_port: TCP/IP listen port
# uptime_in_seconds: Number of seconds since Valkey server start
# uptime_in_days: Same value expressed in days
# hz: The server's frequency setting
# lru_clock: Clock incrementing every minute, for LRU management
# executable: The path to the server's executable
# config_file: The path to the config file


def discover_valkey_info(section: Section) -> DiscoveryResult:
    yield from (Service(item=item) for item in section)


def check_valkey_info(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if not (item_data := section.get(item)):
        return

    if (error := item_data.get("error")) is not None:
        yield Result(state=State.CRIT, summary=f"Error: {error}")

    server_data = item_data.get("Server")
    if server_data is None:
        return

    server_mode = server_data.get("server_mode")
    if server_mode is not None:
        mode_state = State.OK
        infotext = "Mode: %s" % server_mode.title()
        mode_params = params.get("expected_mode")
        if mode_params is not None:
            if mode_params != server_mode:
                mode_state = State.WARN
                infotext += " (expected: %s)" % mode_params.title()

        yield Result(state=mode_state, summary=infotext)

    server_uptime = server_data.get("uptime_in_seconds")
    if server_uptime is not None:
        yield from check_uptime_seconds(
            params, UptimeSection(uptime_sec=server_uptime, message=None)
        )

    for key, infotext in [
        ("valkey_version", "Version"),
        ("gcc_version", "GCC compiler version"),
        ("process_id", "PID"),
    ]:
        value = server_data.get(key)
        if value is not None:
            yield Result(state=State.OK, summary=f"{infotext}: {value}")

    host_data = item_data.get("host")
    if host_data is not None:
        addr = "Socket" if item_data.get("port") == "unix-socket" else "IP"
        yield Result(state=State.OK, summary=f"{addr}: {host_data}")

    port_data = item_data.get("port")
    if port_data is not None and port_data != "unix-socket":
        yield Result(state=State.OK, summary="Port: %s" % port_data)


check_plugin_valkey_info = CheckPlugin(
    name="valkey_info",
    service_name="Valkey %s Server Info",
    discovery_function=discover_valkey_info,
    check_function=check_valkey_info,
    check_ruleset_name="valkey_info",
    check_default_parameters={},
)
