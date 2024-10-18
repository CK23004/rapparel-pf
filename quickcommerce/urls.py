from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [

    path('home', home, name='home'),
    path('category', category, name='category'),

 path('store', store, name='store'),

    #frontend urls for user
    # path('api/landing/', LandingPageView.as_view(), name='landing-page'),
    # path('api/cart/', CartPageView.as_view(), name='cart-page'),
    # path('api/cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    # path('api/checkout/', CheckoutPageView.as_view(), name='checkout-page'),
    path('order/<uuid:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    # path('signup/', SignupView.as_view(), name='signup'),
    # path('login/', LoginView.as_view(), name='login'),
    # path('logout/', LogoutView.as_view(), name='logout'),
    # path('password-reset/', PasswordResetView.as_view(), name='password-reset'),

    # path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify_email'),
    # path('api/wishlist/', WishlistToggleView.as_view(), name='wishlist-page'),
    path('api/my-account/', MyAccountPageView.as_view(), name='my-account-page'),
    # path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('api/stores-by-category/', CategoryStoresView.as_view(), name='stores-by-category'),
    path('api/stores-by-brand/', BrandStoresView.as_view(), name='stores-by-brand'),
    path('store/<slug:store_slug>/', StoreDetailView.as_view(), name='store_detail'), #fake
    # path('product/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),

    #backend urls for dashboard

    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/signup/', SignupView.as_view(), name='signup'),
    # path('api/admin-dashboard/', AdminDashboardView.as_view(), name='admin_dashboard'),
    # path('api/manager-dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    # path('api/staff-dashboard/', StaffDashboardView.as_view(), name='staff_dashboard'),
    # path('api/media/', MediaPageView.as_view(), name='media_list'),
    # path('api/banners/', BannerView.as_view(), name='banner_list'),
    # path('api/banners/<uuid:pk>/', BannerView.as_view(), name='banner_detail'),
    # path('cart/apply-coupon/', apply_coupon, name='apply-coupon'),

    # path('api/users/customers/', CustomerListView.as_view(), name='customer_list'),
    # path('products/', ProductListView.as_view(), name='product-list'),
    # path('products/<uuid:pk>/', ProductListView.as_view(), name='product-detail'),
    # path('coupons/', CouponListView.as_view(), name='coupon-list'),
    # path('coupons/<uuid:pk>/', CouponDetailView.as_view(), name='coupon-detail'),
    # path('api/vendor/', VendorListView.as_view(), name='vendor-list'),
    # path('api/vendor/<uuid:id>/', VendorDetailView.as_view(), name='vendor-detail'),

    # path('categories/', CategoryListView.as_view(), name='category-list'),
    # path('categories/<uuid:id>/', CategoryDetailView.as_view(), name='category-detail'),
    # path('brands/', BrandListView.as_view(), name='brand-list'),
    # path('brands/<uuid:id>/', BrandDetailView.as_view(), name='brand-detail'),

    # path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/<uuid:pk>/update/', OrderUpdateView.as_view(), name='order-update'),
    # path('return-requests/', ReturnRequestListView.as_view(), name='return-request-list'),
    # path('return-requests/<int:pk>/update/', ReturnRequestUpdateView.as_view(), name='return-request'),
    # path('dashboard/statistics/', DashboardStatisticsView.as_view(), name='dashboard-statistics'),
    # path('vendor/inventory/', VendorInventoryView.as_view(), name='vendor-inventory'),
    # path('vendor/orders/<uuid:order_id>/ship/', ShippingIntegrationView.as_view(), name='ship-order'),
    # path('vendor/orders/<uuid:order_id>/status/', ShippingIntegrationView.as_view(), name='fetch-delivery-status'),
    # path('dashboard/customers', dash_customer, name='dash_customer'),
    # path('wishlist/', WishlistToggleView.as_view(), name='wishlist-toggle'),




    #new urls

    path('signup/', signup_view, name='signup'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('accounts/login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', TemplateView.as_view(template_name="registration/password_reset_done.html"), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', TemplateView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', TemplateView.as_view(template_name="registration/password_reset_complete.html"), name='password_reset_complete'),
    path('', LandingPageView.as_view(), name='landing_page'),
    path('api/saved-addresses/', fetch_saved_addresses, name='fetch_saved_addresses'),
    path('store/<slug:store_slug>/', StoreDetailView.as_view(), name='store_detail'), #imp
    path('category/<slug:category_slug>/', CategoryStoresView.as_view(), name='category_stores'),
    path('brand/<slug:brand_slug>/', BrandStoresView.as_view(), name='brand_stores'),
    path('product/<slug:slug>/', product_detail_view, name='product_detail'),
    # path('wishlist/', view_wishlist, name='view_wishlist'),  # View the wishlist
    path('wishlist/add/<slug:product_slug>/', add_to_wishlist, name='add_to_wishlist'),  # Add to wishlist
    path('wishlist/remove/<slug:product_slug>/', remove_from_wishlist, name='remove_from_wishlist'),  # Remove from wishlist
    path('search/', search_products, name='search_products'),  # URL for product search
    path('add-to-cart/', AddToCartView.as_view(), name='add_to_cart'),  #for add to cart
    path('checkout/', CartCheckoutView.as_view(), name='cart_checkout'), #for cart and checkout page
    path('update-cart-item/', update_or_delete_cart_item, name='update_cart_item'),
    path('delete-cart-item/', delete_cart_item, name='delete_cart_item'),  
    path('add-address/', add_address, name='add_address'),
    path('apply-coupon/', ApplyCouponView.as_view(), name='apply_coupon'),
    path('place-order-ajax/', place_order_ajax, name='place_order_ajax'),
    path('order-confirmation/<uuid:order_id>/', order_confirmation, name='order_confirmation'),
    path('myaccount/', edit_account, name='edit_account'),


#dashboard urls
    path('dashboard/home/',base_dash, name='base_dash'),
    path('customer/profile/',customer_profile, name='customer_profile'),
    path('customer/orders/',customer_past_orders, name='customer_past_orders'),
    path('customer/wishlist/',customer_wishlist, name='customer_wishlist'),
    path('returns/request/<uuid:order_item_id>/', create_return_request, name='create_return_request'),
    path('customer/returns/', customer_return_requests, name='customer_return_requests'),














    # Add other URL patterns here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# use for passing location coordinates rest normal0
# GET /api/landing/?latitude=37.7749&longitude=-122.4194

#to create auth tokens and include this token in headers from react while making a get request to any api
# python manage.py drf_create_token <username>


#pass category id or brand id for filtering their views (also location coordinates or saved_address_id)

