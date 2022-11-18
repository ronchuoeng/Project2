from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    title = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.title}"


class Bidding(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.bidder}: ${self.bid_price}"


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=1000)
    s_bid = models.DecimalField(max_digits=8, decimal_places=2)
    c_off = models.ForeignKey(Bidding, on_delete=models.SET_NULL, blank=True, null=True, related_name="bidprices")
    img = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="categories")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sellers")
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title}"