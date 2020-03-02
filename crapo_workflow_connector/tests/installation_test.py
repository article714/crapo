from odoo.tests import common


class IntegrationTestSuite(common.TransactionCase):
    """
    Oversimple test suite to test if module is installed
    """

    def test_module_is_installed(self):
        """
        Testing that current module is installed
        """
        module_model = self.env["ir.module.module"]
        self.assertIsNotNone(module_model)

        found_modules = module_model.search(
            [
                ("name", "=", "crapo_workflow_connector"),
                ("state", "=", "installed"),
            ]
        )

        self.assertEqual(len(found_modules), 1, "Module not installed")
