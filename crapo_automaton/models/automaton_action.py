# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, api, fields
from odoo.addons.queue_job.job import job


class IrActionsServer(models.Model):
    _inherit = "ir.actions.server"

    usage = fields.Selection(
        selection_add=[("crapo_automaton_action", "Crapo automaton action")]
    )


class CrapoAutomatonAction(models.Model):
    """
    Crapo Action is a specialisation of Server Actions in order to be
    able to use them in actions/activities and run them asynchronously
    """

    _name = "crapo.automaton.action"
    _inherits = {"ir.actions.server": "action_server_id"}
    _description = "A specialization of server actions for Crapo Automata"

    action_server_id = fields.Many2one(
        "ir.actions.server", required=True, ondelete="restrict"
    )

    def run(self):
        self.action_server_id.run()

    @api.multi
    @job
    def run_async(self):
        self.action_server_id.run()

    # ==============================
    # Write/Create
    # ==============================

    @api.model
    def create(self, values):
        values["usage"] = "crapo_automaton_action"
        return super(CrapoAutomatonAction, self).create(values)
