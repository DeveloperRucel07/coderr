from rest_framework import serializers
from django.contrib.auth.models import User
from coderr_app.models import Offer, OfferDetail, Order, Review


class UserDetailSerialiser(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['first_name', 'last_name', 'username'] 

class OfferDetailOrderSerializer(serializers.ModelSerializer):
    features = serializers.ListField( child=serializers.CharField(max_length=100))

    class Meta:
        model = OfferDetail
        fields = [ 'id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required = True)
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailOrderSerializer(many=True)
    user = serializers.ReadOnlyField(source='user.id')
    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'details',]
        read_only_fields = ['id', 'user']
        
    def validate_details(self, value):

        if len(value) != 3:
            raise serializers.ValidationError( 'An offer must contain exactly 3 details.')
        offer_types = {detail['offer_type'] for detail in value}
        required_types = {'basic', 'standard', 'premium'}
        if offer_types != required_types:
            raise serializers.ValidationError('Details must include exactly: basic, standard, premium.')
        return value
    
    def validate(self, attrs):
        """
        Validate the entire serializer data.

        Ensures only business users can create offers.

        Args:
            attrs (dict): The serializer data.

        Returns:
            dict: The validated data.

        Raises:
            ValidationError: If the user is not a business user.
        """
        request = self.context['request']
        if request.user.profile.type != 'business':
            raise serializers.ValidationError('Only business users can create offers.')
        return attrs
    
    def create(self, validated_data):
        request = self.context['request']
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=request.user,  **validated_data)

        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data )

        return offer


class OfferDetailLinkSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='offerdetail-detail')

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

class OfferListSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(
        many=True,
        read_only=True
    )

    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = UserDetailSerialiser(source = 'user', read_only = True)

    class Meta:
        model = Offer
        fields = [ 'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details' ]


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailUpdateSerializer(many=True, required=False)
    class Meta:
        model = Offer
        fields = ['id', 'title', 'description', 'image', 'details'  ]
    
    def validate_details(self, value):
        """
        Validate the details for offer update.

        Ensures all offer types are valid.

        Args:
            value (list): List of detail dictionaries.

        Returns:
            list: The validated details.

        Raises:
            ValidationError: If an invalid offer type is provided.
        """
        allowed_types = {'basic', 'standard', 'premium'}
        for detail in value:
            offer_type = detail.get('offer_type')
            if offer_type and offer_type not in allowed_types:
                raise serializers.ValidationError(f'Invalid offer type: {offer_type}')
        return value
        
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if details_data:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                
                if not offer_type:
                    raise serializers.ValidationError('offer_type is required to update an offer detail.')
                
                try:
                    detail = instance.details.get(offer_type = offer_type)
                except OfferDetail.DoesNotExist:
                    raise serializers.ValidationError(f'Offer detail with type {offer_type} not found.')
                
                
                for attr, value in detail_data.items():
                    if attr != 'offer_type':
                        setattr(detail, attr, value)
                
                detail.save()
        return instance
        
    

class OfferDetailSerializer(serializers.ModelSerializer):
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = ['id',  'user',  'title',  'image',  'description',  'created_at',  'updated_at',  'details', 'min_price', 'min_delivery_time'  ]
        
    def get_min_price(self, obj):
        """
        Get the minimum price from the offer details.

        Args:
            obj (Offer): The offer instance.

        Returns:
            float: The minimum price.
        """
        return obj.details.order_by('price').values_list('price', flat=True ).first()
        
    def get_min_delivery_time(self, obj):
        """
        Get the minimum delivery time from the offer details.

        Args:
            obj (Offer): The offer instance.

        Returns:
            int: The minimum delivery time in days.
        """
        return obj.details.order_by('delivery_time_in_days').values_list('delivery_time_in_days', flat=True).first()


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        try:
            detail = OfferDetail.objects.select_related('offer__user').get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError('Offer detail does not exist.')

        request = self.context['request']

        if detail.offer.user == request.user:
            raise serializers.ValidationError('You cannot order your own offer.')

        return detail

    def create(self, validated_data):
        request = self.context['request']
        detail = validated_data['offer_detail_id']

        order = Order.objects.create(
            offer_detail=detail,
            customer_user=request.user,
            business_user=detail.offer.user,
            title=detail.title,
            revisions=detail.revisions,
            delivery_time_in_days=detail.delivery_time_in_days,
            price=detail.price,
            features=detail.features,
            offer_type=detail.offer_type,
        )

        return order
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [ 'id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at' ]
        read_only_fields = fields
    
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

    def validate_status(self, value):
        """
        Validate the order status.

        Ensures the status is one of the allowed values.

        Args:
            value (str): The status value.

        Returns:
            str: The validated status.

        Raises:
            ValidationError: If the status is invalid.
        """
        allowed_statuses = {'in_progress', 'completed', 'cancelled'}

        if value not in allowed_statuses:
            raise serializers.ValidationError('Invalid status.')
        return value



class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [ 'id', 'business_user', 'reviewer', 'rating', 'description', 'created_at', 'updated_at' ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer']
        
    def validate_business_user(self, value):
        if getattr(value.profile, 'type', None) != 'business':
            raise serializers.ValidationError('You can only review business users.')
        return value
    
    def validate(self, attrs):
        request = self.context['request']
        if self.instance is None:
            if Review.objects.filter( business_user=attrs['business_user'], reviewer=request.user).exists():
                raise serializers.ValidationError('You have already reviewed this business user.')
        return attrs

    def create(self, validated_data):
        request = self.context['request']
        return Review.objects.create(reviewer=request.user, **validated_data)
    
    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
