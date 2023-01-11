from climmob.models.schema import mapToSchema, mapFromSchema
from climmob.models import PrjEnumerator, Enumerator


def set_enumerator_as_supervisor(request, project_id, enumerator_id):
    data = {"is_supervisor": 0}
    mapped_data = mapToSchema(PrjEnumerator, data)
    request.dbsession.query(PrjEnumerator).filter(
        PrjEnumerator.project_id == project_id
    ).update(mapped_data)

    data = {"is_supervisor": 1}
    mapped_data = mapToSchema(PrjEnumerator, data)
    request.dbsession.query(PrjEnumerator).filter(
        PrjEnumerator.project_id == project_id
    ).filter(PrjEnumerator.enum_id == enumerator_id).update(mapped_data)
    return True, ""


def project_has_coordinator(request, project_id):
    res = (
        request.dbsession.query(PrjEnumerator)
        .filter(PrjEnumerator.project_id == project_id)
        .all()
    )
    enumerators = mapFromSchema(res)
    if enumerators:
        for an_enumerator in enumerators:
            if an_enumerator["is_supervisor"] == 1:
                return True
        return False
    else:
        return False


def get_supervisor_details(request, project_id, enumerator_id):
    res = (
        request.dbsession.query(Enumerator, PrjEnumerator)
        .filter(Enumerator.user_name == PrjEnumerator.enum_user)
        .filter(Enumerator.enum_id == PrjEnumerator.enum_id)
        .filter(PrjEnumerator.project_id == project_id)
        .filter(PrjEnumerator.enum_id == enumerator_id)
        .filter(Enumerator.enum_active == 1)
        .first()
    )
    details = mapFromSchema(res)
    if details:
        if details["is_supervisor"] == 1:
            return details
    return None
