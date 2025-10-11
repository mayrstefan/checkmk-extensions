#!/usr/bin/env python3

from cmk.rulesets.v1 import form_specs, Help, rule_specs, Title
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    Integer,
    LevelDirection,
    SimpleLevels,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, HostAndItemCondition, Topic

def _parameter_form_pgbouncer_pools() -> Dictionary:
    return Dictionary(
        elements={
            "maxwait_warn_crit": DictElement(
                parameter_form=SimpleLevels(
                    title=Title("Maximum wait time for client connections in pgbouncer pools"),
                    form_spec_template=Integer(unit_symbol='s'),
                    level_direction=LevelDirection.UPPER,
                    prefill_fixed_levels=DefaultValue(value=(5, 10))
                ),
            )
        }
    )

rule_spec_pgbouncer_pools = CheckParameters(
    name="pgbouncer_pools",
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_form_pgbouncer_pools,
    title=Title("PgBouncer pool maxwait"),
    condition=HostAndItemCondition(
        item_title=Title("PgBouncer pool maxwait"),
        item_form=String(help_text=Help("You can restrict this rule to certain services of the specified hosts."))
    )
)
