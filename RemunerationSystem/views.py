import climmob.plugins.utilities as u
from climmob.processes import projectExists, getTheProjectIdForOwner
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from .processes.enumerators import set_enumerator_as_supervisor, get_supervisor_details
from .view_classes import CoordinatorView
from .processes.avatar import Avatar
from pyramid.response import Response
from climmob.config.encdecdata import decodeData
from pyramid.security import remember
from ast import literal_eval


class Gravatar(u.publicView):
    def processView(self):
        try:
            size = int(self.request.params.get("size", 45))
        except ValueError:
            size = 45
        name = self.request.params.get("name", "#")
        avatar = Avatar.generate(size, name, "PNG")
        headers = [("Content-Type", "image/png")]
        return Response(avatar, 200, headers)


class SetEnumeratorAsCoordinator(u.privateView):
    def __init__(self, request):
        u.privateView.__init__(self, request)
        self.checkCrossPost = False

    def processView(self):
        enumerator_id = self.request.matchdict["enumeratorid"]
        active_project_user = self.request.matchdict["user"]
        active_project_cod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, active_project_user, active_project_cod, self.request
        ):
            raise HTTPNotFound()
        else:
            if self.request.method == "POST":
                active_project_id = getTheProjectIdForOwner(
                    active_project_user, active_project_cod, self.request
                )
                set_enumerator_as_supervisor(
                    self.request, active_project_id, enumerator_id
                )
                self.returnRawViewResult = True
                return HTTPFound(
                    location=self.request.route_url(
                        "prjenumerators",
                        user=active_project_user,
                        project=active_project_cod,
                    )
                )
            else:
                raise HTTPNotFound()


def get_policy(request, policy_name):
    policies = request.policies()
    for policy in policies:
        if policy["name"] == policy_name:
            return policy["policy"]
    return None


class CoordinatorLoginView(u.publicView):
    def processView(self):
        active_project_user = self.request.matchdict["user"]
        active_project_cod = self.request.matchdict["project"]
        failed_attempt = False
        next_page = self.request.params.get("next", None)
        if not projectExists(
            active_project_user, active_project_user, active_project_cod, self.request
        ):
            raise HTTPNotFound()

        policy_name = self.request.registry.settings["remuneration.system.policy.name"]
        policy = get_policy(self.request, policy_name)
        login_data = policy.authenticated_userid(self.request)
        project_id = getTheProjectIdForOwner(
            active_project_user, active_project_cod, self.request
        )
        if login_data:
            login_data = literal_eval(login_data)
            if login_data["group"] == "coordinatorApp":
                supervisor_details = get_supervisor_details(
                    self.request, project_id, login_data["login"]
                )
                next_page = self.request.params.get("next") or self.request.route_url(
                    "coordinator_dashboard",
                    user=active_project_user,
                    project=active_project_cod,
                )
                if supervisor_details is not None:
                    return HTTPFound(next_page)
                failed_attempt = False

        if self.request.method == "POST":
            login_data = self.getPostDict()
            if login_data.get("login", "") != "":
                if login_data.get("passwd", "") != "":
                    next_page = self.request.params.get(
                        "next"
                    ) or self.request.route_url(
                        "coordinator_dashboard",
                        user=active_project_user,
                        project=active_project_cod,
                    )
                    supervisor_details = get_supervisor_details(
                        self.request, project_id, login_data.get("login", "")
                    )
                    if supervisor_details is not None:
                        cpass = decodeData(
                            self.request, supervisor_details["enum_password"]
                        )
                        if cpass == bytearray(login_data.get("passwd", "").encode()):
                            login_data = {
                                "login": login_data["login"],
                                "group": "coordinatorApp",
                            }
                            headers = remember(
                                self.request, str(login_data), policies=[policy_name]
                            )
                            return HTTPFound(location=next_page, headers=headers)
                    else:
                        failed_attempt = True
                else:
                    failed_attempt = True
            else:
                failed_attempt = True

        return {"failed_attempt": failed_attempt, "next_page": next_page}


def coordinator_log_out_view(request):
    policy_name = request.registry.settings["remuneration.system.policy.name"]
    policy = get_policy(request, policy_name)
    headers = policy.forget(request)
    active_project_user = request.matchdict["user"]
    active_project_cod = request.matchdict["project"]
    loc = request.route_url(
        "coordinator_login", user=active_project_user, project=active_project_cod
    )
    raise HTTPFound(location=loc, headers=headers)


class CoordinatorDashBoardView(CoordinatorView):
    def process_view(self):
        return {}
