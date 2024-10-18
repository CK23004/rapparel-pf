from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
import uuid
from django.db import IntegrityError
from django.utils.text import slugify
import datetime
# User Model
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=False)
    email = models.EmailField(unique=True)
    total_amount_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone_number']

    class Meta:
        verbose_name = "User Details"
        verbose_name_plural = "User Details"
    def __str__(self):
        return self.email

    


# Category Model
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=False, blank=True, null=True)  # Add slug field
    logo = models.ImageField(upload_to='category_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it is empty
            original_slug = slugify(self.name)
            unique_slug = original_slug
            counter = 1

            # Ensure the slug is unique
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{original_slug}-{counter}'
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Product Category"  # Changes the singular name in the admin
        verbose_name_plural = "Product Categories" 

# Brand Model
class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=False, blank=True, null=True)  # Add slug field
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it is empty
            original_slug = slugify(self.name)
            unique_slug = original_slug
            counter = 1

            # Ensure the slug is unique
            while Brand.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{original_slug}-{counter}'
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name

# Store Model
class Store(models.Model):
    INVENTORY_SOFTWARE_CHOICES = [
        ('excel', 'Excel'),
        ('unicommerce', 'UniCommerce'),
        ('sap_hana', 'SAP HANA'),
        ('logicerp', 'LogicERP'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # Ensure store name is unique
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    street_address = models.CharField(max_length=255,blank=True, null=True)
    city = models.CharField(max_length=100,blank=True, null=True)
    state = models.CharField(max_length=100,blank=True, null=True)
    pin_code = models.CharField(max_length=20,blank=True, null=True)
    country = models.CharField(max_length=100,blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    owner_name = models.ForeignKey(User, on_delete=models.CASCADE)
    owner_contact = models.CharField(max_length=15)
    owner_email = models.CharField(max_length=100)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_number = models.CharField(max_length=15, blank=True, null=True)
    display_image = models.ImageField(upload_to='store_images/', blank=True, null=True)
    banner_image = models.ImageField(upload_to='store_images/banners/', blank=True, null=True)
    inventory_software = models.CharField(max_length=255, choices=INVENTORY_SOFTWARE_CHOICES)  # Select box
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Commission rate as a percentage")
    is_featured = models.BooleanField(default=False)  # Added field for featured stores
    categories = models.ManyToManyField(Category, related_name='stores')
    brands = models.ManyToManyField(Brand, related_name='stores')

    # Fields for API access and credentials
    api_access_token = models.CharField(max_length=255, blank=True, null=True)
    api_refresh_token = models.CharField(max_length=255, blank=True, null=True)
    api_token_expiry = models.DateTimeField(blank=True, null=True)
    api_client_id = models.CharField(max_length=255, blank=True, null=True)
    api_client_secret = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
         # Ensure slug is unique
        original_slug = self.slug
        queryset = Product.objects.filter(slug=original_slug).exclude(pk=self.pk)
        counter = 1
        while queryset.exists():
            self.slug = f"{original_slug}-{counter}"
            queryset = Product.objects.filter(slug=self.slug).exclude(pk=self.pk)
            counter += 1

        super(Store, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


# Banner Model
class Banner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.CharField(max_length=255, choices=[
        ('primary', 'Primary'),
        ('secondary_one', 'Secondary One'),
        ('secondary_two', 'Secondary Two'),
        ('secondary_three', 'Secondary Three'),
        # Add more places as needed
    ])
    title = models.CharField(max_length=255, null=True, blank=True, default='')
    tagline = models.CharField(max_length=555, null=True, blank=True, default='')
    button_text = models.CharField(max_length=100, blank=True, null=True, default='')
    button_link = models.URLField(blank=True, null=True, default='')
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Promotions"
        verbose_name_plural = "Promotions"

class Attribute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # e.g., Size, Color, Material
    description = models.TextField(blank=True, null=True)  # Optional
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Attribute"
        verbose_name_plural = "Product Attributes"

class AttributeValue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attribute = models.ForeignKey(Attribute, related_name='values', on_delete=models.CASCADE)
    value = models.CharField(max_length=255)  # e.g., Small, Red, Cotton

    def __str__(self):
        return f'{self.attribute.name}: {self.value}'
    



# Product Model
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    inventory = models.IntegerField(default=0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, related_name='products', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, related_name='products', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    gallery = models.ManyToManyField('ProductImage', related_name='product_gallery', blank=True)
    attributes = models.ManyToManyField(AttributeValue, related_name='products', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = base_slug
            # Ensure unique slug
            i = 1
            while Product.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{i}"
                i += 1
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_similar_products(self):
        return Product.objects.filter(store=self.store, category=self.category).exclude(id=self.id).order_by('-created_at')[:4]

    def clean(self):
        if self.sale_price > self.mrp:
            raise ValidationError("Sale price cannot be greater than the MRP.")

    # def save(self, *args, **kwargs):
    #     self.full_clean()  # Ensure clean method is called
    #     super(Product, self).save(*args, **kwargs)


#for product gallery
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE) 
    image = models.ImageField(upload_to='product_gallery/')

    def __str__(self):
        return f'Image for {self.product.name}'

# Address Model
class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_default = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.street_address}, {self.city}, {self.state}, {self.country}'

# Wishlist Model
class Wishlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='wishlist', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlisted_by', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "My Wishlist"
        verbose_name_plural = "My Wishlist"
        unique_together = ('user', 'product')

    def __str__(self):
        return f'{self.user.username} - {self.product.name}'


# Cart Model
class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='cart', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    items = models.ManyToManyField('CartItem', related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f'Cart for {self.user.email}'

    def apply_coupon(self, coupon_code):
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True, valid_from__lte=datetime.datetime.now(), valid_until__gte=datetime.datetime.now())
        except Coupon.DoesNotExist:
            return False, "Invalid coupon"

        if self.coupon is not None:
            return False, "A coupon is already applied"

        # Check coupon conditions like minimum spend, category exclusions, etc.
        if coupon.minimum_spend and self.get_total_price() < coupon.minimum_spend:
            return False, "Minimum spend not reached"

        # If all conditions are met, apply the coupon
        self.coupon = coupon
        self.save()
        return True, "Coupon applied successfully"

    def get_total_price(self):
        return sum(item.product.sale_price * item.quantity for item in self.items.all())

# Cart Item Model
class CartItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name} in cart of {self.cart.user.email}'

# Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    # address = models.ForeignKey(Address, related_name='orders', on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)  # Full name of the person who placed the order
    phone_number = models.CharField(max_length=15)  # Phone number with reasonable length
    email = models.EmailField()
    street_address = models.CharField(max_length=255,blank=True, null=True)
    city = models.CharField(max_length=100,blank=True, null=True)
    state = models.CharField(max_length=100,blank=True, null=True)
    pin_code = models.CharField(max_length=20,blank=True, null=True)
    country = models.CharField(max_length=100,blank=True, null=True)
    # payment_method = models.CharField(max_length=50)
    store = models.ForeignKey(Store, related_name='orders', on_delete=models.SET_NULL, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=(('Pending', 'Pending'), ('Completed', 'Completed')),default='pending' )
    tracking_id = models.CharField(max_length=255, blank=True, null=True)  # Tracking ID from the shipping partner
    delivery_status = models.CharField(max_length=50, blank=True, null=True) #delivery status from the same
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending') #incomplete (integration with delivery partner system)
    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id} - {self.user.email}'
    
    class Meta:
        verbose_name = "Manage Order"
        verbose_name_plural = "Manage Orders"
# OrderItem Model
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at the time of order

    def __str__(self):
        return f'{self.product.name} - {self.quantity} pcs'

    def get_total_price(self):
        return self.quantity * self.price
    





# Coupon Model (need to make view function to create coupons from backend)
class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # New fields for coupon applicability
    minimum_spend = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    individual_use = models.BooleanField(default=False)
    exclude_sale_items = models.BooleanField(default=False)
    
    # # Relationships to products and categories
    specific_products = models.ManyToManyField('Product', related_name='coupons', blank=True)
    exclude_products = models.ManyToManyField('Product', related_name='excluded_coupons', blank=True)
    specific_categories = models.ManyToManyField('Category', related_name='category_coupons', blank=True)
    exclude_categories = models.ManyToManyField('Category', related_name='excluded_category_coupons', blank=True)
    
    # Usage limits
    usage_limit_per_coupon = models.PositiveIntegerField(null=True, blank=True)
    usage_limit_per_user = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.code

# Payment Model (for individual orders) (skip saving payment info for mvp) (#incomplete because of phonepe intgration)
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
        ('cod', 'Cash on Delivery'),
    ])
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ])
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment for Order {self.order.id}'

    class Meta:
            verbose_name = "Payment Details"  # Changes the singular name in the admin
            verbose_name_plural = "Payment Details"

# Inventory Model (for individual product) #incomplete for inventory sync with thirdparty system in real time
class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, related_name='inventories', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, related_name='inventories', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    last_updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Inventory"
        verbose_name_plural = "Product Inventory"
        unique_together = ('product', 'store')

    def __str__(self):
        return f'{self.product.name} at {self.store.name}'

#return request model
class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    order_item = models.ForeignKey('OrderItem', related_name='return_requests', on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Return request for {self.order_item.product.name} - Status: {self.status}'




















    





    



























    

# # ProductReview Model
# class ProductReview(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
#     rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
#     comment = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'{self.product.name} - {self.rating} Stars'