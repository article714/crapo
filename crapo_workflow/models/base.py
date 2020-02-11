# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class Base(models.AbstractModel):
    """
        The base model, which is implicitly inherited by all models.

        A new :meth:`wf_event` method is added on all Odoo Models, allowing to
        notify an event to crapo_warkflow
    """

    _inherit = "base"

    def wf_event(self, name, values=None):
        """
            Notify event to workflow broker
        """
        broker = self.env["crapo.workflow.broker"]
        for rec in self:
            if values is None:
                values = {}
            values["record"] = rec
            broker.with_delay().notify(name, values)
