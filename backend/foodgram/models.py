from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import username_validator


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Полe email должно быть заполнено')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user_base(self, email, username, password=None, **extra_fields):
        return self.create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(
        unique=True
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(username_validator,),
    )
    first_name = models.CharField(
        max_length=20
    )
    last_name = models.CharField(
        max_length=20
    )
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    def __str__(self):
        return self.email


class Follow(models.Model):
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed_to',
    )

    def __str__(self):
        return f'{self.subscriber} {self.subscribed_to}'

    class Meta:
        unique_together = (
            'subscriber',
            'subscribed_to'
        )


class Tag(models.Model):
    name = models.CharField(
        max_length=25,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=25,
        unique=True,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=25,
        verbose_name='Единица Измерения'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='foodgram/images/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        max_length=256,
        verbose_name='текст'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(settings.MIN_COOKING_TIME),
            MaxValueValidator(settings.MAX_COOKING_TIME)
        ],
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created_at',)


class IngredientAmountForRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_amount',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
    )
    amount = models.IntegerField(
        validators=[
            MinValueValidator(settings.MIN_AMOUNT),
            MaxValueValidator(settings.MAX_AMOUNT)
        ],
    )


class RecipeSection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    added_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.recipe.name

    class Meta:
        unique_together = (
            'user',
            'recipe'
        )
        ordering = ('-added_at',)


class FavoriteRecipe(RecipeSection):
    class Meta:
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'


class RecipeShoppingCart(RecipeSection):
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
