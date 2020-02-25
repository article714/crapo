# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _, exceptions


class Automaton(models.Model):
    """
    A state-machine (automaton) describes and automates the various
    transitions between states of a given business object class

    There can be a single state machine per Odoo Model Object

    """

    _name = "crapo.automaton"
    _description = "An automaton is a state machine for a given Odoo Model"
    _order = "name, id"

    _record_name = "name"

    _sql_constraints = [
        (
            "unique_per_model_id",
            "unique(model_id)",
            "Choose another value - automaton has to be unique per Model !",
        )
    ]

    name = fields.Char(help="Automaton's name", required=True, translate=True)

    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        help="""Model for which this automaton is relevant""",
        required=True,
    )

    transition_ids = fields.One2many(
        "crapo.automaton.transition", "automaton_id",
    )

    state_ids = fields.One2many("crapo.automaton.state", "automaton_id",)

    default_state_id = fields.Many2one(
        "crapo.automaton.state", compute="_compute_default_state"
    )

    sync_state_field = fields.Char()

    # =========================
    # Compute
    # =========================

    @api.depends("state_ids")
    def _compute_default_state(self):
        for rec in self:
            rec.default_state_id = rec.state_ids.filtered(
                lambda state: state.default_state
            )

    # =========================
    # Create
    # =========================

    @api.model
    def create(self, values):
        """
            Write automaton_id on automaton.model_id existing records
        """
        rec = super(Automaton, self).create(values)

        self.env[rec.model_id.model].search([]).write(
            {"crapo_automaton_id": rec.id}
        )

        return rec
