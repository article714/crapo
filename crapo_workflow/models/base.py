# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Base(models.AbstractModel):
    """The base model, which is implicitly inherited by all models.

    A new :meth:`~wf_trigger` method is added on all Odoo Models, allowing to
    notify an event to crapo_warkflow
    """

    _inherit = "base"

    def wf_trigger(self, name, values={}):
        mdl_joiner_event = self.env["crapo.workflow.joiner.event"]
        for rec in self:
            values["record"] = rec
            mdl_joiner_event.with_delay().notify(name, values)
