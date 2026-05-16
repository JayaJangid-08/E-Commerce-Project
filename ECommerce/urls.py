"""
URL configuration for ECommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("""
        <html>
        <body style="background-color: black; color: white; text-align: center; padding: 50px;">
            <h1>Welcome to E-Commerce API!</h1>
        </body>
        </html>
    """)

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('auth/', include('Authenticate.urls')),
    path('warehouses/', include('Warehouses.urls')),
    path('products/', include('Products.urls')),
    path('carts/', include('Carts.urls')),
    path('orders/', include('Order.urls')),
    path('discount/', include('Discount.urls')),
    path('reviews/', include('Reviews.urls'))
]
