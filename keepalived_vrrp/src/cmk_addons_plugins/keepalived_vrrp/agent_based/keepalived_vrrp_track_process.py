#!/usr/bin/env python3
from collections.abc import Mapping
from typing import Any
from cmk.agent_based.v2 import (
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Metric,
    Result,
    Service,
    State
)
from cmk.rulesets.v1.form_specs import ServiceState

Section = Mapping[str, Any]

def discover_keepalived_vrrp_track_process(section: Section) -> DiscoveryResult:
    for instance in section.get('track_process', []):
        yield Service(item=instance['process'])

def check_keepalived_vrrp_track_process(item: str, params: dict, section: Section) -> CheckResult:
    for instance in section.get('track_process', []):
        if item == instance['process']:
            have_quorum = instance['have_quorum']
            current_processes = instance['current_processes']
            min_processes = instance.get('min_processes')
            max_processes = instance.get('max_processes')
            # Apply state for quorum
            if have_quorum:
                state = State(params['have_quorum_true'])
                summary = 'Has quorum'
            else:
                state = State(params['have_quorum_false'])
                summary = 'Does not have quorum'
            # add reason to summary
            if min_processes and current_processes < min_processes:
                summary += ": did not reach minimal process count of " + \
                        f"{ min_processes } (is { current_processes})"
            if max_processes and max_processes < current_processes:
                summary += ": exceeded maximal process count of " + \
                        f"{ max_processes } (is { current_processes})"
            yield Result(
                state = state,
                summary = summary
            )
            yield Metric(
                name = 'processes',
                value = current_processes
            )

check_plugin_keepalived_vrrp_track_process = CheckPlugin(
    name = "keepalived_vrrp_track_process",
    sections = ["keepalived_vrrp"],
    service_name = "Keepalived VRRP track process %s",
    discovery_function = discover_keepalived_vrrp_track_process,
    check_function = check_keepalived_vrrp_track_process,
    check_default_parameters = {
        'have_quorum_true': ServiceState.OK,
        'have_quorum_false': ServiceState.CRIT
    },
    check_ruleset_name = "keepalived_vrrp_track_process"
)
