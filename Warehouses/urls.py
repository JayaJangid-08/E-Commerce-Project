from django.urls import path
from . import views

urlpatterns = [
    path('assignment/', views.assign_warehouse_to_staff, name='assigned-warehouse-to-staff'),
    path('', views.warehouse_list, name='warehouse-list'),
    path('<int:warehouse_id>/', views.warehouse_detail, name='warehouse-detail'),
    path('inventories/', views.inventory_list, name='inventory-list'),
    path('inventory/<int:inventory_id>/', views.inventory_detail, name='inventory-detail'), 
    # Inventory by warehouse
    path('<int:warehouse_id>/inventory/', views.inventory_of_single_warehouse, name='inventory-of-single-warehouse'),
    path('stock-movements/', views.stock_movement_list, name='stock-movement-list'),
    path('stock-movements/<int:stock_movement_id>/', views.stock_movement_detail, name='stock-movement-detail'),
    # Stock movements by warehouse
    path('<int:warehouse_id>/stock-movements/',views.stock_history_of_warehouse, name='stock-history-of-warehouse'),
    # Stock actions
    path('<int:warehouse_id>/inventory/add-stock/', views.add_stock_in_warehouse, name='add-stock-in-warehouse'),
    path('<int:warehouse_id>/inventory/remove-stock/', views.remove_stock_from_warehouse, name='remove-stock-from-warehouse'),
]
