#!/usr/bin/env python3
from cmk.agent_based.v2 import (
    CheckPlugin,
    Result,
    Service,
    State,
    check_levels,
)

def discover_keepalived_track_process(section):
    for instance in section.get('track_process', []):
        yield Service(item=instance['process'])

def check_keepalived_track_process(item, section):
    for instance in section.get('track_process', []):
        if item != instance['process']:
            continue

        have_quorum = instance['have_quorum']
        if have_quorum :
            yield Result(state=State.OK, summary= "Quorum")
        else:
            yield Result(state=State.WARN, summary= "No Quorum")

        yield from check_levels(
            instance['current_processes'],
            label='Processes',
            metric_name='keepalived_track_current_processes',
            levels_lower=('fixed', (instance['min_processes'], 0)),
            render_func=int,
        )
 

check_plugin_keepalived_track_process = CheckPlugin(
    name = "keepalived_track_process",
    sections=["keepalived_vrrp"],
    service_name = "Keepalived Track Process %s",
    discovery_function = discover_keepalived_track_process,
    check_function = check_keepalived_track_process,
)
