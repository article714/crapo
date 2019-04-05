# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class WorkflowWorkflow(models.Model):
    """
    A workflow coordinates and automates a set of workflow activities that can apply to a whole set of business objects
    """
    _name = 'crapo.workflow'
    _description = 'Specification of a Crapo Workflow, a set of Activities, Triggers, Events and WFTransitions'
