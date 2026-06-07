#!/usr/bin/env python3
# Shebang needed only for editors

from cmk.rulesets.v1.form_specs import (
    Dictionary,
    DictElement,
    String,
    Password,
    migrate_to_password,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic, Help, Title


def _formspec():
    return Dictionary(
        title=Title("Checkly"),
        help_text=Help("Queries ChecklyHQ API for all service statuses."),
        elements={
            "account": DictElement(
                required=True,
                parameter_form=String(
                    title=Title("Account-ID"),
                ),
            ),
            "token": DictElement(
                required=True,
                parameter_form=Password(
                    title=Title("Bearer token"),
                    migrate=migrate_to_password,
                ),
            ),
        },
    )


rule_spec_checkly = SpecialAgent(
    topic=Topic.CLOUD,
    name="checkly",
    title=Title("Checkly service statuses"),
    parameter_form=_formspec,
)
