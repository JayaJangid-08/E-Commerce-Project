from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_list, name= 'cart-list'),
    path('cart/add/', views.add_product, name='add-product'),
    path('cart/<int:item_id>/', views.cart_detail, name= 'cart-detail'),
    path('cart/<int:item_id>/remove/', views.remove_product, name='remove-product'),
]