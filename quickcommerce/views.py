from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAdminUser, IsManagerUser, IsStaffUser
from rest_framework.parsers import MultiPartParser, FormParser
from .forms import PasswordResetForm

from rest_framework import status, generics,serializers
from django.db.models import Sum, F
from .models import Banner,Coupon ,Inventory,ReturnRequest,Product,ProductImage, Category, Brand, Cart, CartItem, Order, Wishlist, Address, User, OrderItem, Store, Attribute
from .serializers import (
    BannerSerializer, ProductSerializer, CategorySerializer, BrandSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer, WishlistSerializer, 
    AddressSerializer, UserSerializer, StoreSerializer, CouponSerializer, ReturnRequestSerializer ,StatisticsSerializer, InventorySerializer)
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import datetime, requests
from django.core.mail import send_mail, EmailMessage
from django.utils.html import strip_tags
from django.shortcuts import render 
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.auth import get_user_model


from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.db import IntegrityError  # Import IntegrityError to handle duplicates
from django.utils.http import url_has_allowed_host_and_scheme



from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas as pd


# #home page
# class LandingPageView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         # Fetch banners, categories, and brands
#         banners = Banner.objects.filter(is_active=True)
#         categories = Category.objects.all()
#         brands = Brand.objects.all()

#         banners_serializer = BannerSerializer(banners, many=True)
#         categories_serializer = CategorySerializer(categories, many=True)
#         brands_serializer = BrandSerializer(brands, many=True)

#         # Initialize variables
#         address = None
#         nearby_stores = []
#         saved_addresses = []
#         featured_stores = []

#         # Check if the user is authenticated and fetch saved addresses
#         user = request.user
#         if user.is_authenticated:
#             saved_addresses = Address.objects.filter(user=user, is_default=True)
#             if saved_addresses.exists():
#                 user_address = saved_addresses.first()
#                 address_location = f"{user_address.street_address}, {user_address.city}, {user_address.state}, {user_address.country}"
#                 geolocator = Nominatim(user_agent="quick-commerce-app")
#                 location = geolocator.reverse(address_location)
#                 address = location.address if location else address_location

#                 # Convert user's saved address to a tuple (latitude, longitude)
#                 user_coords = (user_address.latitude, user_address.longitude)
#             else:
#                 address = "No saved address found."

#         # Check if real-time location is provided in the query parameters
#         latitude = request.query_params.get('latitude')
#         longitude = request.query_params.get('longitude')
#         if latitude and longitude:
#             user_coords = (float(latitude), float(longitude))
#             geolocator = Nominatim(user_agent="quick-commerce-app")
#             location = geolocator.reverse(user_coords, exactly_one=True)
#             address = location.address if location else "Location address not found"
#             # Find nearby stores based on coordinates
#             stores = Store.objects.all()
#             store_distances = []
#             for store in stores:
#                 store_coords = (store.latitude, store.longitude)
#                 distance = geodesic(user_coords, store_coords).kilometers
#                 store_distances.append((store, distance))
#             store_distances.sort(key=lambda x: x[1])
#             nearby_stores = [store[0] for store in store_distances[:12]]
#         else:
#             # No real-time location provided, fetch featured stores
#             featured_stores = Store.objects.filter(is_featured=True).order_by('-id')[:12]
        
#         # Serialize the store data
#         stores_serializer = StoreSerializer(nearby_stores if latitude and longitude else featured_stores, many=True)

#         data = {
#             'banners': banners_serializer.data,
#             'categories': categories_serializer.data,
#             'brands': brands_serializer.data,
#             'user_address': address,
#             'saved_addresses': [f"{addr.street_address}, {addr.city}, {addr.state}, {addr.country}" for addr in saved_addresses],
#             'nearby_stores': stores_serializer.data,
#         }
#         return Response(data, status=200)

class LandingPageView(TemplateView):
    template_name = "landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch banners based on 'place'
        primary_banner = Banner.objects.filter(is_active=True, place='primary').first()
        secondary_banners = Banner.objects.filter(is_active=True, place__in=['secondary_one', 'secondary_two', 'secondary_three'])

        # Fetch categories and brands
        categories = Category.objects.all()
        brands = Brand.objects.all()

        # Initialize variables
        address = None
        nearby_stores = []
        saved_addresses = []
        featured_stores = []
        user_coords = None  # Initialize variable for user's coordinates

        # Check if the user is authenticated and fetch saved addresses
        user = self.request.user
        if user.is_authenticated:
            saved_addresses = Address.objects.filter(user=user)  # Fetch all addresses, not just default

            # If the user has default address, use it
            if saved_addresses.exists():
                default_address = saved_addresses.filter(is_default=True).first()
                if default_address:
                    user_coords = (default_address.latitude, default_address.longitude)
                    address = f"{default_address.street_address}, {default_address.city}, {default_address.state}, {default_address.country}"
                else:
                    address = "No default address found."

        # Check if real-time location is provided in the query parameters
        latitude = self.request.GET.get('latitude')
        longitude = self.request.GET.get('longitude')

        # Override the saved address with real-time location if provided
        if latitude and longitude:
            user_coords = (float(latitude), float(longitude))
            geolocator = Nominatim(user_agent="quick-commerce-app")
            location = geolocator.reverse(user_coords, exactly_one=True)
            address = location.address if location else "Location address not found"
        
        # Fetch nearby stores based on coordinates
        if user_coords:
            stores = Store.objects.all()
            store_distances = []
            for store in stores:
                store_coords = (store.latitude, store.longitude)
                distance = geodesic(user_coords, store_coords).kilometers
                store_distances.append((store, distance))
            store_distances.sort(key=lambda x: x[1])  # Sort stores by distance
            nearby_stores = [store[0] for store in store_distances[:12]]
        else:
            # No location provided, fetch featured stores
            featured_stores = Store.objects.filter(is_featured=True).order_by('-id')[:12]

        # Add serialized data to context
        context['primary_banner'] = primary_banner
        context['secondary_banners'] = secondary_banners
        context['categories'] = categories
        context['brands'] = brands
        context['user_address'] = address
        context['saved_addresses'] = list(saved_addresses)
        context['nearby_stores'] = nearby_stores if user_coords else featured_stores

        return context
    


def fetch_saved_addresses(request):
    # Ensure the user is authenticated
    if request.user.is_authenticated:
        saved_addresses = Address.objects.filter(user=request.user).values(
            'id', 'street_address', 'city', 'state', 'country', 'latitude', 'longitude'
        )
        return JsonResponse(list(saved_addresses), safe=False)
    else:
        return JsonResponse([], safe=False)


# #when clicked on category this view will be rendered...
# class CategoryStoresView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         category_id = request.query_params.get('category')
#         latitude = request.query_params.get('latitude')
#         longitude = request.query_params.get('longitude')
#         user_address_id = request.query_params.get('address_id')


#         # Validate category ID
#         if not category_id:
#             return Response({'error': 'Category ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             category = Category.objects.get(id=category_id)
#         except Category.DoesNotExist:
#             return Response({'error': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

#         user_coords = None
#         if latitude and longitude:
#             user_coords = (float(latitude), float(longitude))
#         elif user_address_id:
#             try:
#                 address = Address.objects.get(id=user_address_id)
#                 user_coords = (address.latitude, address.longitude)
#             except Address.DoesNotExist:
#                 return Response({'error': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'error': 'Latitude and longitude are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch stores that belong to the category
#         stores = Store.objects.filter(categories=category)

#         # Calculate distances and sort by proximity
#         store_distances = []
#         for store in stores:
#             store_coords = (store.latitude, store.longitude)
#             distance = geodesic(user_coords, store_coords).kilometers
#             store_distances.append((store, distance))

