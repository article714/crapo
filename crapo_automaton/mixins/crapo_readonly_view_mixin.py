"""
See README for details
"""

from lxml import etree
from lxml.builder import E

from odoo.tools.safe_eval import safe_eval
from odoo.osv import expression


class ReadonlyViewMixin():
    """
        Mixin class that can be used to set a whole view readonly with domains
    """

    _readonly_domain = []
    _readonly_fields_to_add = []

    def _fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """
            Override to add crapo_readonly_fields to arch and attrs readonly
            on fields that could be editable
        """
        result = super(ReadonlyViewMixin, self)._fields_view_get(
            view_id, view_type, toolbar, submenu
        )
        if view_type in ("form", "tree"):
            readonly_fields = [
                name for name, field in self._fields.items() if field.readonly
            ]

            node = etree.fromstring(result["arch"])
            for field in self._readonly_fields_to_add:
                node.append(E.field(name=field, invisible="1"))

            if not isinstance(self._readonly_domain, (list, tuple)):
                lst_domain = [self._readonly_domain]
            else:
                lst_domain = self._readonly_domain

            self._process_field(node, readonly_fields, lst_domain)
            result["arch"] = etree.tostring(node)
        return result

    def _process_field(self, node, readonly_fields, lst_domain):
        """
            Add readnoly attrs if needed
        """
        if node.get("readonly_global_domain"):
            lst_domain = lst_domain + [node.get("readonly_global_domain")]

        if node.tag == "field":
            field_name = node.get("name")

            attrs = safe_eval(node.get("attrs", "{}"))
            readonly = attrs.get("readonly") or node.get("readonly")
            if isinstance(readonly, str):
                readonly = safe_eval(node.get("readonly", "{}"))

            # Deal with none domain value, if field is explicitly in
            # readonly we skip
            if not isinstance(readonly, (list, tuple)) and readonly:
                return
            # If there is no domain define and fields is already in readonly
            # we skip too

            if readonly is None and field_name in readonly_fields:
                return

            _readonly_domain = expression.OR(
                [
                    safe_eval(domain, {"field_name": field_name})
                    for domain in lst_domain
                ]
            )
            if readonly:
                _readonly_domain = expression.OR([readonly, _readonly_domain])

            attrs["readonly"] = _readonly_domain
            node.set("attrs", str(attrs))

        else:
            for child_node in node:
                self._process_field(child_node, readonly_fields, lst_domain)
