from django_filters.rest_framework import filters, FilterSet
from foodgram.models import FavoriteRecipe, Recipe, RecipeShoppingCart, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_carted__user=self.request.user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(favorited__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_in_shopping_cart',
            'is_favorited',
        )
