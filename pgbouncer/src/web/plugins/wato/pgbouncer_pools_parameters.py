from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Age,
    Dictionary,
    TextInput,
    Tuple,
)
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _item_valuespec_pgbouncer_pools():
    return TextInput(
        title = "PgBouncer pool name",
        help = "You can restrict this rule to certain services of the specified hosts.",
    )

def _parameter_valuespec_pgbouncer_pools():
    return Dictionary(
        elements = [
            ("maxwait_warn_crit",
                Tuple(
                    title = _("Maximum wait time for client connections in pgbouncer pools"),
                    elements = [
                        Age(title = _("Warning"), display = ["seconds"], default_value = 5),
                        Age(title = _("Critical"), display = ["seconds"], default_value = 10),
                    ],
                )
            ),
        ],
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name = "pgbouncer_pools",
        group = RulespecGroupCheckParametersApplications,
        match_type = "dict",
        item_spec = _item_valuespec_pgbouncer_pools,
        parameter_valuespec = _parameter_valuespec_pgbouncer_pools,
        title = lambda: _("PgBouncer pool maxwait"),
    )
)
