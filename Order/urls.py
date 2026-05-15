from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order-list'),
    path('place/', views.place_order, name='place-order'),
    path('<int:order_id>/', views.order_detail, name='order-detail'),
    path('cancel-order-item/<int:item_id>/',views.cancel_order_item, name='cancel-order'),
    path('<int:order_id>/status/',views.update_order_status, name='update-order-status'),
    path('item/<int:item_id>/status/',views.update_item_status, name='update-item-status'),
]