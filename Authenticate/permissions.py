from .models import User
from rest_framework import permissions

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
            return super().has_permission(request, view) and (request.user.roles.filter(name__in = ['admin', 'vendor']).exists())

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view) and(
            request.user.roles.filter(name='admin').exists()
            or obj.user == request.user
        )

