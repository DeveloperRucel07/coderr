from  django_filters import FilterSet, NumberFilter
from coderr_app.models import Offer, Review

class OfferFilter(FilterSet):
    creator_id = NumberFilter(field_name='user__id')
    min_price = NumberFilter(method='filter_min_price')
    max_delivery_time = NumberFilter(method='filter_max_delivery_time')

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']

    def filter_min_price(self, queryset, name, value):
        """
        Filter offers by minimum price.

        Args:
            queryset (QuerySet): The queryset to filter.
            name (str): The name of the filter field.
            value (float): The minimum price value.

        Returns:
            QuerySet: The filtered queryset with distinct results.
        """
        return queryset.filter(details__price__gte=value).distinct()

    def filter_max_delivery_time(self, queryset, name, value):
        """
        Filter offers by maximum delivery time.

        Args:
            queryset (QuerySet): The queryset to filter.
            name (str): The name of the filter field.
            value (int): The maximum delivery time in days.

        Returns:
            QuerySet: The filtered queryset with distinct results.
        """
        return queryset.filter(details__delivery_time_in_days__lte=value).distinct()

class ReviewFilter(FilterSet):
    business_user_id = NumberFilter(field_name="business_user__id")
    reviewer_id = NumberFilter(field_name="reviewer__id")

    class Meta:
        model = Review
        fields = ["business_user_id", "reviewer_id"]
