"""
©2019-2020
License: AGPL-3

@author: D. Couppé (Article 714)

"""
from odoo.addons.component.core import Component
from odoo.addons.component_event.components.event import skip_if


class WorkflowListener(Component):
    _name = "crapo.workflow.listener"
    _inherit = "base.event.listener"

    def wf_event(self, name, values={}):
        try:
            mdl_event = self.env["crapo.workflow.event"]
        except KeyError:
            return

        mdl_event.with_context({"notify_event": True}).with_delay().notify(
            name, values
        )

    @skip_if(
        lambda self, record, fields: self.env.context.get("notify_event")
        or record._module in ("queue", "connector")
    )
    def on_record_create(self, record, fields):

        self.wf_event("record_create", {"record": record, "fields": fields})

    @skip_if(
        lambda self, record, fields: self.env.context.get("notify_event")
        or record._module in ("queue", "connector")
    )
    def on_record_write(self, record, fields):
        self.wf_event("record_write", {"record": record, "fields": fields})

    @skip_if(
        lambda self, record: self.env.context.get("notify_event")
        or record._module in ("queue", "connector")
    )
    def on_record_unlink(self, record):
        self.wf_event("record_unlink", {"record": record})
