#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Any

from cmk.rulesets.v1 import Label, Title, Help
from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    Integer,
    InputHint,
    List,
    Password,
    String,
)
from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _migrate(value: object) -> Any:
    """
    >>> _migrate(("instance", "host", 4444, "pa$$word"))
    {'instance': 'instance', 'password': 'pa$$word', 'connection': ('tcp', {'host': 'host', 'port': 4444})}
    """
    if isinstance(value, tuple):
        instance, host, port, password = value
        return {
            "instance": instance,
            "password": password,
            "connection": ("tcp", {"host": host, "port": port}),
        }
    return value


def _parameter_form_valkey_bakery() -> Dictionary:
    return Dictionary(
        elements={
            "deployment": DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title("Valkey databases"),
                    help_text=Help(
                        "If you activate this option, then the agent plug-in <tt>valkey</tt> will be deployed. "
                        "           You can configure multiple instances or auto detect running instances."
                    ),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="autodetect",
                            title=Title("Autodetect instances"),
                            parameter_form=FixedValue(value=None),
                        ),
                        CascadingSingleChoiceElement(
                            name="static",
                            title=Title("Specific list of instances"),
                            parameter_form=List(
                                element_template=Dictionary(
                                    elements={
                                        "instance": DictElement(
                                            parameter_form=String(
                                                title=Title(
                                                    "Name of the instance in the monitoring"
                                                ),
                                            ),
                                            required=True,
                                        ),
                                        "connection": DictElement(
                                            parameter_form=CascadingSingleChoice(
                                                title=Title("Connection"),
                                                elements=[
                                                    CascadingSingleChoiceElement(
                                                        name="tcp",
                                                        title=Title("TCP"),
                                                        parameter_form=Dictionary(
                                                            elements={
                                                                "host": DictElement(
                                                                    parameter_form=String(
                                                                        title=Title(
                                                                            "IPv4 address"
                                                                        ),
                                                                        prefill=DefaultValue(
                                                                            "127.0.0.1"
                                                                        ),
                                                                    ),
                                                                    required=True,
                                                                ),
                                                                "port": DictElement(
                                                                    parameter_form=Integer(
                                                                        title=Title(
                                                                            "TCP port number"
                                                                        ),
                                                                        prefill=DefaultValue(
                                                                            6379
                                                                        ),
                                                                    ),
                                                                    required=True,
                                                                ),
                                                            }
                                                        ),
                                                    ),
                                                    CascadingSingleChoiceElement(
                                                        name="unixsocket",
                                                        title=Title("Unix-Socket"),
                                                        parameter_form=Dictionary(
                                                            elements={
                                                                "socket": DictElement(
                                                                    parameter_form=String(
                                                                        title=Title(
                                                                            "Path to unix socket"
                                                                        ),
                                                                    ),
                                                                    required=True,
                                                                ),
                                                            }
                                                        ),
                                                    ),
                                                ],
                                                prefill=DefaultValue("tcp"),
                                            ),
                                        ),
                                        "password": DictElement(
                                            parameter_form=Password(
                                                title=Title("Password"),
                                            ),
                                        ),
                                    },
                                ),
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="do_not_deploy",
                            title=Title("Do not deploy the Valkey plug-in"),
                            parameter_form=FixedValue(value=None),
                        ),
                    ],
                    prefill=DefaultValue("autodetect"),
                ),
            ),
        },
    )


rule_spec_valkey_bakery = AgentConfig(
    name="valkey",
    title=Title("Valkey databases"),
    topic=Topic.DATABASES,
    parameter_form=_parameter_form_valkey_bakery,
)
