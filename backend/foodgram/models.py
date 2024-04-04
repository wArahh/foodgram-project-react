from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


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


class Tag(models.Model):
    name = models.CharField(
        max_length=25,
        verbose_name='Название тега'
    )
    color_code = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=25,
        unique=True,
        verbose_name='Слаг'
    )

    def __str__(self):
        return self.name


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
        verbose_name='Время приготовления'
    )

    def __str__(self):
        return self.name
