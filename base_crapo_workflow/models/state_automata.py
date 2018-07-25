# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class WorkflowStateAutomata(models.Model):
    """
    A state automata describes and automates the various transitions between states of a given business object class
    """
    _name = 'crapo.automata'
