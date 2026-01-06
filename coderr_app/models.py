from django.db import models
from django.forms import ValidationError
from django.contrib.auth.models import User

class Offer(models.Model):
    """
    Represents an offer created by a business user, containing details for different tiers.

    Attributes:
        user (ForeignKey): The business user who created the offer.
        title (CharField): The title of the offer.
        image (ImageField): An optional image for the offer.
        description (TextField): The description of the offer.
        created_at (DateTimeField): The date and time the offer was created.
        updated_at (DateTimeField): The date and time the offer was last updated.
    """

    user = models.ForeignKey(User, related_name='offers', on_delete=models.CASCADE, limit_choices_to={'profile__type': 'business'})
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offers/', null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validates that the offer has exactly three details.

        Raises:
            ValidationError: If the offer does not have exactly 3 details.
        """
        if self.pk:
            detail_count = self.details.count()
            if detail_count != 3:
                raise ValidationError(
                    'An offer must contain exactly 3 details (basic, standard, premium).'
                )

    def __str__(self):
        return self.title
    
class OfferDetail(models.Model):
    """
    Represents the details of an offer, including pricing and features for different tiers.

    Attributes:
        OFFER_TYPE_CHOICES (list): Choices for offer types (basic, standard, premium).
        offer (ForeignKey): The offer this detail belongs to.
        title (CharField): The title of the offer detail.
        revisions (PositiveIntegerField): Number of revisions allowed.
        delivery_time_in_days (PositiveIntegerField): Delivery time in days.
        price (DecimalField): The price of the offer detail.
        offer_type (CharField): The type of the offer (basic, standard, premium).
        features (JSONField): A list of features included in the offer detail.
    """

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
    """
    Represents an order placed by a customer for a specific offer detail from a business user.

    Attributes:
        STATUS_CHOICES (list): Choices for order status (in_progress, completed, cancelled).
        offer_detail (ForeignKey): The offer detail being ordered.
        customer_user (ForeignKey): The customer placing the order.
        business_user (ForeignKey): The business user fulfilling the order.
        title (CharField): The title of the order.
        revisions (PositiveIntegerField): Number of revisions allowed.
        delivery_time_in_days (PositiveIntegerField): Delivery time in days.
        price (DecimalField): The price of the order.
        features (JSONField): A list of features included in the order.
        offer_type (CharField): The type of the offer (basic, standard, premium).
        status (CharField): The current status of the order.
        created_at (DateTimeField): The date and time the order was created.
        updated_at (DateTimeField): The date and time the order was last updated.
    """

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
    """
    Represents a review given by a customer to a business user.

    Attributes:
        reviewer (ForeignKey): The user who gave the review.
        business_user (ForeignKey): The business user being reviewed.
        rating (PositiveSmallIntegerField): The rating given (1-5).
        description (TextField): The description of the review.
        created_at (DateTimeField): The date and time the review was created.
        updated_at (DateTimeField): The date and time the review was last updated.
    """

    reviewer  = models.ForeignKey(User, related_name='reviewer', on_delete=models.CASCADE)
    business_user = models.ForeignKey(User, related_name='review_for', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Review {self.rating}/5 by {self.reviewer} for {self.business_user}'