#         store_distances.sort(key=lambda x: x[1])
#         nearby_stores = [store[0] for store in store_distances]

#         # Serialize the store data
#         stores_serializer = StoreSerializer(nearby_stores, many=True)

#         data = {
#             'category': category.name,
#             'nearby_stores': stores_serializer.data,
#         }
#         return Response(data, status=status.HTTP_200_OK)


class CategoryStoresView(View):
    def get(self, request, category_slug, *args, **kwargs):
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        user_address_id = request.GET.get('address_id')

        # Fetch the category using the name
        category = get_object_or_404(Category, slug=category_slug)

        user_coords = None
        if latitude and longitude:
            try:
                user_coords = (float(latitude), float(longitude))
            except ValueError:
                return
        elif user_address_id:
            address = get_object_or_404(Address, id=user_address_id)
            user_coords = (address.latitude, address.longitude)
       

        # Fetch stores that belong to the category
        stores = Store.objects.filter(categories=category)

        # Calculate distances and sort by proximity
        store_distances = []
        for store in stores:
            store_coords = (store.latitude, store.longitude)
            distance = geodesic(user_coords, store_coords).kilometers
            store_distances.append((store, distance))

        store_distances.sort(key=lambda x: x[1])
        nearby_stores = [store[0] for store in store_distances]

        # Pass the category and stores data to the template
        context = {
            'category_name': category.name,
            'nearby_stores': nearby_stores,
        }

        return render(request, 'category_base.html', context)
    
# #when clicked on brand this will be rendered
# class BrandStoresView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         brand_id = request.query_params.get('brand')
#         latitude = request.query_params.get('latitude')
#         longitude = request.query_params.get('longitude')
#         user_address_id = request.query_params.get('address_id')

#         if not brand_id:
#             return Response({'error': 'Brand ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             brand = Brand.objects.get(id=brand_id)
#         except Brand.DoesNotExist:
#             return Response({'error': 'Brand not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Get user's location or selected address
#         user_coords = None
#         if latitude and longitude:
#             user_coords = (float(latitude), float(longitude))
#         elif user_address_id:
#             try:
#                 address = Address.objects.get(id=user_address_id)
#                 user_coords = (address.latitude, address.longitude)
#             except Address.DoesNotExist:
#                 return Response({'error': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)
#         else:
#             return Response({'error': 'Latitude, longitude, or address_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

#         # Fetch stores that have the brand
#         stores = Store.objects.filter(brands=brand)

#         # Calculate distances and find the nearest store
#         store_distances = []
#         for store in stores:
#             store_coords = (store.latitude, store.longitude)
#             distance = geodesic(user_coords, store_coords).kilometers
#             store_distances.append((store, distance))

#         store_distances.sort(key=lambda x: x[1])
#         nearest_store = store_distances[0][0] if store_distances else None

#         # Fetch products from the nearest store filtered by the brand
#         products = Product.objects.filter(store=nearest_store, brand=brand) if nearest_store else []

#         # Calculate estimated arrival time
#         estimated_arrival_time = None
#         if nearest_store:
#             estimated_arrival_time = int(store_distances[0][1] * 60)  # Assuming 1 km = 1 minute of travel

#         # Serialize store and brand data
#         all_stores_serializer = StoreSerializer([store[0] for store in store_distances], many=True)
#         nearest_store_serializer = StoreSerializer(nearest_store)
#         categories = nearest_store.categories.all()
#         categories_serializer = CategorySerializer(categories, many=True)
#         brand_serializer = BrandSerializer(brand)
#         products_serializer = ProductSerializer(products, many=True)


#         data = {
#             'brand': brand_serializer.data,
#             'nearest_store': nearest_store_serializer.data,
#             'all_stores': all_stores_serializer.data,
#             'categories': categories_serializer.data,
#             'estimated_arrival_time': estimated_arrival_time,
#             'products': products_serializer.data,

#         }
#         return Response(data, status=status.HTTP_200_OK)

class BrandStoresView(View):
    def get(self, request, brand_slug, *args, **kwargs):
        latitude = request.GET.get('latitude')
        longitude = request.GET.get('longitude')
        user_address_id = request.GET.get('address_id')

        # Fetch the brand using the slug
        brand = get_object_or_404(Brand, slug=brand_slug)

        user_coords = None
        if latitude and longitude:
            try:
                user_coords = (float(latitude), float(longitude))
            except ValueError:
                return
        elif user_address_id:
            address = get_object_or_404(Address, id=user_address_id)
            user_coords = (address.latitude, address.longitude)

        # Fetch stores that carry the brand
        stores = Store.objects.filter(brands=brand)

        # Calculate distances and sort by proximity
        store_distances = []
        for store in stores:
            store_coords = (store.latitude, store.longitude)
            distance = geodesic(user_coords, store_coords).kilometers
            store_distances.append((store, distance))

        store_distances.sort(key=lambda x: x[1])
        nearby_stores = [store[0] for store in store_distances]

        # Pass the brand and stores data to the template
        context = {
            'brand_name': brand.name,
            'nearby_stores': nearby_stores,
        }

        return render(request, 'brand_base.html', context)


# #individual store view
# class StoreDetailView(APIView):
#     permission_classes = [AllowAny]

#     def get(self, request, store_slug):
#         try:
#             # Fetch the store by slug
#             store = Store.objects.get(slug=store_slug)
            
#             user_location = request.query_params.get('location')
#             address_id = request.query_params.get('address_id')
#             user_coords = None

#             if user_location:
#                 latitude, longitude = map(float, user_location.split(','))
#                 user_coords = (latitude, longitude)
#             elif address_id:
#                 try:
#                     address = Address.objects.get(id=address_id, user=request.user)
#                     user_coords = (address.latitude, address.longitude)
#                 except Address.DoesNotExist:
#                     return Response({'error': 'Address not found'}, status=status.HTTP_404_NOT_FOUND)

#             # Calculate the estimated arrival time if user location is available
#             estimated_arrival_time = None
#             if user_coords:
#                 store_coords = (store.latitude, store.longitude)
#                 distance = geodesic(user_coords, store_coords).kilometers

#                 # Assuming an average speed of 35 km/h for delivery (you can adjust this)
#                 average_speed_kmh = 35
#                 estimated_time_hours = distance / average_speed_kmh
#                 estimated_arrival_time = datetime.timedelta(hours=estimated_time_hours)


            
#             # Fetch all categories and brands associated with the store
#             categories = Category.objects.filter(product__store=store).distinct()
#             brands = Brand.objects.filter(product__store=store).distinct()
            
#             # Fetch all products available in the store
#             products = Product.objects.filter(store=store)
            
#             # Serialize the data
#             store_serializer = StoreSerializer(store)
#             categories_serializer = CategorySerializer(categories, many=True)
#             brands_serializer = BrandSerializer(brands, many=True)
#             products_serializer = ProductSerializer(products, many=True)

#             # Prepare the response data
#             data = {
#                 'store': store_serializer.data,
#                 'categories': categories_serializer.data,
#                 'brands': brands_serializer.data,
#                 'products': products_serializer.data,
#                 'estimated_arrival_time': estimated_arrival_time,

#             }

#             return Response(data, status=status.HTTP_200_OK)

#         except Store.DoesNotExist:
#             return Response({'error': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)

