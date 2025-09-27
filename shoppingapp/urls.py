from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('bulk_order/', views.bulk_order, name='bulk_order'),
    path('bulk_order/<int:pk>/', views.bulk_order, name='bulk_order_product'),
    path('customer-service/', views.customer_service, name='customer_service'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:cart_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)