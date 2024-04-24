import django_filters
from django_filters.filters import ModelMultipleChoiceFilter
from django_filters.rest_framework import filters

from foodgram.models import Recipe, Tag, RecipeShoppingCart, FavoriteRecipe


class RecipeFilter(django_filters.FilterSet):
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            shopping_carted = RecipeShoppingCart.objects.select_related('recipe').values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=shopping_carted)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value:
            favorited = FavoriteRecipe.objects.select_related('recipe').values_list('recipe_id', flat=True)
            queryset = queryset.filter(id__in=favorited)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_in_shopping_cart'
        )
