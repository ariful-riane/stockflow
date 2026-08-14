from django.contrib import admin

from .models import Category, Product, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "category",
        "quantity",
        "price",
        "minimum_stock",
        "low_stock",
        "updated_at",
    )

    search_fields = ("name", "sku")
    list_filter = ("category",)
    readonly_fields = ("quantity", "created_at", "updated_at")

    @admin.display(boolean=True, description="Low stock")
    def low_stock(self, product):
        return product.is_low_stock


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "movement_type",
        "quantity",
        "performed_by",
        "created_at",
    )

    search_fields = (
        "product__name",
        "product__sku",
        "performed_by__username",
    )

    list_filter = ("movement_type", "created_at")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"