#!/usr/bin/env python3
# Shebang needed only for editors

from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    Dictionary,
    DictElement,
    FixedValue,
    String,
    Password,
    migrate_to_password,
    validators,
)
from cmk.rulesets.v1 import Help, Label, Title
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _formspec():
    return Dictionary(
        title=Title("HAProxy Fusion Special Agent"),
        help_text=Help("Get HAProxy Fusion Health."),
        elements={
            "url": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("URL for /v2/healthz or /v2/healthz/fusion endpoint"),
                    custom_validate=(
                        validators.Url(
                            protocols=[
                                validators.UrlProtocol.HTTP,
                                validators.UrlProtocol.HTTPS,
                            ]
                        ),
                    ),
                ),
            ),
            "auth": DictElement(
                required=True,
                parameter_form=CascadingSingleChoice(
                    title=Title("Authentication type"),
                    prefill=DefaultValue("none"),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="none",
                            title=Title("Anonymous access"),
                            parameter_form=FixedValue(value=None),
                        ),
                        CascadingSingleChoiceElement(
                            name="basic",
                            title=Title("HTTP Basic Authentication"),
                            parameter_form=Dictionary(
                                elements={
                                    "username": DictElement(
                                        required=True,
                                        parameter_form=String(
                                            title=Title("Username"),
                                            custom_validate=(
                                                validators.LengthInRange(min_value=1),
                                            ),
                                        ),
                                    ),
                                    "password": DictElement(
                                        required=True,
                                        parameter_form=Password(
                                            title=Title("Password"),
                                            custom_validate=(
                                                validators.LengthInRange(min_value=1),
                                            ),
                                            migrate=migrate_to_password,
                                        ),
                                    ),
                                }
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="apikey",
                            title=Title("API-Key"),
                            parameter_form=Dictionary(
                                elements={
                                    "key": DictElement(
                                        required=True,
                                        parameter_form=Password(
                                            title=Title("API-Key"),
                                            custom_validate=(
                                                validators.LengthInRange(min_value=1),
                                            ),
                                            migrate=migrate_to_password,
                                        ),
                                    ),
                                }
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="x_api_key",
                            title=Title("X-API-Key"),
                            parameter_form=Dictionary(
                                elements={
                                    "key": DictElement(
                                        required=True,
                                        parameter_form=Password(
                                            title=Title("X-API-Key"),
                                            custom_validate=(
                                                validators.LengthInRange(min_value=1),
                                            ),
                                            migrate=migrate_to_password,
                                        ),
                                    ),
                                }
                            ),
                        ),
                        CascadingSingleChoiceElement(
                            name="x_fusion_apikey",
                            title=Title("X-Fusion-ApiKey"),
                            parameter_form=Dictionary(
                                elements={
                                    "key": DictElement(
                                        required=True,
                                        parameter_form=Password(
                                            title=Title("X-Fusion-ApiKey"),
                                            custom_validate=(
                                                validators.LengthInRange(min_value=1),
                                            ),
                                            migrate=migrate_to_password,
                                        ),
                                    ),
                                }
                            ),
                        ),
                    ],
                ),
            ),
            "verify": DictElement(
                parameter_form=BooleanChoice(
                    title=Title("Verify TLS Connection"),
                    label=Label("enabled"),
                    prefill=DefaultValue(value=True),
                ),
            ),
        },
    )


rule_spec_haproxy_fusion = SpecialAgent(
    topic=Topic.NETWORKING,
    name="haproxy_fusion",
    title=Title("HAProxy Fusion Health"),
    parameter_form=_formspec,
)
