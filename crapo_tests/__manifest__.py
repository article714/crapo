# @author: C. Guychard
# @copyright: ©2018-2019 Article 714
# @license: AGPL v3

{
    "name": "Crapo: Test Module for workflow management",
    "version": "12.0.1.0.0",
    "category": "Crapo Workflows",
    "author": "Article714",
    "license": "AGPL-3",
    "website": "https://www.article714.org",
    "summary": "Crapo: Test module for workflow management",
    "depends": ["crapo_automaton", "crapo_workflow", "crm"],
    "data": [
        "security/access_model.xml",
        "views/menus_and_views.xml",
        "data/crm_automaton.xml",
        "data/an_object_automaton.xml",
    ],
    "installable": True,
    "images": [],
    "application": True,
}
