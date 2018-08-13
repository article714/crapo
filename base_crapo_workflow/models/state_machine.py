# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class WorkflowStateMachine(models.Model):
    """
    A state-machine (automaton) describes and automates the various transitions between states of a given business object class
    """
    _name = 'crapo.automaton'
