from django.contrib import admin

from .models import (FavoriteRecipe, Follow, Ingredient,
                     IngredientAmountForRecipe, Recipe, RecipeShoppingCart,
                     Tag, User)


@admin.register(
    User, Tag, Ingredient,
    Recipe, IngredientAmountForRecipe,
    FavoriteRecipe, RecipeShoppingCart, Follow
)
class AllModelsAdmin(admin.ModelAdmin):
    list_display = '__all__'
