from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.id} {self.title}"

class New_listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    s_bid = models.DecimalField(max_digits=8, decimal_places=2)
    img = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")

    def __str__(self):
        return f"{self.title} {self.s_bid}"