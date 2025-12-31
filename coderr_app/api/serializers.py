from rest_framework import serializers
from coderr_app.models import Offer, OfferDetail, Order



class OfferDetailSerializer(serializers.ModelSerializer):
    features = serializers.ListField( child=serializers.CharField(max_length=100))

    class Meta:
        model = OfferDetail
        fields = [ 'id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)
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

    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [ 'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time' ]
        
    def get_min_price(self, obj):
        return obj.details.order_by('price').values_list(
            'price', flat=True
        ).first()
        
    def get_min_delivery_time(self, obj):
        return obj.details.order_by('delivery_time_in_days').values_list(
            'delivery_time_in_days', flat=True
        ).first()
    


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
        allowed_transitions = {
            'in_progress': ['completed', 'cancelled'],
            'completed': [],
            'cancelled': [],
        }

        current_status = self.instance.status
        if value not in allowed_transitions[current_status]:
            raise serializers.ValidationError(f'Cannot change status from {current_status} to {value}.')

        return value
