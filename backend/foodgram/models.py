from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
    )
    measurement_unit = models.CharField(
        max_length=25,
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=25,
    )
    color_code = models.CharField(
        max_length=7,
    )
    slug = models.SlugField(
        max_length=25,
        unique=True,
    )


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=200,
    )
    image = models.ImageField(
        upload_to='foodgram/images/',
    )
    text = models.TextField(
        max_length=256
    )
    ingredients = models.ManyToManyField(
        'Ingredient', related_name='recipes'
    )
    tags = models.ManyToManyField(
        'Tag', related_name='recipes'
    )
    cooking_time = models.IntegerField(
    )
