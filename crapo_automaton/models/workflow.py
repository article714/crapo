# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _


class Workflow(models.Model):
    """
    A workflow coordinates and automates a set of workflow activities that
    can apply to a whole set of business objects
    """

    _name = "crapo.workflow"
    _description = """ Specification of a Crapo Workflow, a set of Activities,
    Triggers, Events and WFTransitions"""

    name = fields.Char(help="Workflow's name", required=True)

    activity_ids = fields.One2many("crapo.workflow.activity", "workflow_id")

    transition_ids = fields.One2many(
        "crapo.workflow.transition", "workflow_id"
    )

    joiner_ids = fields.One2many("crapo.workflow.joiner", "workflow_id")

    context_entry_ids = fields.One2many(
        "crapo.workflow.context.entry", "workflow_id"
    )

    def set_context_entry(self, key, value):
        self.ensure_one()
        data = {"key": key, "value": value}
        if isinstance(value, models.Model):
            data["value"] = ",".join(value.ids())
            data["model_id"] = value

        entry = self.context_entry_ids.filtered(lambda rec: rec.key == key)
        if entry:
            entry.write(data)
        else:
            self.write({"context_entry_ids": (0, False, data)})

    def get_context_entry(self, key):
        self.ensure_one()

        entry = self.context_entry_ids.filtered(lambda rec: rec.key == key)

        if not entry:
            raise KeyError(
                _("There is not context entry for key: {}").format(key)
            )

        if entry.model_id:
            return entry.get_recordset()

        return entry.value
