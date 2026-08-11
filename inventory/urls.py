from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
]