# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkflowContext(models.Model):

    _name = "crapo.workflow.context"

    workflow_id = fields.Many2one("crapo.workflow", ondelete="cascade")

    context_entry_ids = fields.One2many(
        "crapo.workflow.context.entry", "wf_context_id"
    )

    context_event_ids = fields.One2many(
        "crapo.workflow.context.event", "wf_context_id"
    )

    def set_context_entry(self, key, value):
        data = {"key": key, "value": value}
        if isinstance(value, models.Model):
            data["value"] = ",".join(map(str, value.ids))
            data["model_id"] = self.env["ir.model"]._get_id(value._name)

        entry = self.context_entry_ids.filtered(lambda rec: rec.key == key)
        if entry:
            entry.write(data)
        else:
            self.write({"context_entry_ids": [(0, False, data)]})

    def get_context_entry(self, key, convert=True):
        entry = self.context_entry_ids.filtered(lambda rec: rec.key == key)

        if not entry:
            raise KeyError(
                _("There is not context entry for key: {}").format(key)
            )

        if convert and entry.model_id:
            return entry.get_recordset()

        return entry.value


class WorkflowContextEntry(models.Model):

    _name = "crapo.workflow.context.entry"

    _sql_constraints = [
        (
            "unique_key_per_context",
            "UNIQUE(wf_context_id, key)",
            "One workflow context can't have duplicate key",
        )
    ]

    wf_context_id = fields.Many2one(
        "crapo.workflow.context", ondelete="cascade"
    )

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


class WorkflowContextEvent(models.Model):

    _name = "crapo.workflow.context.event"

    wf_context_id = fields.Many2one(
        "crapo.workflow.context", required=True, ondelete="cascade"
    )

    done = fields.Boolean(default=False, required=True)

    event_id = fields.Many2one("crapo.workflow.event", required=True)

    trigger_id = fields.Many2one(
        "crapo.workflow.trigger", related="event_id.trigger_id",
    )

    record_id = fields.Integer()

    @api.model
    def create(self, values):
        rec = super(WorkflowContextEvent, self).create(values)

        if rec.event_id.record_id_context_key:
            rec.record_id = int(
                rec.wf_context_id.get_context_entry(
                    rec.event_id.record_id_context_key, convert=False
                )
            )
        elif rec.event_id.event_type == "activity_ended":
            rec.record_id == rec.event_id.activity_id.id
        return rec

    @api.multi
    def write(self, values):

        res = super(WorkflowContextEvent, self).write(values)

        if values.get("done"):
            for wf_context_id in self.mapped("wf_context_id"):
                self.mapped("trigger_id").with_delay().check_and_run(
                    wf_context_id=wf_context_id
                )

        return res
