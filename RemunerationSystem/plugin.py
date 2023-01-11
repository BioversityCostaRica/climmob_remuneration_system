import climmob.plugins as plugins
import climmob.plugins.utilities as u
import sys
import os
from .views import (
    SetEnumeratorAsCoordinator,
    CoordinatorLoginView,
    CoordinatorDashBoardView,
    coordinator_log_out_view,
    Gravatar,
)
from .processes.enumerators import project_has_coordinator


class RemunerationSystem(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfig)
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.ISchema)
    plugins.implements(plugins.IProject)
    plugins.implements(plugins.ICloneProject)
    plugins.implements(plugins.IProjectEnumerator)
    plugins.implements(plugins.IRoutes)
    plugins.implements(plugins.IDashBoard)
    plugins.implements(plugins.IAuthenticationPolicy)

    def before_mapping(self, config):
        # We don't add any routes before the host application
        return []

    def after_mapping(self, config):
        # We add here a new route /json that returns a JSON
        custom_map = [
            u.addRoute(
                "set_enumerator_as_coordinator",
                "/user/{user}/project/{project}/enumerator/{enumeratorid}/set_as_coordinator",
                SetEnumeratorAsCoordinator,
                None,
            ),
            u.addRoute(
                "coordinator_login",
                "/user/{user}/project/{project}/coordinator/login",
                CoordinatorLoginView,
                "coordinator/login.jinja2",
            ),
            u.addRoute(
                "coordinator_logout",
                "/user/{user}/project/{project}/coordinator/logout",
                coordinator_log_out_view,
                None,
            ),
            u.addRoute(
                "coordinator_dashboard",
                "/user/{user}/project/{project}/coordinator/dashboard",
                CoordinatorDashBoardView,
                "coordinator/dashboard.jinja2",
            ),
            u.addRoute(
                "coordinator_gravatar",
                "/coordinator_gravatar",
                Gravatar,
                None,
            ),
        ]
        return custom_map

    # IConfig

    def update_config(self, config):
        # We add here the templates of the plugin to the config
        u.addTemplatesDirectory(config, "templates")
        u.addStaticView(config, "RemunerationSystem", "static")

    # ITranslation

    def get_translation_directory(self):
        module = sys.modules["RemunerationSystem"]
        return os.path.join(os.path.dirname(module.__file__), "locale")

    def get_translation_domain(self):
        return "RemunerationSystem"

    # ISchema
    def update_schema(self, config):
        return [
            u.addFieldToProjectEnumertorSchema("is_supervisor", "Is supervisor"),
            u.addFieldToProjectSchema(
                "use_remuneration_system", "Use remuneration system"
            ),
        ]

    # IProject
    def before_adding_project(self, request, user_name, project_data):
        if "use_remuneration_system" in project_data.keys():
            project_data["use_remuneration_system"] = "on"
        else:
            project_data["use_remuneration_system"] = "off"
        return True, ""

    def after_adding_project(self, request, user_name, project_data):
        pass

    def before_updating_project(self, request, user_name, project_id, project_data):
        if "use_remuneration_system" in project_data.keys():
            project_data["use_remuneration_system"] = "on"
        else:
            project_data["use_remuneration_system"] = "off"
        return True, ""

    def after_updating_project(self, request, user_name, project_id, project_data):
        pass

    def before_deleting_project(self, request, user_name, project_id):
        return True, ""

    def after_deleting_project(self, request, user_name, project_id):
        pass

    def before_returning_project_context(self, request, context):
        return context

    # ICloneProject
    def before_cloning_enumerator(self, request, enumerator_data, clone_data):
        if "is_supervisor" in enumerator_data.keys():
            clone_data["is_supervisor"] = enumerator_data["is_supervisor"]
        else:
            clone_data["is_supervisor"] = 0
        return True

    def after_cloning_enumerator(self, request, enumerator_data, clone_data):
        pass

    # IProject Enumerator
    def before_adding_enumerator_to_project(self, request, project_enumerator_data):
        project_enumerator_data["is_supervisor"] = 0
        return True, ""

    def after_adding_enumerator_to_project(self, request, project_enumerator_data):
        pass

    # IDashBoard
    def before_returning_dashboard_context(self, request, context):
        if context["hasActiveProject"]:
            context["project_has_coordinator"] = project_has_coordinator(
                request, context["activeProject"]["project_id"]
            )
            if not context["project_has_coordinator"]:
                if context["pcompleted"] >= 40:
                    context["pcompleted"] = context["pcompleted"] - 20
            return context
        else:
            return context

    # IAuthenticationPolicy
    def get_new_authentication_policy_details(self, settings):
        print("Plugin get_new_authentication_policy_details")
        return [
            {
                "secret": settings["remuneration.system.secret"],
                "cookie_timeout": settings.get(
                    "remuneration.system.cookie.timeout", 7200
                ),
                "cookie_name": settings["remuneration.system.cookie.name"],
                "policy_name": settings["remuneration.system.policy.name"],
            }
        ]
