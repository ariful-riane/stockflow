from .forms import CustomUserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError, Q, F
from .services import apply_stock_movement
from .models import StockMovement

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage

from .forms import ContactForm, ProductForm, StockForm
from .models import Product, Category

def index(request):
    return render(request, "inventory/index.html")

def overview(request):
    return render(request, "inventory/overview.html")

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]

            email_message = EmailMessage(
                subject=f"Contact Form Submission from {name}",
                body=(
                    f"Name: {name}\n"
                    f"Email: {email}\n\n"
                    f"{message}"
                ),
                from_email=None,
                to=[settings.CONTACT_EMAIL],
                reply_to=[email],
            )
            email_message.send(using="default")

            messages.success(request, "Your message has been sent successfully.")
            return redirect("inventory:contact")
    else:
        form = ContactForm()
    return render(request, "inventory/contact.html", {"form": form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inventory:index')
    return auth_views.LoginView.as_view(template_name='registration/login.html')(request)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inventory:product_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})



@login_required
def product_list(request):
    products = Product.objects.filter(created_by=request.user).select_related("category").all().order_by("name")
    categories = Category.objects.all().order_by("name")

    search = request.GET.get("search", "").strip()
    category_id = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    selected_category_id = None

    if search:
        products = products.filter(
            Q(name__icontains=search) | Q(sku__icontains=search) | Q(id__icontains=search)
        )

    if category_id:
        try:
            selected_category_id = int(category_id)
     
        except ValueError:
            selected_category_id = None
        else:
            products = products.filter(category_id=selected_category_id)
    
    if status == "out":
        products = products.filter(quantity=0)
    elif status == "low":
        products = products.filter(quantity__gt=0, quantity__lte=F("minimum_stock"))
    elif status == "in":
        products = products.filter(quantity__gt=F("minimum_stock"))
    
    if min_price:
        try:
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    
    if max_price:
        try:
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass

    return render(request, "inventory/product_list.html", 
                  {
                      "products": products,
                      "search": search,
                      "categories": categories,
                      "selected_category_id": selected_category_id,
                      "status": status,
                      "min_price": min_price,
                      "max_price": max_price
                   }
                  )

@login_required
def product_create(request):
    if request.method == "POST":
        product = Product(created_by=request.user)
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("inventory:product_list")
    else:
        form = ProductForm(instance=Product(created_by=request.user))
    return render(request, 
                    "inventory/product_form.html",
                    {"form": form}
                )

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, created_by=request.user)
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

@login_required
def product_stock(request, pk):
    product = get_object_or_404(Product, pk=pk, created_by=request.user)

    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]
            edit_quantity = form.cleaned_data["edit_quantity"]

            if action == "increase":
                movement_type = StockMovement.MovementType.STOCK_IN
            else:
                movement_type = StockMovement.MovementType.STOCK_OUT
            try:
                apply_stock_movement(product=product,movement_type=movement_type, quantity=edit_quantity, user=request.user)
                return redirect("inventory:product_list")
            except ValidationError as e:
                form.add_error("edit_quantity", e.message)
    else:
        form = StockForm()

    return render(
        request,
        "inventory/product_stock.html",{
            "product": product,
            "form": form,
            }
    )

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, created_by=request.user)

    if product.quantity > 0:
        return render(request, "inventory/product_confirm_delete.html",
                          {
                              "product": product,
                              "cannot_delete": True,
                          }
                        )

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