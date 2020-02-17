# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, _, api, exceptions


class CrapoAutomatonState(models.Model):
    """
    A state used in the context of an automaton
    """

    _name = "crapo.automaton.state"
    _description = "State in a workflow, specific to a given model"
    _order = "sequence, name"

    name = fields.Char(help="State's name", required=True)

    description = fields.Text()

    automaton_id = fields.Many2one(
        "crapo.automaton",
        default=lambda self: self._get_default_automaton(),
        required=True,
    )

    sequence = fields.Integer(
        default=1,
        help="Sequence gives the order in which states are displayed",
    )

    default_state = fields.Boolean(
        help="Might be use as default state.", default=False, store=True
    )

    transitions_to_ids = fields.One2many(
        "crapo.automaton.transition",
        "to_state",
        string="Incoming transitions",
    )

    transitions_from_ids = fields.One2many(
        "crapo.automaton.transition",
        "from_state",
        string="Outgoing transitions",
    )

    # computed field to identify start and end states
    is_start_state = fields.Boolean(
        "Start State",
        compute="_compute_is_start_state",
        store=True,
        index=True,
    )

    is_end_state = fields.Boolean(
        "End State", compute="_compute_is_end_state", store=True, index=True
    )

    is_creation_state = fields.Boolean(
        help="""Indicate if this state is a possible state to create a record.
        This value is not take in account if it's a start state""",
        default=False,
    )

    readonly_fields = fields.Char(
        help="List of model's fields name separated by comma"
    )

    @api.depends("transitions_to_ids", "automaton_id")
    def _compute_is_start_state(self):
        for record in self:
            if (
                len(record.transitions_to_ids) == 0
                or record.transitions_to_ids is False
            ):
                record.is_start_state = True
            else:
                record.is_start_state = False

    @api.depends("transitions_from_ids", "automaton_id")
    def _compute_is_end_state(self):
        for record in self:
            if (
                len(record.transitions_to_ids) == 0
                or record.transitions_to_ids is False
            ):
                record.is_end_state = True
            else:
                record.is_end_state = False

    def _do_search_default_automaton(self):
        return False

    @api.model
    def _get_default_automaton(self):
        default_value = 0
        if "current_automaton" in self.env.context:
            try:
                default_value = int(self.env.context.get("current_automaton"))
            except Exception:
                default_value = 0
        else:
            return self._do_search_default_automaton()

        return self.env["crapo.automaton"].browse(default_value)

    @api.multi
    def write(self, values):
        """
        Override default method to check if there is a valid default_state
        """
        if "default_state" in values:
            if values["default_state"]:
                if len(self) > 1:
                    raise exceptions.ValidationError(
                        _(u"There should only one default state per model")
                    )
                else:
                    found = self.search(
                        [
                            ("default_state", "=", True),
                            ("automaton_id", "=", self.automaton_id.id),
                            ("id", "!=", self.id),
                        ]
                    )
                    for s in found:
                        s.write({"default_state": False})

        return super(CrapoAutomatonState, self).write(values)
