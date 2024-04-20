from django.contrib import admin

from .models import (
    User,
    Tag,
    Ingredient,
    Recipe,
    FavoriteRecipe,
    RecipeShoppingCart
)

admin.site.register(User)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(Recipe)
admin.site.register(FavoriteRecipe)
admin.site.register(RecipeShoppingCart)
