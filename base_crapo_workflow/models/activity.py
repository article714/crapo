# -*- coding: utf-8 -*-
# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class WorkflowActivity(models.Model):
    """
    An activity step in a Workflow, i.e. a step where something must me done
    """
    _name = 'crapo.workflow.activity'
    _description = 'Workflow activity'
