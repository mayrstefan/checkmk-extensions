#!/usr/bin/env python3
import json
from collections.abc import Mapping # type: ignore
from typing import Any # type: ignore
from cmk.agent_based.v2 import (
    AgentSection,
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

vrrp_states = {
    # https://github.com/acassen/keepalived/blob/8b2877ef5754a0a0ff5654f0508784d9a71fbc1e/keepalived/include/vrrp.h#L414-L420
    # RFC 2338
    0: { 'name': 'INIT', 'result': State.OK },
    1: { 'name': 'BACKUP', 'result': State.OK },
    2: { 'name': 'MASTER', 'result': State.OK },
    3: { 'name': 'FAULT', 'result': State.CRIT },
    # additional keepalived states
    97: { 'name': 'DELETED', 'result': State.OK },
    98: { 'name': 'STOP', 'result': State.CRIT }
    }

def parse_keepalived_vrrp(string_table: StringTable) -> Section:
    if len(string_table) == 0:
        return {}
    section = json.loads(string_table[0][0])
    if isinstance(section, list):
        section = {'vrrp': section}
    return section

def discover_keepalived_vrrp(section: Section) -> DiscoveryResult:
    for instance in section.get('vrrp', []):
        yield Service(item=instance['data']['iname'])

def check_keepalived_vrrp(item: str, section: Section) -> CheckResult:
    for instance in section.get('vrrp', []):
        if item == instance['data']['iname']:
            vrrp_state = instance['data']['state']
            if vrrp_state in vrrp_states:
                state = vrrp_states[vrrp_state]['result']
                state_pretty = vrrp_states[vrrp_state]['name']
            else:
                state = State.UNKNOWN
                state_pretty = f'Unknown state { vrrp_state }'
            # all metrics we have are simple counters
            for metric_name, metric_value in instance['stats'].items():
                yield Metric(f'keepalived_{ metric_name }', metric_value)
            vips = '-' # default: empty
            if 'vips' in instance['data']:
                vips = ", ".join(instance['data']['vips'])
            yield Result(
                state = state,
                summary = f"State: { state_pretty }, VIPs: { vips  }"
            )

agent_section_keepalived_vrrp = AgentSection(
    name = "keepalived_vrrp",
    parse_function = parse_keepalived_vrrp,
)

check_plugin_keepalived_vrrp = CheckPlugin(
    name = "keepalived_vrrp",
    service_name = "Keepalived VRRP instance %s",
    discovery_function = discover_keepalived_vrrp,
    check_function = check_keepalived_vrrp,
)
