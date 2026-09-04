from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1500)
    image_src = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    post_date = models.DateTimeField(auto_now_add=True)
    wishlisted_by = models.ManyToManyField(User, related_name="wishlisted_by")
    is_active = models.BooleanField(default=True)


class Comment(models.Model):
    content = models.CharField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    post_date = models.DateTimeField(auto_now_add=True)


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer")

