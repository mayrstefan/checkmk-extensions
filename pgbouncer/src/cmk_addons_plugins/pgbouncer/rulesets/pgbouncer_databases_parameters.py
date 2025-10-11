#!/usr/bin/env python3

from cmk.rulesets.v1 import form_specs, Help, rule_specs, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    LevelDirection,
    Percentage,
    SimpleLevels,
    String
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic

def _parameter_form_pgbouncer_databases() -> Dictionary:
    return Dictionary(
        elements={
            "connection_usage_warn_crit": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Connection usage threshold of pgbouncer database"),
                    form_spec_template=Percentage(),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(90.0, 95.0))
                )
            )
        }
    )

rule_spec_pgbouncer_databases = CheckParameters(
    name="pgbouncer_databases",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_form_pgbouncer_databases,
    title=Title("PgBouncer database connection usage"),
    condition=HostAndItemCondition(
        item_title=Title("PgBouncer database connection usage"),
        item_form=String(help_text=Help("You can restrict this rule to certain services of the specified hosts."))
    )
)
