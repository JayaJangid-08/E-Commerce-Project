from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:product_id>/reviews/', views.review_list, name='review-list'),
    path('<int:review_id>/', views.review_detail, name='review-detail'),
]

