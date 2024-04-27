from django.contrib import admin

from .models import Follow, Ingredient, Recipe, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    pass