class StoreDetailView(View):
    def get(self, request, store_slug):
        # Fetch the store by slug or return 404 if not found
        store = get_object_or_404(Store, slug=store_slug)

        latitude = request.GET.get('latitude')  # Get latitude from query parameters
        longitude = request.GET.get('longitude')  # Get longitude from query parameters
        address_id = request.GET.get('address_id')  # Get address_id from query parameters
        user_coords = None

        if latitude and longitude:
            # Parse the user coordinates from the query parameters
            user_coords = (float(latitude), float(longitude))
        elif address_id:
            # Fetch the address by ID and check if it belongs to the current user
            address = get_object_or_404(Address, id=address_id, user=request.user)
            user_coords = (address.latitude, address.longitude)

        # Calculate the estimated arrival time if user coordinates are available
        estimated_arrival_time = None
        if user_coords:
            store_coords = (store.latitude, store.longitude)
            distance = geodesic(user_coords, store_coords).kilometers
            average_speed_kmh = 35  # Assuming an average speed of 35 km/h for delivery
            estimated_time_hours = distance / average_speed_kmh
            estimated_arrival_time = estimated_time_hours * 60

        # Fetch categories, brands, and products associated with the store
        categories = Category.objects.filter(products__store=store).distinct()
        brands = Brand.objects.filter(products__store=store).distinct()
        products = Product.objects.filter(store=store)
        store_address = f"{store.street_address}, {store.city}, {store.state}" if store.street_address else None
        attributes = Attribute.objects.filter(values__products__store=store).distinct()
        wishlisted_products = Wishlist.objects.filter(user=request.user).values_list('product__id', flat=True)

        # Prepare the context for rendering
        context = {
            'store': store,
            'categories': categories,
            'brands': brands,
            'products': products,
            'estimated_arrival_time': estimated_arrival_time,
            'wishlisted_products': wishlisted_products,
            'store_address': store_address ,
            'attributes' : attributes
        }

        # Render the template with the context data
        return render(request, 'store_detail.html', context)


# #single product page
# class ProductDetailView(APIView):
#     permission_classes = [AllowAny]

    
    
#     def get(self, request, slug, *args, **kwargs):
#         try:
#             product = Product.objects.get(slug=slug)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

#         product_serializer = ProductSerializer(product, context={'request': request})

#         # Fetch related store, brand, and category data
#         store_serializer = StoreSerializer(product.store)
#         brand_serializer = BrandSerializer(product.brand)
#         category_serializer = CategorySerializer(product.category)

#         # Fetch similar products
#         similar_products = product.get_similar_products()
#         similar_products_serializer = ProductSerializer(similar_products, many=True, context={'request': request})

#         data = {
#             'product': product_serializer.data,
#             'store': store_serializer.data,
#             'brand': brand_serializer.data,
#             'category': category_serializer.data,
#             'similar_products': similar_products_serializer.data,
#         }

#         return Response(data, status=status.HTTP_200_OK)

def product_detail_view(request, slug):
    # Get the product by slug, return 404 if not found
    product = get_object_or_404(Product, slug=slug)
    
    # Fetch similar products
    similar_products = product.get_similar_products()
    gallery_images = ProductImage.objects.filter(product=product)
    is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()
    discount_percentage = 0
    if product.sale_price < product.mrp:
        discount_percentage = ((product.mrp - product.sale_price) / product.mrp) * 100


    # Pass the product, gallery images, and similar products to the template
    context = {
        'product': product,
        'similar_products': similar_products,
        'gallery_images': gallery_images,  # Pass gallery images separately
        'discount_percentage': round(discount_percentage),  # Round off the percentage
        'is_wishlisted': is_wishlisted  # Pass the wishlist status to the template



    }

    return render(request, 'product_detail.html', context)

# #wishlist toggle & page view
# class WishlistToggleView(APIView):
#     permission_classes = [AllowAny]

#     # permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         wishlist = Wishlist.objects.filter(user=request.user)
#         wishlist_serializer = WishlistSerializer(wishlist, many=True)
#         return Response(wishlist_serializer.data, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         product_slug = request.data.get('product_slug')
#         try:
#             product = Product.objects.get(slug=product_slug)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

#         Wishlist.objects.get_or_create(user=request.user, product=product)
#         return Response({'status': 'added'}, status=status.HTTP_201_CREATED)

#     def delete(self, request, *args, **kwargs):
#         product_slug = request.data.get('product_slug')
#         try:
#             product = Product.objects.get(slug=product_slug)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

#         Wishlist.objects.filter(user=request.user, product=product).delete()
#         return Response({'status': 'removed'}, status=status.HTTP_204_NO_CONTENT)



# View Wishlist
# @login_required
# def view_wishlist(request):
#     wishlist = Wishlist.objects.filter(user=request.user)
#     return render(request, 'wishlist.html', {'wishlist': wishlist})

