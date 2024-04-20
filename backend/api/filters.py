import django_filters
from django_filters.filters import ModelMultipleChoiceFilter

from foodgram.models import Recipe, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags'
        )
