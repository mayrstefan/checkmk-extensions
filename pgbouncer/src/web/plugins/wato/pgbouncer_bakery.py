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
    ListOf,
    Migrate,
    TextInput,
)

def _add_instance_name(instances_settings):
    if "instance_name" not in instances_settings:
        instances_settings["instance_name"] = ""
    return instances_settings

def _valuespec_instance_settings():
    return Migrate(
        migrate=_add_instance_name,
        valuespec=Dictionary(
            elements=[
                (
                    "instance_env_filepath",
                    TextInput(
                        title=_(
                            'The environment file of the PgBouncer instance. This file contains variables of the form PGPORT="6432". Check the header of the agent plugin for a more detailed description.'
                        )
                    ),
                ),
                (
                    "instance_name",
                    TextInput(
                        title=_("Instance name"),
                        help=_(
                            'The name of the instance to be monitored. If left empty, the instance name is determined based on the name of the environment file. For example, if you have specified the name "/home/postgres/db.env", then the plugin will remove the directory and the trailing ".env". This results in the instance name "db". Using this mechanism is not recommended. It is kept around for backwards compability.'
                        ),
                    ),
                ),
                (
                    "instance_username",
                    TextInput(
                        title=_(
                            "Instance username",
                        )
                    ),
                ),
                (
                    "instance_pgpass_filepath",
                    TextInput(
                        title=_(
                            "Path to .pgpass file",
                        )
                    ),
                ),
            ],
        ),
    )
def _valuespec_pgbouncer():
    return Dictionary(
        title=_("PgBouncer (Linux)"),
        help=_("This will deploy the pgbouncer plugin."),
        elements=[
            (
                "instance_settings",
                Dictionary(
                    title=_("Instances settings"),
                    optional_keys=[],
                    elements=[
                        (
                            "db_username",
                            TextInput(
                                title=_("DB username"),
                                allow_empty=False
                            )
                        ),
                        (
                            "instances",
                            ListOf(
                                valuespec=_valuespec_instance_settings(),
                                title=_("Monitor multiple instances on the host"),
                                add_label=_("Add instance to be monitored"),
                                allow_empty=False
                            )
                        )
                    ]
                )
            ),
            (
                "dbuser",
                TextInput(
                    title=_("DB username")
                )
            ),
            (
                "pghost",
                TextInput(
                    title=_("DB Host or Socket directory")
                )
            ),
            (
                "pgport",
                TextInput(
                    title=_("DB Port")
                )
            ),
            (
                "interval",
                Age(
                    title=_("Run asynchronously"),
                    label=_("Interval for collecting data"),
                    default_value=300, # default: 5 minutes
                )
            ),
        ],
        optional_keys=["instance_settings", "dbuser", "pghost", "pgport", "interval"],
    )

rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsAgentPlugins,
        name="agent_config:pgbouncer",
        valuespec=_valuespec_pgbouncer,
    ))
