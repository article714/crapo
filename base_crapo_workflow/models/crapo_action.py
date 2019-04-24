# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, api
from odoo.addons.queue_job.job import job


class CrapoAction(models.Model):
    """
    Crapo Action is a specialisation of Server Actions in order to be
    able to use them in actions/activities and run them asynchronously
    """
    _name = 'crapo.action'
    _inherit = 'ir.actions.server'
    _description = u"A specialization of server actions for Crapol"

    @api.model
    def _get_states(self):

        return [('code', 'Execute Python Code'),
                ('object_create', 'Create or Copy a new Record'),
                ('object_write', 'Write on a Record'),
                ('multi', 'Execute several actions')]

    @api.multi
    @job
    def run_async(self, context={}): # pylint: disable=dangerous-default-value
        self.with_context(context).run()
