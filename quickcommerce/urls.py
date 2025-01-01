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
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), name='password_reset_confirm'),
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
    # path('myaccount/', edit_account, name='edit_account'),


#dashboard urls
    path('dashboard/home/',base_dash, name='base_dash'),
    path('dashboard/orders/', orders_page, name='orders_page'),
    path('dashboard/orders/fetch', ajax_orders, name='ajax_orders'),
    path('dashboard/orders/<uuid:order_id>/details/', order_details, name='order_details'),
    path('dashboard/orders/<uuid:order_id>/update_status/', update_order_status, name='update_order_status'),
    path('dashboard/new-pending-orders/', get_new_pending_orders, name='get_new_pending_orders'),
    path('dashboard/return-requests/', admin_return_requests, name='admin_return_requests'),
    path('dashboard/user/profile/',admin_profile, name='admin_profile'),
    path('dashboard/analytics/',analytics_view, name='analytics_view'),
    # path('dashboard/store/<uuid:store_id>/update/',update_store_image, name='update_store_image'),




    path('customer/profile/',customer_profile, name='customer_profile'),
    path('customer/orders/',customer_past_orders, name='customer_past_orders'),
    path('customer/wishlist/',customer_wishlist, name='customer_wishlist'),
    path('returns/request/<uuid:order_item_id>/', create_return_request, name='create_return_request'),
    path('customer/returns/',customer_return_requests, name='customer_return_requests'),
    path('customer/saved-addresses/',customer_saved_addresses, name='customer_saved_addresses'),
    path('customer/delete-address/', delete_address, name='delete_address'),  # URL for the AJAX request



    # path('dashboard/products/',products_dash, name='products_dash'),
    path('dashboard/products/', list_products, name='products_dash'),
    path('dashboard/products/bulk/add/', add_bulk_products , name='add_bulk_products'),

    # path('dashboard/products/add/', add_or_edit_product, name='add_product'),
    # path('dashboard/products/edit/<uuid:product_id>/', add_or_edit_product, name='edit_product'),
    path('dashboard/delete_product/<uuid:product_id>/', delete_product, name='delete_product'),

    # path('dashboard/user/account/',user_dash, name='user_dash'),
    # path('wizapp/fetch-inventory/', fetch_inventory_from_wizapp, name='fetch_inventory_wizapp'),
    
    #logistics (shadowfax hyperlocal)
    path('place-order/', place_order, name='place_order'),
    path('order/status/<int:sfx_order_id>/', get_order_status, name='get_order_status'),
    path('order/cancel/<int:sfx_order_id>/', cancel_order, name='cancel_order'),

    #logistics (shadowfax flash)
    path("order/workflow/", sfx_flash_order_workflow, name="order_workflow"),  # Handles steps 1-3
    path("order/cancel/", sfx_cancel_order, name="cancel_order"),       # Cancel order
    path("order/track/<int:order_id>/", sfx_track_order, name="track_order"),  # Track order


    path('autocomplete/', ola_autocomplete, name='ola_autocomplete'),
    path('reverse-geocode/', ola_reverse_geocode, name='ola_reverse_geocode'),

    path('about-us/', about_us_page, name='about_us'),
    path('contact-us/', contact_us_page, name='contact_us'),
    path('terms-conditions/', terms_conditions, name='terms_conditions'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('return-refund-policy/', return_refund, name='return_refund'),
    path('shipping-policy/', shipping_policy, name='shipping_policy'),
    path('faq/', faq, name='faq'),
    path('payment/', initiate_payment, name='initiate_payment'),
    path('callback-phnpe/', phonepe_callback, name='phonepe_callback'),
    path('sfx/s2s-callback/', sfx_callback_view, name='sfx_callback_view'),
    path("fetch-data/<int:mode>/", trigger_fetch, name="fetch_data"),
    path("wizapp_download_csv/<int:mode>/", wizapp_download_csv, name="wizapp_download_csv"),

    path("create/",create_dummy_products, name="create_dummy_products"),
    
    path("check-serviceability/",sfx_serviceability_check, name="sfx_serviceability_check"),
    
    path('trigger-inventory-sync/', trigger_inventory_sync, name='trigger_inventory_sync'),
    path('task-status/<str:task_id>/', check_task_status, name='check_task_status'),
    path('download/size_chart/', download_sizechart, name='download_sizechart'),

    # path("download-csv/", download_csv, name="download_csv"),
    path("upload-csv/", create_products_from_csv, name="upload_csv"),
    # Add other URL patterns here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# use for passing location coordinates rest normal0
# GET /api/landing/?latitude=37.7749&longitude=-122.4194

#to create auth tokens and include this token in headers from react while making a get request to any api
# python manage.py drf_create_token <username>


#pass category id or brand id for filtering their views (also location coordinates or saved_address_id)

