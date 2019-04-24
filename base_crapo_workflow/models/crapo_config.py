# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class CrapoConfigSettings(models.TransientModel):
    """
    Crapo configuration
    """
    _inherit = 'res.config.settings'
