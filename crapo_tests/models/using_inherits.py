"""
©2018-2019
License: AGPL-3

@author: C. Guychard (Article 714)

"""


from odoo import models, fields


class CrapoObjectWithInherits(models.Model):
    _name = "crapo.test.withinherits"

    _inherits = {"crapo.automaton.mixin": "wf_object_id"}

    wf_object_id = fields.Many2one(
        string="Workflow Object",
        comodel_name="crapo.automaton.mixin",
        ondelete="cascade",
        required=True,
    )

    myname = fields.Char("My Name")
