#!/usr/bin/env python3

from cmk.rulesets.v1 import Label, Help, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    List,
    String,
    TimeSpan,
    TimeMagnitude
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic

def _add_instance_name(instances_settings):
    if "instance_name" not in instances_settings:
        instances_settings["instance_name"] = ""
    return instances_settings

def _formspec_instance_settings() -> Dictionary:
    return Dictionary(
        elements={
            "instance_env_filepath": DictElement(
                parameter_form=String(
                     title=Title('The environment file of the PgBouncer instance. This file contains variables of the form PGPORT="6432". Check the header of the agent plugin for a more detailed description.')
                )
            ),
            "instance_name": DictElement(
                parameter_form=String(
                    title=Title("Instance name"),
                    help_text=Help('The name of the instance to be monitored. If left empty, the instance name is determined based on the name of the environment file. For example, if you have specified the name "/home/postgres/db.env", then the plugin will remove the directory and the trailing ".env". This results in the instance name "db". Using this mechanism is not recommended. It is kept around for backwards compability.')
                )
            ),
            "instance_username": DictElement(
                parameter_form=String(
                    title=Title("Instance username")
                )
            ),
            "instance_pgpass_filepath": DictElement(
                parameter_form=String(
                    title=Title("Path to .pgpass file")
                )
            )
        }
    )

def _parameter_form_pgbouncer_bakery() -> Dictionary:
    return Dictionary(
        help_text=Help("This will deploy the pgbouncer plugin."),
        elements={
            "instance_settings": DictElement(
                parameter_form=Dictionary(
                    title=Title("Instances settings"),
                    elements={
                        "db_username": DictElement(
                            parameter_form=String(
                                title=Title("DB username"),
                                #allow_empty=False
                            )
                        ),
                        "instances": DictElement(
                            parameter_form=List(
                                element_template=_formspec_instance_settings(),
                                title=Title("Monitor multiple instances on the host"),
                                add_element_label=Label("Add instance to be monitored"),
                                remove_element_label=Label("Remove instance to be monitored"),
                            )
                        )
                    }
                )
            ),
            "dbuser": DictElement(
                parameter_form=String(
                    title=Title("DB username")
                )
            ),
            "pghost": DictElement(
                parameter_form=String(
                    title=Title("DB Host or Socket directory")
                )
            ),
            "pgport": DictElement(
                parameter_form=String(
                    title=Title("DB Port")
                )
            ),
            "interval": DictElement(
                parameter_form=TimeSpan(
                    title=Title("Run asynchronously"),
                    label=Label("Interval for collecting data"),
                    displayed_magnitudes=[TimeMagnitude.SECOND, TimeMagnitude.MINUTE],
                    prefill=DefaultValue(300.0), # default: 5 minutes
                )
            )
        }
    )

rule_spec_pgbouncer_bakery = AgentConfig(
    name="pgbouncer",
    title=Title("PgBouncer (Linux)"),
    topic=Topic.GENERAL,
    parameter_form=_parameter_form_pgbouncer_bakery
)
