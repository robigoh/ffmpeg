from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price_per_month = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True)
    ad_variations_per_month = models.IntegerField(default=0)
    stripe_price_id = models.CharField(max_length=100, unique=True, default="default_price_id")  # Added default

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Bind to user
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)  # User's Plan
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('canceled', 'Canceled')], default='active')  # Status
    unused_credits = models.IntegerField(default=0)  # Remaining ad variations
    stripe_subscription_id = models.CharField(max_length=100, unique=True, default="default_subscription_id")  # Stripe Subscription ID

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"