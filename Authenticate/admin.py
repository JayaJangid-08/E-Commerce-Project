from django.contrib import admin
from .models import User , Address , Role

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username','email','get_roles']
    def get_roles(self, obj):
        roles = obj.roles.values_list('name', flat=True)
        return ", ".join(roles) if roles else "-"

    get_roles.short_description = "Roles"


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','city','state']

admin.site.register(User , UserAdmin)
admin.site.register(Address , AddressAdmin)
admin.site.register(Role)
