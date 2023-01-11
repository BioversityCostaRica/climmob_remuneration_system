from climmob.processes.db.validators import projectExists, getTheProjectIdForOwner
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from RemunerationSystem.processes.enumerators import get_supervisor_details
from pyramid.session import check_csrf_token
import logging
from formencode.variabledecode import variable_decode
from ast import literal_eval

log = logging.getLogger(__name__)


class CoordinatorView(object):
    def __init__(self, request):
        self.request = request
        self._ = self.request.translate
        self.checkCrossPost = False
        self.viewResult = {}
        self.returnRawViewResult = False
        self.user_id = None
        self.project_code = None
        self.project_id = None
        self.coordinator_details = None

    def __call__(self):
        self.user_id = self.request.matchdict["user"]
        self.project_code = self.request.matchdict["project"]
        if not projectExists(
            self.user_id, self.user_id, self.project_code, self.request
        ):
            raise HTTPNotFound()
        self.project_id = getTheProjectIdForOwner(
            self.user_id, self.project_code, self.request
        )

        policy_name = self.request.registry.settings["remuneration.system.policy.name"]
        policy = self.get_policy(policy_name)
        login_data = policy.authenticated_userid(self.request)
        if login_data:
            login_data = literal_eval(login_data)
            if login_data["group"] == "coordinatorApp":
                self.coordinator_details = get_supervisor_details(
                    self.request, self.project_id, login_data["login"]
                )
                if self.coordinator_details is None:
                    return HTTPFound(
                        location=self.request.route_url(
                            "coordinator_login",
                            user=self.user_id,
                            project=self.project_code,
                        )
                    )
            else:
                return HTTPFound(
                    location=self.request.route_url(
                        "coordinator_login",
                        user=self.user_id,
                        project=self.project_code,
                    )
                )
        else:
            return HTTPFound(
                location=self.request.route_url(
                    "coordinator_login", user=self.user_id, project=self.project_code
                )
            )
        if (
            self.request.method == "POST"
            or self.request.method == "PUT"
            or self.request.method == "DELETE"
        ):
            safe = check_csrf_token(self.request, raises=False)
            if not safe:
                self.request.session.pop_flash()
                log.error("SECURITY-CSRF error at {} ".format(self.request.url))
                raise HTTPNotFound()
            else:
                if self.checkCrossPost:
                    if self.request.referer != self.request.url:
                        self.request.session.pop_flash()
                        log.error(
                            "SECURITY-CrossPost error. Posting at {} from {} ".format(
                                self.request.url, self.request.referer
                            )
                        )
                        raise HTTPNotFound()

        view_result = self.process_view()

        if not self.returnRawViewResult:
            view_result["coordinator_details"] = self.coordinator_details
            view_result["user_id"] = self.user_id
            view_result["project_code"] = self.project_code
            return view_result
        else:
            return view_result

    def process_view(self):
        raise NotImplementedError()

    def get_post_dict(self):
        dct = variable_decode(self.request.POST)
        return dct

    def get_policy(self, policy_name):
        policies = self.request.policies()
        for policy in policies:
            if policy["name"] == policy_name:
                return policy["policy"]
        return None
