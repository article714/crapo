# coding: utf-8

"""
©2018-2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields


class CrapoObjectWithInherits(models.Model):
    _name = "crapo.test.withinherits"

    _inherits = {'crapo.business.object': 'wf_object_id'}

    wf_object_id = fields.Many2one(string='Workflow Object',
                                   comodel_name='crapo.business.object', ondelete='cascade', required=True)

    myname = fields.Char('My Name')
