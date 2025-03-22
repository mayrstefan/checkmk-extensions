#!/usr/bin/env python3

from cmk.rulesets.v1 import Label, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    String,
    TimeSpan,
    TimeMagnitude
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic

def _parameter_form_keepalived_vrrp_bakery():
    return Dictionary(
        #help=_("This will deploy the keepalived_vrrp plugin."),
        elements = {
            "pidfile": DictElement(
                parameter_form = String(
                    title = Title("Keepalived pidfile (Default: /var/run/keepalived.pid)"),
                #allow_empty=False,
                )
            ),
            "jsonfile": DictElement(
                parameter_form = String(
                    title = Title("Keepalived JSON status file (Default: /tmp/keepalived.json)"),
                #allow_empty=False,
                )
            ),
            "interval": DictElement(
                parameter_form = TimeSpan(
                    title = Title("Run asynchronously"),
                    label = Label("Interval for collecting data"),
                    displayed_magnitudes = [TimeMagnitude.SECOND],
                    prefill = DefaultValue(300.0) # default: 5 minutes
                )
            )
        }
    )

rule_spec_keepalived_vrrp_bakery = AgentConfig(
    name = "keepalived_vrrp",
    title = Title("Keepalived VRRP (Linux)"),
    topic = Topic.GENERAL,
    parameter_form = _parameter_form_keepalived_vrrp_bakery
)
