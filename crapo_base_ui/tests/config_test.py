# ©2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import common


class ConfigTestSuite(common.TransactionCase):
    """
    Test the configuration of Crapo base module
    """

    def setUp(self):
        super(ConfigTestSuite, self).setUp()
        self.res_config = self.env["res.config.settings"]
        self.ir_config_param = self.env["ir.config_parameter"]

    def test_config(self):
        """
        Test default language get/set/get
        """

        settings_model = self.res_config.create({})
        settings_model.execute()
