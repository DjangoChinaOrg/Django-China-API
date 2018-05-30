from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.core.paginator import InvalidPage
from django.utils import six


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        """
        Update self.page_size, if page_size_query_param appears in the request url

        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)

        # this is the only difference from the PageNumberPagination's paginate_queryset function
        if not page_size:
            return None
        else:
            self.page_size = page_size

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page_size', self.page_size),
            ('current_page', self.page.number),
            ('last_page', self.page.paginator.num_pages),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('count', self.page.paginator.count),
            ('data', data)
        ]))
