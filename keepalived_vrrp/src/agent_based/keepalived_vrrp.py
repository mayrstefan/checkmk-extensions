#!/usr/bin/env python3
from .agent_based_api.v1 import Metric, register, Result, Service, State
import json

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

def parse_keepalived_vrrp(string_table):
    if len(string_table) == 0:
        return []
    return json.loads(string_table[0][0])

def discover_keepalived_vrrp(section):
    for instance in section:
        yield Service(item=instance['data']['iname'])

def check_keepalived_vrrp(item, section):
    for instance in section:
        if item == instance['data']['iname']:
            vrrp_state = instance['data']['state']
            if vrrp_state in vrrp_states:
                state = vrrp_states[vrrp_state]['result']
                state_pretty = vrrp_states[vrrp_state]['name']
            else:
                state = State.UNKNOWN
                state_pretty = 'Unknown state %i' % vrrp_state
            # all metrics we have are simple counters
            for k, v in instance['stats'].items():
                yield Metric('keepalived_%s' % k, v)
            vips = '-' # default: empty
            if 'vips' in instance['data']:
                vips = ", ".join(instance['data']['vips'])
            yield Result(
                    state = state,
                    summary = "State: %s, VIPs: %s" % (state_pretty, vips))
            return

register.agent_section(
    name = "keepalived_vrrp",
    parse_function = parse_keepalived_vrrp,
)

register.check_plugin(
    name = "keepalived_vrrp",
    service_name = "Keepalived VRRP instance %s",
    discovery_function = discover_keepalived_vrrp,
    check_function = check_keepalived_vrrp,
)
