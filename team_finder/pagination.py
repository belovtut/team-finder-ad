from django.core.paginator import Paginator

DEFAULT_PAGE_SIZE = 12
DEFAULT_PAGE_NUMBER = 1


def paginate_queryset(queryset, page_number, per_page=DEFAULT_PAGE_SIZE):
    paginator = Paginator(queryset, per_page)
    page = page_number or DEFAULT_PAGE_NUMBER
    return paginator.get_page(page)
