import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    # Filter by conversation participants (assuming conversation has participants M2M to User)
    user = django_filters.NumberFilter(field_name="conversation__participants__id", lookup_expr="exact")

    # Filter messages by created_at datetime field
    start_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Message
        fields = ["user", "start_date", "end_date"]
