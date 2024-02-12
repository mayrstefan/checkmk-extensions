#!/usr/bin/env python3

from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)
from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import RulespecGroupMonitoringAgentsAgentPlugins
from cmk.gui.valuespec import (
    Age,
    Dictionary,
    TextAscii,
)

def _valuespec_keepalived_vrrp():
    return Dictionary(
        title=_("Keepalived VRRP (Linux)"),
        help=_("This will deploy the keepalived_vrrp plugin."),
        elements=[
            ("pidfile", TextAscii(
                title=_("Keepalived pidfile (Default: /var/run/keepalived.pid)"),
                allow_empty=False,
            )),
            ("jsonfile", TextAscii(
                title=_("Keepalived JSON status file (Default: /tmp/keepalived.json)"),
                allow_empty=False,
            )),
            ("interval",
             Age(
                 title=_("Run asynchronously"),
                 label=_("Interval for collecting data"),
                 default_value=300, # default: 5 minutes
             )),
        ],
        optional_keys=["pidfile", "jsonfile", "interval"],
    )

rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsAgentPlugins,
        name="agent_config:keepalived_vrrp",
        valuespec=_valuespec_keepalived_vrrp,
    ))
