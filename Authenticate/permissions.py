from .models import User
from rest_framework import permissions

class IsAuthenticatedBase(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'admin'

class IsVendor(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'vendor'

class IsCustomer(IsAuthenticatedBase):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == 'customer'

class IsVendorOrAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
            return super().has_permission(request, view) and (request.user.role in ['admin', 'vendor'])

    def has_object_permission(self, request, view, obj):
        return super().has_permission(request, view)and(
            request.user.role == 'admin' or
            obj.vendor == request.user
            )

