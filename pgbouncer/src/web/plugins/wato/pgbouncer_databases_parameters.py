from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    Percentage,
    TextInput,
    Tuple,
)
from cmk.gui.plugins.wato.utils import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _item_valuespec_pgbouncer_databases():
    return TextInput(
        title = "PgBouncer database name",
        help = "You can restrict this rule to certain services of the specified hosts.",
    )

def _parameter_valuespec_pgbouncer_databases():
    return Dictionary(
        elements = [
            ("connection_usage_warn_crit",
                Tuple(
                    title = _("Connection usage threshold of pgbouncer database"),
                    elements = [
                        Percentage(title = _("Warning"), default_value = 90.0),
                        Percentage(title = _("Critical"), default_value = 95.0),
                    ],
                )
            ),
        ],
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name = "pgbouncer_databases",
        group = RulespecGroupCheckParametersApplications,
        match_type = "dict",
        item_spec = _item_valuespec_pgbouncer_databases,
        parameter_valuespec = _parameter_valuespec_pgbouncer_databases,
        title = lambda: _("PgBouncer database connection usage"),
    )
)
