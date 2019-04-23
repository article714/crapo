# coding: utf-8

"""
©2018-2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields
from odoo.addons.base_crapo_workflow.mixins import crapo_automata_mixins


class CrapoObjectWithMixin(crapo_automata_mixins.ObjectWithStateMixin, models.Model):
    _name = "crapo.test.withmixin"

    myname = fields.Char('My Name')
