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

    def wf_trigger(self, name, values={}):
        try:
            mdl_joiner_event = self.env["crapo.workflow.joiner.event"]
        except KeyError:
            return

        mdl_joiner_event.with_context(
            {"notify_joiner_event": True}
        ).with_delay().notify(name, values)

    @skip_if(
        lambda self, record, fields: self.env.context.get(
            "notify_joiner_event"
        )
        or record._module in ("queue", "connector")
    )
    def on_record_create(self, record, fields):

        self.wf_trigger("record_create", {"record": record, "fields": fields})

    @skip_if(
        lambda self, record, fields: self.env.context.get(
            "notify_joiner_event"
        )
        or record._module in ("queue", "connector")
    )
    def on_record_write(self, record, fields):
        self.wf_trigger("record_write", {"record": record, "fields": fields})

    @skip_if(
        lambda self, record: self.env.context.get("notify_joiner_event")
        or record._module in ("queue", "connector")
    )
    def on_record_unlink(self, record):
        self.wf_trigger("record_unlink", {"record": record})
