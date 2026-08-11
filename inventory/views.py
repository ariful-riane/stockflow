from django.shortcuts import redirect, render

from .forms import ProductForm
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, "inventory/product_list.html", 
                  {"products": products})

def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory:product_list")
    else:
        form = ProductForm()
    return render(request, 
                    "inventory/product_form.html",
                    {"form": form}
                )
