# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": "Crapo: Automaton",
    "version": "12.0.2.0.0",
    "category": "Crapo Workflows",
    "author": "Article714",
    "license": "AGPL-3",
    "website": "https://www.article714.org",
    "summary": """ Fexible tool to manage automata & workflows
     for your odoo objects""",
    "depends": ["queue_job", "crapo_base"],
    "data": [
        "security/automaton_action.xml",
        "security/crapo_automaton_mixin.xml",
        "security/automaton.xml",
        "security/automaton_transition.xml",
        "security/automaton_condition.xml",
        "security/automaton_state.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
