from django.contrib import admin
from .models import (
    Tag,
    Ingredient,
    Recipe,
    IngredientAmountForRecipe,
    RecipeSection,
    FavoriteRecipe,
    RecipeShoppingCart,
    Follow
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(IngredientAmountForRecipe)
class IngredientAmountForRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeSection)
class RecipeSectionAdmin(admin.ModelAdmin):
    pass


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(RecipeShoppingCart)
class RecipeShoppingCartAdmin(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