# Add to Wishlist
@login_required
@csrf_exempt
def add_to_wishlist(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        return JsonResponse({'status': 'added'}, status=201)  # Product was added to wishlist
    else:
        return JsonResponse({'status': 'already_exists'}, status=200)  # Product already in wishlist

# Remove from Wishlist
@login_required
@csrf_exempt
def remove_from_wishlist(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    if wishlist_item.exists():
        wishlist_item.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # If it's an AJAX request, return a JSON response with the redirect URL
            return JsonResponse({'status': 'removed', 'redirect_url': '/wishlist/'}, status=200)
        else:
            # Otherwise, redirect back to the wishlist page
            return redirect('view_wishlist')
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Product not found in wishlist'}, status=404)
        else:
            return redirect('view_wishlist')


@require_GET  # Only accept GET requests
def search_products(request):
    query = request.GET.get('q', None)  # Get the query parameter from the request

    if not query or len(query) < 2:
        return JsonResponse({'error': 'Please enter at least 2 characters'}, status=400)

    # Search products by name or other fields
    products = Product.objects.filter(name__icontains=query)[:10]  # Limit to 10 results for performance
    
    # Prepare the product data to be returned in JSON format
    product_list = [{
        'name': product.name,
        'price': product.sale_price,
        'image': product.image.url,
        'slug': product.slug
    } for product in products]
    print(product_list)
    return JsonResponse({'products': product_list}, status=200)




# #add to cart
# class AddToCartView(APIView):
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         product_id = request.data.get('product_id')
#         quantity = request.data.get('quantity', 1)
        
#         product = get_object_or_404(Product, id=product_id)
#         store = product.store
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         if cart.store and cart.store != store:
#             # Empty the cart if the store is different
#             cart.items.clear()

#         cart.store = store
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         cart_item.quantity = quantity
#         cart_item.save()
#         cart.save()

#         return Response({'message': 'Item added to cart successfully'}, status=status.HTTP_200_OK)

# class CartPageView(APIView):
#     permission_classes = [AllowAny]  # Allow both authenticated and anonymous users to access

#     def get(self, request, *args, **kwargs):
#         # Check if the user is authenticated
#         if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
#             # Try to fetch the cart for the authenticated user, or create one if not found
#             cart, created = Cart.objects.get_or_create(user=request.user)

#             # If the cart is newly created, return an empty cart message
#             if created:
#                 return Response({'message': 'Cart was created. It is currently empty.'}, status=status.HTTP_200_OK)

#             # If cart already exists, return the cart items and store info
#             items = CartItemSerializer(cart.items.all(), many=True).data
#             store = StoreSerializer(cart.store).data if cart.store else None
#             return Response({'store': store, 'items': items}, status=status.HTTP_200_OK)
        
#         # Handle anonymous users
#         return Response({'message': 'Please log in to view your cart.'}, status=status.HTTP_401_UNAUTHORIZED)



# #checkout page view
# class CheckoutPageView(APIView):
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [AllowAny]

#     def get(self, request, *args, **kwargs):
#         try:
#             cart = Cart.objects.get(user=request.user)
#         except Cart.DoesNotExist:
#             return Response({'detail': 'Cart is empty.'}, status=status.HTTP_404_NOT_FOUND)

#         addresses = Address.objects.filter(user=request.user)
#         address_serializer = AddressSerializer(addresses, many=True)
#         cart_serializer = CartSerializer(cart)

#         data = {
#             'cart': cart_serializer.data,
#             'addresses': address_serializer.data,
#         }
#         return Response(data, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         cart = Cart.objects.get(user=request.user)
#         address_id = request.data.get('address_id')
#         payment_method = request.data.get('payment_method')

#         if not cart.items.exists():
#             return Response({'error': 'Your cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             address = Address.objects.get(id=address_id, user=request.user)
#         except Address.DoesNotExist:
#             return Response({'error': 'Invalid address'}, status=status.HTTP_400_BAD_REQUEST)

#         total_amount = sum(item.product.sale_price * item.quantity for item in cart.items.all())

#         # Create the order
#         order = Order.objects.create(
#             user=request.user,
#             address=address,
#             total_amount=total_amount,
#             payment_status='Pending',
#             order_status='Processing',
#             payment_method=payment_method,
#         )

#         # Create order items
#         for item in cart.items.all():
#             OrderItem.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 price=item.product.sale_price,
#             )

#         # Clear the cart after order creation
#         cart.items.all().delete()

#         # Send Invoice Email
#         subject = f"Invoice for Order #{order.id}"
#         context = {
#             'order': order,
#             'user': request.user,
#             'logo_url': 'https://rapparel.com/static/logo.png',  # replace with actual logo URL
#         }

#         html_message = render_to_string('invoice_email.html', context)
#         plain_message = strip_tags(html_message)

#         customer_email = EmailMessage(subject, html_message, 'info@rapprel.com', [request.user.email])
#         customer_email.content_subtype = 'html'
#         customer_email.send()

#         # Send to Owner
#         owner_email = EmailMessage(subject, html_message, 'info@rapprel.com', ['owner@rapprel.com'])
#         owner_email.content_subtype = 'html'
#         owner_email.send()

#         # Send to Admin
#         admin_email = EmailMessage(subject, html_message, 'info@rapprel.com', ['admin@rapparel.com'])
#         admin_email.content_subtype = 'html'
#         admin_email.send()

#         return Response({'order_id': order.id, 'message': 'Order placed successfully'}, status=status.HTTP_201_CREATED)

# class AddToCartView(View):
#     def post(self, request, *args, **kwargs):
#         # Ensure user is authenticated
#         if not request.user.is_authenticated:
#             messages.error(request, "Please log in to add items to your cart.")
#             return redirect('login')  # Redirect to login if not authenticated

#         # Retrieve the product ID and quantity from the POST request
#         product_id = request.POST.get('product_id')
#         quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity is not provided

#         # Get the product and the user's cart
#         product = get_object_or_404(Product, id=product_id)
#         cart, created = Cart.objects.get_or_create(user=request.user)

#         # Add the product to the cart
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         cart_item.quantity += quantity  # Increment quantity if item already exists
#         cart_item.save()
#         cart.save()


#         # Redirect to cart page or any other page
#         return redirect('cart_checkout')  # Redirect to the cart and checkout page

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        # Ensure user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to add items to your cart.")
            return redirect('login')  # Redirect to login if not authenticated

        # Retrieve the product ID and quantity from the POST request
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if quantity is not provided

        # Get the product and the user's cart
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Check if there are existing items in the cart
        if cart.cart_items.exists():
            # Get the store of the new product
            new_product_store = product.store

            # Check the store of existing products in the cart
            existing_store = cart.cart_items.first().product.store  # Get the store of the first existing product

            # If the stores do not match, clear the cart
            if existing_store != new_product_store:
                cart.cart_items.all().delete()  # Clear the cart
                messages.info(request, "Your cart has been cleared to add a new product from a different store.")

        # Add the product to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += quantity  # Increment quantity if item already exists
        cart_item.save()
        cart.save()

        # Redirect to cart page or any other page
        return redirect('cart_checkout')

# def send_order_confirmation_email(order, cart_items, user_email):
#     # Prepare the email context with order and cart details
#     context = {
#         'order': order,
#         'cart_items': cart_items,
#         'total_amount': order.total_amount,
#         'address': order.address,
#     }

#     # Render the HTML email template
#     html_content = render_to_string('emails/order_confirmation.html', context)
#     text_content = strip_tags(html_content)  # Fallback to plain text if HTML is not supported

#     # Create the email message
#     subject = f"Order Confirmation - #{order.id}"
#     from_email = settings.DEFAULT_FROM_EMAIL
#     recipient_list = [user_email, settings.ADMIN_EMAIL]

#     # Send the email to both user and admin
#     email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
#     email.attach_alternative(html_content, "text/html")
#     email.send()



class CartCheckoutView(View):
    def get(self, request):
        # Retrieve the cart for the user
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            addresses = Address.objects.filter(user=request.user)

            # Calculate total price of the cart items
            total_price = sum(item.product.sale_price * item.quantity for item in cart_items)
            
            # Dummy discount logic (e.g., fixed discount or based on cart value)
            discount = 0
            # if total_price > 1000:  # Apply discount if cart total is more than ₹1000
            #     discount = 100  # Apply ₹100 discount

            # Delivery charges (you can adjust based on your business logic)
            if cart_items.exists():
                delivery_charges = 100 if total_price < 500 else 0  # Apply delivery charges if total is less than ₹500
            else:
                delivery_charges = 0
            # Final total amount after applying discount and adding delivery charges
            total_amount = total_price - discount + delivery_charges

            context = {
                'cart_items': cart_items,
                'addresses': addresses,
                'cart': cart,
                'discount': discount,
                'delivery_charges': delivery_charges,
                'total_price': total_price,
                'total_amount': total_amount,
            }

            return render(request, 'cart_checkout.html', context)

        else:
            cart_items = []
            addresses = []

            return render(request, 'cart_checkout.html', {
                'cart_items': cart_items,
                'addresses': addresses,
            })
    
    def post(self, request):
        # Proceed to checkout
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')

        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            return redirect('cart_checkout')

        address = get_object_or_404(Address, id=address_id, user=request.user)

        total_amount = sum(item.product.sale_price * item.quantity for item in cart_items)

        # Create the order
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total_amount,
            payment_status='Pending',
            order_status='Processing',
            payment_method=payment_method,
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.sale_price,
            )

        # Clear the cart
        cart_items.all().delete()

        # Send email and other order processing tasks
        send_order_confirmation_email(order, cart_items, request.user.email)


        return redirect('order_success', order_id=order.id)



# class UpdateCartItemView(View):
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return JsonResponse({'error': 'You must be logged in to update the cart.'}, status=403)

#         cart_item_id = request.POST.get('cart_item_id')
#         new_quantity = int(request.POST.get('quantity'))

#         # Get the cart item and update its quantity
#         cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
#         cart_item.quantity = new_quantity
#         cart_item.save()

#         # Recalculate cart totals
#         cart = cart_item.cart
#         total_price = sum(item.product.sale_price * item.quantity for item in CartItem.objects.filter(cart=cart))
#         discount = 0
#         # if total_price > 1000:
#         #     discount = 100  # Example discount logic
#         delivery_charges = 100 if total_price < 500 else 0
#         total_amount = total_price - discount + delivery_charges

#         # Return updated cart data in JSON format
#         return JsonResponse({
#             'total_price': total_price,
#             'discount': discount,
#             'delivery_charges': delivery_charges,
#             'total_amount': total_amount,
#         })


@login_required
def update_or_delete_cart_item(request):
    if request.method == 'POST':
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in to update the cart.'}, status=403)

        # Get the cart item ID and action from the POST request
        cart_item_id = request.POST.get('cart_item_id')
        action = request.POST.get('action')  # Action: either 'update' or 'delete'

        # Get the cart item and ensure it belongs to the current user's cart
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        cart = cart_item.cart

        if action == 'update':
            print('update')
            # Update quantity
            try:
                new_quantity = int(request.POST.get('quantity'))
                cart_item.quantity = new_quantity
                cart_item.save()
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid quantity provided.'}, status=400)

        elif action == 'delete':
            print('here')
            # Delete the cart item
            cart_item.delete()
        else:
            return JsonResponse({'error': 'Invalid action provided.'}, status=400)

        # Recalculate cart totals after update/delete
        total_price = sum(item.product.sale_price * item.quantity for item in CartItem.objects.filter(cart=cart))
        discount = 0
        # if total_price > 1000:
        #     discount = 100  # Example discount logic
        delivery_charges = 100 if total_price < 500 else 0
        total_amount = total_price - discount + delivery_charges

        # Return updated cart data in JSON format
        return JsonResponse({
            'total_price': total_price,
            'discount': discount,
            'delivery_charges': delivery_charges,
            'total_amount': total_amount,
        })
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@login_required
def delete_cart_item(request):
    if request.method == 'POST':
        # Get cart item ID from the request
        cart_item_id = request.POST.get('cart_item_id')

        # Get the cart item and ensure it belongs to the current user's cart
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
        cart = cart_item.cart

        # Delete the cart item
        cart_item.delete()

        # Update the cart totals
        total_price = sum(item.product.sale_price * item.quantity for item in CartItem.objects.filter(cart=cart))

        # Optionally apply discount or delivery charges logic here
        discount = 100 if total_price > 1000 else 0
        delivery_charges = 100 if total_price < 500 else 0
        total_amount = total_price - discount + delivery_charges

        # Return updated cart totals as JSON response
        return JsonResponse({
            'total_price': total_price,
            'discount': discount,
            'delivery_charges': delivery_charges,
            'total_amount': total_amount
        })
    
    # If not POST request, return error or redirect
    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
@require_POST
def add_address(request):
    if request.method == 'POST':
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')

        # Save the new address
        address = Address.objects.create(
            user=request.user,
            street_address=street_address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country
        )
        addresses = Address.objects.filter(user=request.user)
        # Return a JSON response with the new address data
        return JsonResponse({
            'addresses' : True,
            'id': str(address.id),
            'street_address': address.street_address,
            'city': address.city,
            'state': address.state,
            'postal_code': address.postal_code,
            'country': address.country
        })
    


class ApplyCouponView(View):

    def post(self, request, *args, **kwargs):
        code = request.POST.get('code')  # Get the coupon code from the POST data
        total_price = float(request.POST.get('total_price'))  # Get total price from POST data
        delivery_charges = float(request.POST.get('delivery_charges'))  # Get delivery charges from POST data
        discount_amount = 0.00  # Initially no discount

        try:
            # Retrieve the coupon by code and ensure it's active
            coupon = get_object_or_404(Coupon, code=code, is_active=True)

            # Check if coupon is within valid date range
            if not (coupon.valid_from <= timezone.now() <= coupon.valid_until):
                return JsonResponse({'error': 'Coupon is expired'}, status=400)

            # Check if minimum spend requirement is met
            if coupon.minimum_spend and total_price < coupon.minimum_spend:
                return JsonResponse({'error': f'Minimum spend of ₹ {coupon.minimum_spend} is required'}, status=400)

            # Calculate the discount
            discount_amount = (coupon.discount_percentage / 100) * total_price
            if discount_amount > coupon.max_discount_amount:
                discount_amount = coupon.max_discount_amount

            # Calculate the new total price after applying the coupon
            new_total_price = total_price - discount_amount
            total_amount = new_total_price + delivery_charges

            return JsonResponse({
                'success': True,
                'new_total_price': round(new_total_price, 2),
                'discount_amount': round(discount_amount, 2),
                'total_amount': round(total_amount, 2)
            })

        except Coupon.DoesNotExist:
            return JsonResponse({'error': 'Invalid coupon code'}, status=400)




# @csrf_exempt  # CSRF exemption for simplicity in AJAX calls, ensure security in production
@login_required
def place_order_ajax(request):
    if request.method == 'POST':
        try:
            user = request.user
            address_id = request.POST.get('address_id')
            total_amount = request.POST.get('total_amount')
            address = get_object_or_404(Address, id=address_id, user=user)

            # Get user details from the form
            full_name = request.POST.get('full_name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone_number')

            # Get the cart and calculate the total amount
            cart = Cart.objects.get(user=user)
            cart_items = CartItem.objects.filter(cart=cart)
            # total_amount = sum(item.product.sale_price * item.quantity for item in cart_items)
            # delivery_charges = 50.00  # Example delivery charges
            # total_amount += delivery_charges
            if not cart_items.exists():
                return JsonResponse({'error': 'Your cart is empty.'}, status=400)
            # Create the order
            order = Order.objects.create(
                user=user,
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                street_address=address.street_address,
                city=address.city,
                state=address.state,
                pin_code=address.postal_code,
                country=address.country,
                total_amount=total_amount,
                store= cart_items[0].product.store,
                delivery_status = 'Pending',
                order_status='Pending',
                payment_status='Pending'
            )

            # Create order items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.sale_price
                )

            # Clear the cart after order is placed
            cart_items.delete()

            return JsonResponse({'success': True, 'message': 'Order placed successfully!', 'order_id': str(order.id)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)



@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Prepare email content for customer
    subject = f'Order Confirmation - Order #{order.id}'
    email_template_name = 'emails/order_confirmation.html'
    customer_support = settings.SUPPORT_EMAIL
    email_content = render_to_string(email_template_name, {'order': order, 'customer_support': customer_support})

    # Send email to customer
    send_mail(
        subject,
        '',  # Plain text version (can be left empty or set to None)
        settings.DEFAULT_FROM_EMAIL,  # Replace with your email
        [request.user.email],
        fail_silently=False,
        html_message=email_content  # HTML version
    )

    # Prepare email content for admin/store owner
    admin_subject = f'New Order Notification - Order #{order.id}'
    admin_email_template_name = 'emails/new_order_notification.html'
    admin_email_content = render_to_string(admin_email_template_name, {'order': order})
    # Send email to admin and store owner
    send_mail(
        admin_subject,
        '',  # Plain text version (can be left empty or set to None)
        settings.DEFAULT_FROM_EMAIL,  # Replace with your email
        [settings.ADMIN_EMAIL],  # List of recipients
        fail_silently=False,
        html_message=admin_email_content  # HTML version
    )

    # Check if the store and owner's email are available
    if order.store and order.store.owner_email:
        store_owner_email = order.store.owner_email

        # Send email to store owner
        send_mail(
            admin_subject,
            '',  # Plain text version (can be left empty or set to None)
            settings.DEFAULT_FROM_EMAIL,  # Replace with your email
            [store_owner_email],
            fail_silently=False,
            html_message=admin_email_content  # HTML version
        )

    return render(request, 'order_confirmation.html', {'order': order})












#for previous orders
class OrderDetailView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

# My Account Page View
class MyAccountPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(user=user)
        addresses = Address.objects.filter(user=user)

        user_serializer = UserSerializer(user)
        order_serializer = OrderSerializer(orders, many=True)
        address_serializer = AddressSerializer(addresses, many=True)

        data = {
            'user': user_serializer.data,
            'orders': order_serializer.data,
            'addresses': address_serializer.data,
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user = request.user
        user_serializer = UserSerializer(user, data=request.data, partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    pass

account_activation_token = EmailVerificationTokenGenerator()


# class SignupView(APIView):
#     permission_classes = [AllowAny]
    
#     @csrf_exempt
#     def post(self, request, *args, **kwargs):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             # Assign user to a specific group based on request data
#             group_name = request.data.get('group')
#             if group_name:
#                 try:
#                     group = Group.objects.get(name=group_name)
#                     user.groups.add(group)
#                 except Group.DoesNotExist:
#                     return Response({"error": "Invalid group name."}, status=status.HTTP_400_BAD_REQUEST)
#             # Send email verification link
#             self.send_verification_email(user, request)
#             return Response({"message": "User created successfully! Please verify your email to activate your account."}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def send_verification_email(self, user, request):
#         token = account_activation_token.make_token(user)
#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         activation_link = request.build_absolute_uri(
#             reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
#         )
#         subject = 'Activate Your Account'
#         message = f'Hi {user.username},\n\nPlease click the link below to verify your email and activate your account:\n\n{activation_link}\n\nThank you!'
#         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


# class VerifyEmailView(APIView):
#     def get(self, request, uidb64, token, *args, **kwargs):
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#             user = None

#         if user is not None and account_activation_token.check_token(user, token):
#             user.is_active = True
#             user.save()
#             return Response({"message": "Email verified successfully!"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "Invalid token or user does not exist."}, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate Password Match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'signup.html')

        # Create user
        user = User.objects.create_user(
            username=email,  # Assuming username is the same as email in your model
            email=email,
            phone_number=phone_number,
            first_name=full_name.split()[0],  # You can handle full name better here
            last_name=" ".join(full_name.split()[1:]),  # Handle if there is more than one name part
            password=password,
            is_active=False  # Initially, the user is inactive until they verify their email
        )

        # Add the user to the 'Customer' group
        customer_group, created = Group.objects.get_or_create(name='Customer')
        user.groups.add(customer_group)

        # Generate email verification token
        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})

        full_link = f'http://{current_site.domain}{verification_link}'
        message = render_to_string('email_verification.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
            'verification_link': full_link
        })
        email_message = EmailMultiAlternatives(
        mail_subject, message, settings.DEFAULT_FROM_EMAIL, [email]
        )
    
        # Add HTML content
        email_message.attach_alternative(message, "text/html")
        
        # Send the email
        email_message.send()

        messages.success(request, 'Please confirm your email to complete registration.')
        return redirect('login')  # Redirect to login after signup
    else:
        return render(request, 'signup.html')


