from rest_framework.pagination import PageNumberPagination


class LMSPagination(PageNumberPagination):
    """Один пагинатор на все"""

    page_size = 10  # 10 элементов (5-15 по ТЗ)
    page_size_query_param = "page_size"
    max_page_size = 15  # Максимум 15


"""class CoursePagination(PageNumberPagination):
    page_size = 5      # 5 курсов на страницу
    page_size_query_param = 'page_size'
    max_page_size = 20 # Максимум 20

class LessonPagination(PageNumberPagination):
    page_size = 10     # 10 уроков на страницу
    page_size_query_param = 'page_size'
    max_page_size = 50"""
