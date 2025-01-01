from rest_framework import serializers
from .models import User, ReturnRequest,Category, Brand, Store, Product, Order, OrderItem,Banner, Coupon, Address, Payment, Wishlist, Cart, CartItem, ProductImage
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse




User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # Handle group assignments via SlugRelatedField
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'password', 'total_amount_spent', 'last_login', 'date_joined', 'groups']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def create(self, validated_data):
        # Pop the groups field from validated_data
        groups_data = validated_data.pop('groups', None)

        # Create the user with necessary details
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            is_active=False  # User will be inactive until email verification
        )

        # If groups were provided, assign them to the user
        if groups_data:
            for group in groups_data:
                user.groups.add(group)

        return user

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'logo', 'description', 'parent', 'subcategories', 'created_at', 'updated_at']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo', 'description', 'created_at', 'updated_at']

class StoreSerializer(serializers.ModelSerializer):
    brands = BrandSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    brand_ids = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all(), write_only=True, source='brands', many=True)
    category_ids = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True, source='categories', many=True)

    class Meta:
        model = Store
        fields = [
            'id', 'name', 'street_address', 'city', 'state', 'pin_code', 'country', 
            'display_image', 'brands', 'categories', 'slug', 
            'brand_ids', 'category_ids'
        ]
    
    # def create(self, validated_data):
    #     brands = validated_data.pop('brands', [])
    #     categories = validated_data.pop('categories', [])
    #     store = Store.objects.create(**validated_data)
    #     store.brands.set(brands)
    #     store.categories.set(categories)
    #     return store

    # def update(self, instance, validated_data):
    #     instance.brands.set(validated_data.pop('brands', []))
    #     instance.categories.set(validated_data.pop('categories', []))
    #     return super().update(instance, validated_data)





# class AttributeValueSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AttributeValue
#         fields = ['id', 'attribute', 'value']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    brand = BrandSerializer()
    store = StoreSerializer()
    gallery = ProductImageSerializer(many=True, read_only=True)
    # attributes = AttributeValueSerializer(many=True, read_only=True)
    is_wishlisted = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'mrp', 'sale_price', 'category', 
                  'brand', 'store', 'image', 'gallery', 'attributes', 'created_at','is_wishlisted']
    
    def get_is_wishlisted(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return Wishlist.objects.filter(user=user, product=obj).exists()
        return False

    def create(self, validated_data):
        # Handles creating products with possible nested operations if needed
        return super().create(validated_data)
    

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    # cart = CartSerializer()
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True)
    store = StoreSerializer()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'cart_items','store','updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'added_at']


class BannerSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'tagline', 'button_text', 'button_link',
            'image', 'link', 'place', 'is_active', 'created_at'
        ]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'street_address', 'city', 'state', 'postal_code', 'country', 'latitude', 'longitude','is_default']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']

# class OrderSerializer(serializers.ModelSerializer):
#     user = UserSerializer()
#     store = StoreSerializer()
#     order_items = OrderItemSerializer(many=True)

#     class Meta:
#         model = Order
#         fields = ['id', 'user', 'store', 'address','total_amount', 'payment_status', 'order_status', 'payment_method', 'created_at', 'order_items','updated_at']

#     def create(self, validated_data):
#         items_data = validated_data.pop('order_items')
#         order = Order.objects.create(**validated_data)
#         for item_data in items_data:
#             OrderItem.objects.create(order=order, **item_data)
#         return order


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    store_name = serializers.CharField(source='store.name', read_only=True)  # Example if you want the store name

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'user', 'full_name', 'phone_number', 'email', 
            'street_address', 'city', 'state', 'pin_code', 'country',
            'store', 'store_name', 'total_amount', 'payment_status', 
            'tracking_id', 'delivery_status', 'order_status', 
            'placed_at', 'updated_at', 'order_items'
        ]
        read_only_fields = ['id', 'order_no', 'placed_at', 'updated_at']

    def create(self, validated_data):
        """
        Create an Order with nested OrderItems.
        """
        items_data = validated_data.pop('order_items')
        with transaction.atomic():  # Ensure atomicity
            order = Order.objects.create(**validated_data)
            order_items = [
                OrderItem(order=order, **item_data) for item_data in items_data
            ]
            OrderItem.objects.bulk_create(order_items)
        return order

    def validate_order_items(self, value):
        """
        Ensure the order has at least one item.
        """
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value


# class InventorySerializer(serializers.ModelSerializer):
#     product = ProductSerializer()
#     store = StoreSerializer()

#     class Meta:
#         model = Inventory
#         fields = ['id', 'product', 'store', 'quantity']


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class ReturnRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnRequest
        fields = '__all__'



class StatisticsSerializer(serializers.Serializer):
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_products = serializers.IntegerField()
    recent_orders = OrderSerializer(many=True)

    total_users = serializers.IntegerField(allow_null=True)
    total_commission = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    recent_orders = serializers.ListField(child=serializers.DictField())
    top_selling_products = serializers.ListField(child=serializers.DictField())








# class ProductReviewSerializer(serializers.ModelSerializer):
#     user = UserSerializer()

#     class Meta:
#         model = ProductReview
#         fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']



class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer()

    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_method', 'amount', 'status', 'transaction_id', 'payment_date']