def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated successfully!')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return render(request, 'activation_invalid.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate the user using email and password
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # If authentication is successful, log the user in
            login(request, user)
            # Get the 'next' parameter from the query string
            next_url = request.GET.get('next')
            print(next_url)
            # Ensure the URL is safe (prevents open redirect vulnerabilities)
            # if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            #     return redirect(next_url)
            if next_url:
                return redirect(next_url)
            else:
                print('home page redirect')
                return redirect('landing_page')
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')



@login_required  # Ensures only authenticated users can log out
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout



class PasswordResetView(FormView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    from_email = settings.DEFAULT_FROM_EMAIL

    def form_valid(self, form):
        email = form.cleaned_data['email']
        associated_users = User.objects.filter(email=email)

        if associated_users.exists():
            opts = {
                'use_https': self.request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': self.from_email,
                'email_template_name': self.email_template_name,
                'subject_template_name': self.subject_template_name,
                'request': self.request,
            }
            form.save(**opts)

        return super().form_valid(form)



@login_required
def edit_account(request):
    user = request.user

    # Get the user's group (role)
    user_groups = user.groups.all()
    user_role = user_groups[0].name if user_groups.exists() else 'No Role Assigned'

    if request.method == 'POST':
        # Get the submitted data
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Validate data (you can add more validation logic here)
        if not email or not phone_number or not first_name or not last_name:
            messages.error(request, 'All fields are required.')
            return render(request, 'myaccount.html', {'user': user, 'user_role': user_role})

        try:
            # Update user details
            user.email = email
            user.phone_number = phone_number
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, 'Your account details were updated successfully!')
            return redirect('edit_account')
        
        except IntegrityError:
            # Handle the duplicate email error
            messages.error(request, 'This email is already registered with another account.')
            return render(request, 'myaccount.html', {'user': user, 'user_role': user_role})

    return render(request, 'myaccount.html', {'user': user, 'user_role': user_role})











# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]  # Ensures only authenticated users can log out

#     def post(self, request):
#         logout(request)
#         return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    
# class PasswordResetView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         if not email:
#             return Response({"email": "This field is required."}, status=status.HTTP_400_BAD_REQUEST)

#         form = PasswordResetForm(data=request.data)
#         if form.is_valid():
#             opts = {
#                 'use_https': request.is_secure(),
#                 'token_generator': default_token_generator,
#                 'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
#                 'email_template_name': 'registration/password_reset_email.html',
#                 'subject_template_name': 'registration/password_reset_subject.txt',
#                 'request': request,
#                 'html_email_template_name': 'registration/password_reset_email.html',
#             }
#             form.save(**opts)
#             return Response({"detail": "Password reset e-mail has been sent."}, status=status.HTTP_200_OK)

#         return Response({"detail": "Invalid email"}, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
        
#         user = authenticate(request, email=email, password=password)
        
#         if user is not None:
#             login(request, user)
#             return Response({"message": "Login successful!"}, status=status.HTTP_200_OK)
#         else:
#             return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)
        






class ProductListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProductSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Role-based Dashboard Views
class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Welcome, Admin!"})

class ManagerDashboardView(APIView):
    permission_classes = [IsManagerUser]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Welcome, Manager!"})

class StaffDashboardView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, *args, **kwargs):
        return Response({"detail": "Welcome, Staff!"})


