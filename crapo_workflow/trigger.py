# ©2018-2019 Article 714
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from decorator import decorate


def _wf_trigger(func, self, *args, **kwargs):
    logging.info("OOOOOOOOOOOOOOOOO %s, %s, %s", self, args, kwargs)

    value = func(self, *args, **kwargs)

    mdl_joiner_event = self.env["crapo.workflow.joiner.event"]
    for rec in self:
        mdl_joiner_event.notify(func.wf_trigger_name, {"record": rec})
    return value


def wf_trigger(name):
    def decorator_wf_trigger(func):
        func.wf_trigger_name = name
        return decorate(func, _wf_trigger)

    return decorator_wf_trigger
