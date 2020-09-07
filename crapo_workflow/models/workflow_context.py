"""
see README for details
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class WorkflowContext(models.Model):
    """
        Workflow context is an instance of a worklow a time
    """

    _name = "crapo.workflow.context"

    workflow_id = fields.Many2one("crapo.workflow", ondelete="cascade")

    context_entry_ids = fields.One2many(
        "crapo.workflow.context.entry", "wf_context_id"
    )

    context_event_ids = fields.One2many(
        "crapo.workflow.context.event", "wf_context_id"
    )

    def set_context_entry(self, key, value):
        """
            Save value to context associate with key
        """
        data = {"key": key, "value": value}
        # Id it's a record we save the id in the value and the
        # model where the record come from
        if isinstance(value, models.Model):
            data["value"] = ",".join(map(str, value.ids))
            data["model_id"] = self.env[  # pylint: disable=protected-access
                "ir.model"
            ]._get_id(
                value._name  # pylint: disable=protected-access
            )

        # Update if exists
        entry = self.context_entry_ids.filtered(lambda rec: rec.key == key)
        if entry:
            entry.write(data)
        # Else create
        else:
            self.write({"context_entry_ids": [(0, False, data)]})

    def get_context_entry(self, key, convert=True):
        """
            Read key from context and return value. If key refer to a
            record, we return the record directly if convert is True
        """
        entry = self.context_entry_ids.filtered(lambda rec: rec.key == key)

        if not entry:
            raise KeyError(
                _("There is not context entry for key: {}").format(key)
            )

        if convert and entry.model_id:
            return entry.get_recordset()

        return entry.value


class WorkflowContextEntry(models.Model):
    """
        Model key/value to save nearly everything
    """

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

    @api.depends("key", "model_id", "value")
    def _compute_display_name(self):
        for rec in self:
            if rec.model_id:
                value = rec.get_recordset()
            else:
                value = rec.value
            rec.display_name = "{}: {}".format(rec.key, value)


class WorkflowContextEvent(models.Model):
    """
    A class to store values/env var relative to a specific event
    e.g. contains the record_id of the record concerned by the event
    """

    _name = "crapo.workflow.context.event"

    wf_context_id = fields.Many2one(
        "crapo.workflow.context", required=True, ondelete="cascade"
    )

    done = fields.Boolean(default=False, required=True)

    event_id = fields.Many2one("crapo.workflow.event", required=True)

    # Shortcut for convenience
    trigger_id = fields.Many2one(
        "crapo.workflow.trigger", related="event_id.trigger_id",
    )

    record_id = fields.Integer()

    @api.depends("trigger_id", "event_id", "done")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "{}.{}: {}".format(
                rec.trigger_id.display_name,
                rec.event_id.display_name,
                rec.done,
            )

    def get_record_id(self):
        """
            Return record_id if set, if not set try to get it from
            context and set it.
        """
        if not self.record_id:
            try:
                self.record_id = int(
                    self.wf_context_id.get_context_entry(
                        self.event_id.record_id_context_key, convert=False
                    )
                )
            except KeyError:  # pylint: disable=except-pass
                # If we have a key error it means that record_id_context_key
                # doesn't exists wet in context
                pass
        return self.record_id

    # ==================
    # Write / Create
    # ==================

    @api.model
    def create(self, values):
        """
        Override default create to set record_id on event creation
        """
        rec = super(WorkflowContextEvent, self).create(values)

        if rec.event_id.record_id_context_key:
            rec.get_record_id()
        elif rec.event_id.event_type == "activity_ended":
            rec.record_id = rec.event_id.activity_id.id
        return rec

    @api.multi
    def write(self, values):
        """
        Override default write to add relative context for event
        """

        res = super(WorkflowContextEvent, self).write(values)

        if values.get("done"):
            for wf_context_id in self.mapped("wf_context_id"):
                filtered_rec = self.filtered(
                    lambda rec: rec.wf_context_id
                    == wf_context_id  # pylint: disable=cell-var-from-loop
                )
                filtered_rec.mapped("trigger_id").with_delay().check_and_run(
                    wf_context_id=wf_context_id
                )

        return res
