# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkflowContextEntry(models.Model):

    _name = "crapo.workflow.context.entry"

    _sql_constraints = [
        (
            "unique_key_per_context",
            "UNIQUE(workflow_id, key)",
            "One workflow context can't have duplicate key",
        )
    ]

    workflow_id = fields.Many2one("crapo.workflow")

    model_id = fields.Many2one("ir.model")

    key = fields.Char(required=True)

    value = fields.Char(required=True)

    def get_recordset(self):
        """
            Return recordset stored in this context entry
        """
        self.ensure_one()

        if not self.model_id:
            raise UserError(_("This context is not linked to a model"))

        return self.env[self.model_id.model].browse(
            map(int, self.value.split(","))
        )
