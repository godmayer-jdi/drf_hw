from rest_framework.pagination import PageNumberPagination

class CoursePagination(PageNumberPagination):
    page_size = 5      # 5 курсов на страницу
    page_size_query_param = 'page_size'
    max_page_size = 20 # Максимум 20

class LessonPagination(PageNumberPagination):
    page_size = 10     # 10 уроков на страницу
    page_size_query_param = 'page_size'
    max_page_size = 50