#done
#for media page need to check once... for admin view only
class MediaPageView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)


    def get(self, request, *args, **kwargs):
        # Retrieve all products and their main images
        products = Product.objects.all()
        data = []

        for product in products:
            product_data = {
                'product_id': product.id,
                'product_name': product.name,
                'product_url': reverse('product_detail', kwargs={'slug': product.slug}),
                'image_url': product.image.url if product.image else None,
                'gallery_images': [{'image_url': img.image.url} for img in product.images.all()]
            }
            data.append(product_data)

        return Response(data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # Check if the request is for a main product image or a gallery image
        if 'product_id' in request.data:
            try:
                product = Product.objects.get(id=request.data['product_id'])
                
                # Handling main product image upload
                if 'image' in request.FILES:
                    product.image = request.FILES.get('image')
                    product.save()

                    response_data = {
                        'product_id': product.id,
                        'product_url': reverse('product_detail', kwargs={'slug': product.slug}),
                        'image_url': product.image.url
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    # Handling gallery image upload
                    image = ProductImage.objects.create(
                        product=product,
                        image=request.FILES.get('image')
                    )
                    
                    response_data = {
                        'product_id': product.id,
                        'product_url': reverse('product_detail', kwargs={'slug': product.slug}),
                        'image_url': image.image.url
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
            
            except Product.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid request."}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        image_ids = request.data.get('image_ids', [])
        if not image_ids:
            return Response({"error": "No image IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_images = []
        for image_id in image_ids:
            try:
                image = ProductImage.objects.get(id=image_id)
                deleted_images.append(image.image.url)
                image.delete()
            except ProductImage.DoesNotExist:
                continue

        if deleted_images:
            return Response({"message": "Images deleted successfully.", "deleted_images": deleted_images}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No images were deleted. Please check the provided IDs."}, status=status.HTTP_400_BAD_REQUEST)


#done
class BannerView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, *args, **kwargs):
        # Banner.objects.all().delete()
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        banner_id = kwargs.get('pk')
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            return Response({"error": "Banner not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BannerSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        banner_id = kwargs.get('pk')
        try:
            banner = Banner.objects.get(id=banner_id)
            banner.delete()
            return Response({"message": "Banner deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Banner.DoesNotExist:
            return Response({"error": "Banner not found."}, status=status.HTTP_404_NOT_FOUND)

#users list done
#Customer_List view 
class CustomerListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        customers = User.objects.filter(groups__name='Customer')
        print(customers)
        serializer = UserSerializer(customers, many=True)
        return Response(serializer.data)

def dash_customer(request):
    return render(request,'test.html')

#done
#coupons page
class CouponListView(APIView):
    def get(self, request, format=None):
        coupons = Coupon.objects.all()
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponDetailView(APIView):
    def get(self, request, pk, format=None):
        coupon = Coupon.objects.get(pk=pk)
        serializer = CouponSerializer(coupon)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        coupon = Coupon.objects.get(pk=pk)
        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        coupon = Coupon.objects.get(pk=pk)
        coupon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


#for apply coupon button for user (cart page or checkout page)
# class ApplyCouponView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         coupon_code = request.data.get('coupon_code')
#         cart = Cart.objects.get(user=request.user)
#         success, message = cart.apply_coupon(coupon_code)
#         if success:
#             return Response({"message": message})
#         else:
#             return Response({"error": message}, status=400)
        

#done
# for vendor page
class VendorListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    parser_classes = (MultiPartParser, FormParser)
#done

class VendorDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]

    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = 'id'
    parser_classes = (MultiPartParser, FormParser)
#done

# for category page
#done
class CategoryListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser)

#done
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (MultiPartParser, FormParser)

# for brand page
#done
class BrandListView(generics.ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    parser_classes = (MultiPartParser, FormParser)  # Include these if handling image uploads

#done
class BrandDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    lookup_field = 'id'

#order create for checkout 
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#order update view backend
class OrderUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
        except Order.DoesNotExist:
            return Response({'message': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        order_status = request.data.get('order_status')
        if order_status:
            order.order_status = order_status
            order.save()
            return Response({'message': 'Order status updated successfully.'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

#order list view backend    
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


#return request list for user and admin both
class ReturnRequestListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    queryset = ReturnRequest.objects.all()
    serializer_class = ReturnRequestSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return ReturnRequest.objects.all()
        return ReturnRequest.objects.filter(order_item__order__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure the order item belongs to the user
        if serializer.validated_data['order_item'].order.user != self.request.user:
            raise serializers.ValidationError('You cannot create a return request for this order item.')
        serializer.save()
#for specific admin to update request
class ReturnRequestUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            return_request = ReturnRequest.objects.get(pk=pk)
        except ReturnRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        status = request.data.get('status')
        if status in ['approved', 'rejected']:
            return_request.status = status
            return_request.save()
            return Response({'message': 'Return request updated.'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)

#ecommerce dashboard for both vendor and admin
class DashboardStatisticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        if user.is_staff:
            # Admin: See all statistics including commissions
            total_sales = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            total_orders = Order.objects.count()
            total_products = Product.objects.count()
            total_users = User.objects.count()

            # Calculate total commission for all stores
            total_commission = Store.objects.aggregate(
                total_commission=Sum(F('orders__total_amount') * F('commission_rate') / 100)
            )['total_commission'] or 0

            recent_orders = Order.objects.order_by('-placed_at')[:5].values('id', 'total_amount', 'placed_at')
            top_selling_products = Product.objects.annotate(total_sold=Sum('order_items__quantity')).order_by('-total_sold')[:5].values('name', 'total_sold')

        elif user.groups.filter(name='Brand').exists():
            # Brand: Calculate commission for products under their brand
            brands = Brand.objects.all()  # Assuming the Brand model has an owner field #change from .filter(owner=user)
            total_sales = Order.objects.filter(order_items__product__brand__in=brands).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            total_orders = Order.objects.filter(order_items__product__brand__in=brands).count()
            total_products = Product.objects.filter(brand__in=brands).count()

            # Calculate total commission for the brand's products
            total_commission = brands.aggregate(
                total_commission=Sum(F('products__order_items__order__total_amount') * F('products__store__commission_rate') / 100)
            )['total_commission'] or 0

            recent_orders = Order.objects.filter(order_items__product__brand__in=brands).order_by('-placed_at')[:5].values('id', 'total_amount', 'placed_at')
            top_selling_products = Product.objects.filter(brand__in=brands).annotate(total_sold=Sum('order_items__quantity')).order_by('-total_sold')[:5].values('name', 'total_sold')

        else:
            # Vendor: See statistics specific to their store
            # stores = Store.objects.filter(owner=user)
            stores = Store.objects.all() #change from .filter
            total_sales = Order.objects.filter(store__in=stores).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            total_orders = Order.objects.filter(store__in=stores).count()
            total_products = Product.objects.filter(store__in=stores).count()

            # Calculate total commission for the vendor's store
            total_commission = stores.aggregate(
                total_commission=Sum(F('orders__total_amount') * F('commission_rate') / 100)
            )['total_commission'] or 0

            recent_orders = Order.objects.filter(store__in=stores).order_by('-placed_at')[:5].values('id', 'total_amount', 'placed_at')
            top_selling_products = Product.objects.filter(store__in=stores).annotate(total_sold=Sum('order_items__quantity')).order_by('-total_sold')[:5].values('name', 'total_sold')

        data = {
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_products': total_products,
            'total_users': total_users if user.is_staff else None,  # Only for admins
            'total_commission': total_commission,
            'recent_orders': list(recent_orders),
            'top_selling_products': list(top_selling_products),
        }

        serializer = StatisticsSerializer(data)
        return Response(serializer.data)
    
#inventory sync page
class VendorInventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if the user is a vendor and has access to a store
        try:
            store = Store.objects.get(owner=user)
        except Store.DoesNotExist:
            return Response({"error": "No store found for this vendor."}, status=404)

        # Handle different inventory software integrations
        inventory_software = store.inventory_software

        if inventory_software == 'manual_excel':
            # Handle manual Excel upload
            return Response({"message": "Please upload an Excel file to update inventory."}, status=200)

        elif inventory_software == 'software_a':
            # Fetch inventory data from Software A's API
            inventory_data = self.fetch_inventory_data_software_a(store)
        
        elif inventory_software == 'software_b':
            # Fetch inventory data from Software B's API
            inventory_data = self.fetch_inventory_data_software_b(store)

        # Add more elif blocks for additional software integrations as needed

        else:
            return Response({"error": "Unsupported inventory software."}, status=400)

        if inventory_data is None:
            return Response({"error": "Failed to fetch inventory data."}, status=500)

        # Serialize the inventory data
        serializer = InventorySerializer(inventory_data, many=True)
        return Response(serializer.data, status=200)

    def fetch_inventory_data_software_a(self, store):
        api_url = "https://api.softwarea.com/inventory"
        headers = {
            "Authorization": f"Bearer {store.api_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(api_url, headers=headers, params={"store_id": store.id})

        if response.status_code == 200:
            return response.json()
        return None

    def fetch_inventory_data_software_b(self, store):
        api_url = "https://api.softwareb.com/inventory"
        headers = {
            "Authorization": f"Bearer {store.api_token}",
            "Content-Type": "application/json",
        }

        response = requests.get(api_url, headers=headers, params={"store_id": store.id})

        if response.status_code == 200:
            return response.json()
        return None

    def post(self, request):
        user = request.user

        # Check if the user is a vendor and has access to a store
        try:
            store = Store.objects.get(owner=user)
        except Store.DoesNotExist:
            return Response({"error": "No store found for this vendor."}, status=404)

        if store.inventory_software == 'manual_excel':
            # Handle manual Excel upload
            excel_file = request.FILES.get('file')

            if not excel_file:
                return Response({"error": "No file uploaded."}, status=400)

            # Save the uploaded file temporarily
            file_name = default_storage.save(f"temp/{excel_file.name}", ContentFile(excel_file.read()))
            file_path = default_storage.path(file_name)

            # Read the Excel file using pandas
            try:
                df = pd.read_excel(file_path)
                # Process the DataFrame as needed to update your inventory
                self.process_excel_data(store, df)
            except Exception as e:
                return Response({"error": str(e)}, status=500)
            finally:
                # Clean up the temporary file
                default_storage.delete(file_path)

            return Response({"message": "Inventory updated successfully."}, status=200)

        else:
            return Response({"error": "Manual Excel upload is not enabled for this store."}, status=400)

    def process_excel_data(self, store, df):
        # Example processing: Assuming the Excel file has columns 'product_id' and 'quantity'
        for index, row in df.iterrows():
            try:
                product = Product.objects.get(id=row['product_id'], store=store)
                inventory, created = Inventory.objects.get_or_create(product=product, store=store)
                inventory.quantity = row['quantity']
                inventory.save()
            except Product.DoesNotExist:
                # Handle the case where a product doesn't exist
                pass

#delivery partner integration
class ShippingIntegrationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        user = request.user

        # Get the order
        try:
            order = Order.objects.get(id=order_id, store__owner=user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or you do not have permission to access it."}, status=404)

        # Send order details to the shipping partner
        shipping_data = self.send_order_to_shipping_partner(order)

        if not shipping_data:
            return Response({"error": "Failed to send order details to shipping partner."}, status=500)

        # Update the order with the tracking ID
        order.tracking_id = shipping_data.get('tracking_id')
        order.delivery_status = shipping_data.get('status', 'shipped')
        order.save()

        return Response({"message": "Order details sent to shipping partner successfully."}, status=200)

    def get(self, request, order_id):
        user = request.user

        # Get the order
        try:
            order = Order.objects.get(id=order_id, store__owner=user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or you do not have permission to access it."}, status=404)

        # Fetch the delivery status from the shipping partner
        delivery_status = self.fetch_delivery_status(order)

        if not delivery_status:
            return Response({"error": "Failed to fetch delivery status from shipping partner."}, status=500)

        # Update the order with the latest delivery status
        order.delivery_status = delivery_status
        order.save()

        return Response({"message": "Delivery status updated successfully.", "delivery_status": delivery_status}, status=200)

    def send_order_to_shipping_partner(self, order):
        # Shipping partner API URL and credentials (Assuming they are stored in the Store model)
        api_url = "https://shippingpartner.com/api/orders"
        store = order.store

        headers = {
            "Authorization": f"Bearer {store.api_token}",
            "Content-Type": "application/json",
        }

        # Prepare the order data to send
        order_data = {
            "order_id": str(order.id),
            "recipient_name": order.user.get_full_name(),
            "recipient_address": order.user.profile.address,  # Assuming the User model has a related Profile with an address field
            "recipient_phone": order.user.profile.phone,  # Assuming the User model has a related Profile with a phone field
            "order_total": str(order.total_amount),
            "payment_method": order.payment_method,  # Assuming Order model has a payment_method field
            "payment_status": order.payment_status,  # Assuming Order model has a payment_status field
            "items": [
                {
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "price": str(item.price),
                }
                for item in order.order_items.all()
            ],
            "shipping_instructions": "Leave at the front door if no one is home.",  # Example additional data
        }

        # Make the API request
        response = requests.post(api_url, json=order_data, headers=headers)

        if response.status_code == 201:  # Assuming 201 means the order was successfully created
            return response.json()  # Assuming the response contains a tracking_id and status
        return None

    def fetch_delivery_status(self, order):
        # Shipping partner API URL to fetch delivery status
        api_url = f"https://shippingpartner.com/api/orders/{order.tracking_id}/status"
        store = order.store

        headers = {
            "Authorization": f"Bearer {store.api_token}",
            "Content-Type": "application/json",
        }

        # Make the API request
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return response.json().get('status')  # Assuming the response contains the delivery status
        return None
    
# class CheckoutPageView(APIView):
#     permission_classes = [IsAuthenticated]

    

#     def post(self, request, *args, **kwargs):
#         try:
#             cart = Cart.objects.get(user=request.user)
#             if not cart.cart_items.exists():
#                 return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)
            
#             # Calculate total price
#             total_price = cart.cart_items.aggregate(total=Sum('product__price'))['total']

#             order = Order.objects.create(
#                 user=request.user,
#                 store=request.data.get('store'),
#                 total_price=total_price,
#                 status='pending'
#             )
            
#             for item in cart.cart_items.all():
#                 OrderItem.objects.create(
#                     order=order,
#                     product=item.product,
#                     quantity=item.quantity,
#                     price=item.product.price
#                 )
            
#             # Clear the cart after order placement
#             cart.cart_items.all().delete()
#             return Response({'detail': 'Order placed successfully.'}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)




def home(request):
    return render(request, 'index.html')

def category(request):
    return render(request, 'category_base.html')

def store(request):
    return render(request, 'store_base.html')








#dashboard views
@login_required
def base_dash(request):
    return render(request, 'dashboard/base_dash.html')


@login_required
def customer_profile(request):
    user = request.user

    # Get the user's group (role)
    user_groups = user.groups.all()
    user_role = user_groups[0].name if user_groups.exists() else 'No Role Assigned'

    if request.method == 'POST':
        # Get the submitted data
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Validate data (you can add more validation logic here)
        if not email or not phone_number or not first_name or not last_name:
            messages.error(request, 'All fields are required.')
            return render(request, 'dashboard/customer_profile.html', {'user': user, 'user_role': user_role})

        try:
            # Update user details
            user.email = email
            user.phone_number = phone_number
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, 'Your account details were updated successfully!')
            return redirect('customer_profile')
        
        except IntegrityError:
            # Handle the duplicate email error
            messages.error(request, 'This email is already registered with another account.')
            return render(request, 'dashboard/customer_profile.html', {'user': user, 'user_role': user_role})

    return render(request, 'dashboard/customer_profile.html', {'user': user, 'user_role': user_role})


@login_required
def customer_past_orders(request):
    # Check if the logged-in user belongs to the 'Customer' group
        # Fetch all orders for the logged-in customer
        orders = Order.objects.filter(user=request.user).order_by('-placed_at')

        context = {
            'orders': orders,
        }
        return render(request, 'dashboard/customer_past_orders.html', context)
  
    

@login_required
def customer_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'dashboard/customer_wishlist.html', {'wishlist': wishlist})
    

@login_required
def create_return_request(request, order_item_id):
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__user=request.user)

    # Check if a return request already exists
    existing_request = ReturnRequest.objects.filter(order_item=order_item).first()
    if existing_request:
        return JsonResponse({'success': False, 'message': 'Return request already exists.'})

    if request.method == 'POST':
        reason = request.POST.get('reason')
        if reason:
            # Create a new return request
            return_request = ReturnRequest.objects.create(
                order_item=order_item,
                reason=reason
            )
            return JsonResponse({'success': True, 'message': 'Return request created successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Please provide a reason for return.'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def customer_return_requests(request):
    # Fetch return requests for the logged-in user's orders
    return_requests = ReturnRequest.objects.filter(order_item__order__user=request.user)

    context = {
        'return_requests': return_requests,
    }
    return render(request, 'dashboard/customer_return_requests.html', context)