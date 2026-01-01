from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User

class Offer(models.Model):
    user = models.ForeignKey(User, related_name='offers', on_delete=models.CASCADE, limit_choices_to={'profile__type': 'business'})
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.pk:
            detail_count = self.details.count()
            if detail_count != 3:
                raise ValidationError(
                    'An offer must contain exactly 3 details (basic, standard, premium).'
                )

    def __str__(self):
        return self.title
    
class OfferDetail(models.Model):

    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    offer = models.ForeignKey(Offer, related_name='details', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    features = models.JSONField(default=list)

    class Meta:
        unique_together = ('offer', 'offer_type')

    def __str__(self):
        return f'{self.offer.title} - {self.offer_type}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    offer_detail = models.ForeignKey(OfferDetail, related_name='orders', on_delete=models.PROTECT)
    customer_user = models.ForeignKey(User, related_name='customer_orders', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='business_orders', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField()
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Order #{self.id} - {self.title}'
    

class Review(models.Model):
    reviewer  = models.ForeignKey(User, related_name='reviewer', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='review_for', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Review {self.rating}/5 by {self.reviewer} for {self.business_user}'