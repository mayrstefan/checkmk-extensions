#!/usr/bin/env python3

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import DefaultValue, DictElement, Dictionary, ServiceState
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic

def _parameter_form_keepalived_vrrp_track_process() -> Dictionary:
    return Dictionary(
        elements = {
            "have_quorum_true": DictElement(
                parameter_form = ServiceState(
                    title = Title("State if quorum is reached"),
                    prefill = DefaultValue(ServiceState.OK)
                )
            ),
            "have_quorum_false": DictElement(
                parameter_form = ServiceState(
                    title = Title("State if quorum is not reached"),
                    prefill = DefaultValue(ServiceState.CRIT)
                )
            )
        }
    )

rule_spec_keepalived_vrrp_track_process = CheckParameters(
    name = "keepalived_vrrp_track_process",
    title = Title("Keepalived VRRP track process (Linux)"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_form_keepalived_vrrp_track_process,
    condition = HostAndItemCondition(item_title=Title("Keepalived VRRP track process"))
)
