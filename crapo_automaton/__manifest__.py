# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": u"Crapo: Automaton",
    "version": u"12.0.2.0.0",
    "category": u"Crapo Workflows",
    "author": u"Article714",
    "license": u"AGPL-3",
    "website": u"https://www.article714.org",
    "summary": u""" Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["queue_job", "crapo_base"],
    "data": [
        "security/automaton_action.xml",
        "security/crapo_business_object.xml",
        "security/automaton.xml",
        "security/automaton_transition.xml",
        "security/automaton_condition.xml",
        "security/automaton_state.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
