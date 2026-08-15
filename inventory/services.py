"""Business logic for inventory stock operations."""


from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Product, StockMovement


@transaction.atomic
def apply_stock_movement(*, product, movement_type, quantity, user):
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise ValidationError("Quantity must be a whole number.")

    if quantity <= 0:
        raise ValidationError("Quantity must be greater than zero.")

    if movement_type not in StockMovement.MovementType.values:
        raise ValidationError("Invalid stock movement type.")

    if user is None or not user.is_authenticated:
        raise ValidationError("An authenticated user is required.")

    locked_product = Product.objects.select_for_update().get(pk=product.pk)

    if movement_type == StockMovement.MovementType.STOCK_IN:
        locked_product.quantity += quantity

    elif movement_type == StockMovement.MovementType.STOCK_OUT:
        if quantity > locked_product.quantity:
            raise ValidationError(
                f"Only {locked_product.quantity} units are available."
            )

        locked_product.quantity -= quantity

    locked_product.save(update_fields=["quantity", "updated_at"])

    movement = StockMovement.objects.create(
        product=locked_product,
        movement_type=movement_type,
        quantity=quantity,
        performed_by=user,
    )

    return movement