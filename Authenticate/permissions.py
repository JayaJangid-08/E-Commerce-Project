from .models import User
from rest_framework import permissions
from Warehouses.models import Warehouse


class IsAuthenticatedBase(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles.filter(name='admin').exists()


class IsVendor(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles.filter(name='vendor').exists()


class IsCustomer(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles.filter(name='customer').exists()


class IsVendorOrAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
            return super().has_permission(request, view) and (request.user.roles.filter(name__in = ['admin', 'vendor']).exists())

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and (
            request.user.roles.filter(name='admin').exists() or
            obj.vendor == request.user)


class IsDiscountOwnerOrAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
            return super().has_permission(request, view) and (request.user.roles.filter(name__in = ['admin', 'vendor']).exists())

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and(
            request.user.roles.filter(name='admin').exists()
            or obj.creator == request.user
        )


class IsReviewOwnerOrAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
            return super().has_permission(request, view) and (request.user.roles.filter(name__in = ['admin', 'customer']).exists())

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and(
            request.user.roles.filter(name='admin').exists()
            or obj.user == request.user
        )


class IsAdminOrOwner(IsAuthenticatedBase):
    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and (
            request.user.roles.filter(name='admin').exists() or
            obj.order.customer == request.user
        )


class IsAdminOrAssignedStaff(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and (request.user.roles.filter(name__in=['admin', 'staff']).exists())

    def has_object_permission(self, request, view, obj):
        # Admin can access everything
        if request.user.roles.filter(name='admin').exists():
            return True
        
        user_warehouses = Warehouse.objects.filter(staffwarehouse__staff=request.user)
        # If object itself is Warehouse
        if isinstance(obj, Warehouse):
            return obj in user_warehouses
        
        # If object has warehouse field
        if hasattr(obj, 'warehouse'):
            return obj.warehouse in user_warehouses
        return False

class IsCourier(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.roles.filter(name='courier').exists()
