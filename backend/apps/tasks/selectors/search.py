from django.db.models import Case, When
from elasticsearch.dsl import Q, Search


def task_search(queryset, search_query, filters):
    s = Search(index="tasks").extra(size=1000)

    if search_query:
        s = s.query(
            Q(
                "multi_match",
                query=search_query,
                fields=["title^3", "description^2", "comments.content", "labels.name", "assignee.fio", "creator.fio"],
                fuzziness="AUTO",
            )
        )

    if "workspace" in filters:
        s = s.filter("term", workspace__id=filters["workspace"])

    if "status" in filters:
        s = s.filter("term", status__id=filters["status"])

    if "priority" in filters:
        s = s.filter("terms", priority=filters["priority"])

    if "assignee" in filters:
        s = s.filter("term", assignee__id=filters["assignee"])

    if "creator" in filters:
        s = s.filter("term", creator__id=filters["creator"])

    if "is_closed" in filters:
        s = s.filter("term", is_closed=filters["is_closed"])

    if "labels" in filters:
        s = s.filter("terms", labels__id=filters["labels"])

    if "due_date_before" in filters:
        s = s.filter("range", due_date={"lte": filters["due_date_before"]})

    if "due_date_after" in filters:
        s = s.filter("range", due_date={"gte": filters["due_date_after"]})

    response = s.execute()

    task_ids = [hit.id for hit in response]

    preserved_order = Case(*[When(id=id, then=pos) for pos, id in enumerate(task_ids)])
    return queryset.filter(id__in=task_ids).order_by(preserved_order)
