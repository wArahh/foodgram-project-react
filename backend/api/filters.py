import django_filters

from foodgram.models import FavoriteRecipe, Recipe, RecipeShoppingCart, Tag


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            in_shopping_cart = RecipeShoppingCart.objects.values_list(
                'recipe_id',
                flat=True
            )
            queryset = queryset.filter(id__in=in_shopping_cart)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        if value:
            favorited = FavoriteRecipe.objects.values_list(
                'recipe_id',
                flat=True
            )
            queryset = queryset.filter(id__in=favorited)
        return queryset

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags',
            'is_in_shopping_cart'
        )
