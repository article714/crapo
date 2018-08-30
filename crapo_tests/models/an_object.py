# -*- coding: utf-8 -*-
# ©2018 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AnObject(models.Model):
    _name = 'crapo.test.object'
    _inherit = ['crapo.business.object']
    _description = u"A sample business Object"

    name = fields.Char(string="A Name")

    some_value = fields.Boolean('Some Value')

    some_objects = fields.One2many(comodel_name='crapo.test.another', inverse_name='to_object')
