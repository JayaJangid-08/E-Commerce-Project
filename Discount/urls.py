from django.urls import path
from . import views

urlpatterns = [
    path('coupon/', views.discount_list, name='discount-list'),
    path('coupon/<int:coupon_id>/', views.discount_detail, name='discount-detail')
]
