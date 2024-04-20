from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class PageLimitPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = settings.PAGE_LIMIT_PAGINATION_PAGE_SIZE
