from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import ProtectedError, Q

from .forms import ProductForm
from .models import Product, Category

def index(request):
    return render(request, "inventory/index.html")

def product_list(request):
    products = Product.objects.select_related("category").all().order_by("name")
    categories = Category.objects.all().order_by("name")

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()

    selected_category_id = None

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(sku__icontains=search)
        )

    if category_id:
        try:
            selected_category_id = int(category_id)
     
        except ValueError:
            selected_category_id = None
        else:
            products = products.filter(category_id=selected_category_id)

    return render(request, "inventory/product_list.html", 
                  {
                      "products": products,
                      "search": search,
                      "categories": categories,
                      "selected_category_id": selected_category_id
                   }
                  )

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

def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("inventory:product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, 
                    "inventory/product_form.html",
                    {
                        "form": form,
                        "product": product,
                        "is_edit": True,
                    }
                )

def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        try:
            product.delete()
            return redirect("inventory:product_list")
        except ProtectedError:
            return render(request, "inventory/product_confirm_delete.html",
                          {
                              "product": product,
                              "cannot_delete": True,
                          }
                        )

    return render(request, "inventory/product_confirm_delete.html",
                  {"product": product},
                )