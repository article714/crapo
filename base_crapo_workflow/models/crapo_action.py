# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo import SUPERUSER_ID
from odoo import fields, models, _, exceptions, api
from odoo.addons.queue_job.job import job
from odoo.tools.safe_eval import safe_eval


class CrapoAction(models.Model):
    """
    Crapo Action is a specialisation of Server Actions

    """
    _name = 'crapo.action'
    _inherit = 'ir.actions.server'
    _description = u"A specialization of server actions for Crapol"

    @api.multi
    @job
    def run(self):
        super(CrapoAction, self).run()
