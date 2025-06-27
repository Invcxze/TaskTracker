from elasticsearch.dsl import Q
from ..search_document import UserDocument


def search_users(search=None, is_active=None, is_staff=None, is_superuser=None, permission_code=None):
    q = Q("match_all")

    if search:
        q &= Q("multi_match", query=search, fields=["email^2", "fio"], fuzziness="auto")
    if is_active is not None:
        q &= Q("term", is_active=is_active.lower() == "true")
    if is_staff is not None:
        q &= Q("term", is_staff=is_staff.lower() == "true")
    if is_superuser is not None:
        q &= Q("term", is_superuser=is_superuser.lower() == "true")
    if permission_code:
        q &= Q("nested", path="permissions", query=Q("term", permissions__code=permission_code))

    return UserDocument.search().query(q)
