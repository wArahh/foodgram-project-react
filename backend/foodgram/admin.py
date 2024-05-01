from django.contrib import admin

from .models import (FavoriteRecipe, Follow, Ingredient,
                     IngredientAmountForRecipe, Recipe, RecipeShoppingCart,
                     Tag, User)

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(IngredientAmountForRecipe)
admin.site.register(FavoriteRecipe)
admin.site.register(RecipeShoppingCart)
admin.site.register(Follow)
