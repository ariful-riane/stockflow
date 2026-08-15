from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path("", views.index, name="index"),

    path("overview/", views.overview, name="overview"),
    path("contact/", views.contact, name="contact"),

    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
]