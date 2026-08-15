from django.test import TestCase

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Category, Product, StockMovement
from .services import apply_stock_movement


class StockOperationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpassword",
        )

        self.category = Category.objects.create(
            name="Electronics",
        )

        self.product = Product.objects.create(
            name="Wireless Keyboard",
            sku="KEY-001",
            category=self.category,
            quantity=10,
            price=Decimal("39.99"),
            minimum_stock=5,
        )

    def test_stock_in_increases_quantity_and_creates_movement(self):
        movement = apply_stock_movement(
            product=self.product,
            movement_type=StockMovement.MovementType.STOCK_IN,
            quantity=5,
            user=self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 15)
        self.assertEqual(StockMovement.objects.count(), 1)
        self.assertEqual(movement.product, self.product)
        self.assertEqual(movement.quantity, 5)
        self.assertEqual(
            movement.movement_type,
            StockMovement.MovementType.STOCK_IN,
        )
        self.assertEqual(movement.performed_by, self.user)

    def test_stock_out_decreases_quantity_and_creates_movement(self):
        movement = apply_stock_movement(
            product=self.product,
            movement_type=StockMovement.MovementType.STOCK_OUT,
            quantity=4,
            user=self.user,
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 6)
        self.assertEqual(StockMovement.objects.count(), 1)
        self.assertEqual(movement.quantity, 4)
        self.assertEqual(
            movement.movement_type,
            StockMovement.MovementType.STOCK_OUT,
        )

    def test_stock_out_rejects_insufficient_stock(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Only 10 units are available.",
        ):
            apply_stock_movement(
                product=self.product,
                movement_type=StockMovement.MovementType.STOCK_OUT,
                quantity=11,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_zero_quantity_is_rejected(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Quantity must be greater than zero.",
        ):
            apply_stock_movement(
                product=self.product,
                movement_type=StockMovement.MovementType.STOCK_IN,
                quantity=0,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_negative_quantity_is_rejected(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Quantity must be greater than zero.",
        ):
            apply_stock_movement(
                product=self.product,
                movement_type=StockMovement.MovementType.STOCK_IN,
                quantity=-5,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_non_integer_quantity_is_rejected(self):
        for quantity in ("5", 2.5, True):
            with self.subTest(quantity=quantity):
                with self.assertRaisesMessage(
                    ValidationError,
                    "Quantity must be a whole number.",
                ):
                    apply_stock_movement(
                        product=self.product,
                        movement_type=StockMovement.MovementType.STOCK_IN,
                        quantity=quantity,
                        user=self.user,
                    )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_invalid_movement_type_is_rejected(self):
        with self.assertRaisesMessage(
            ValidationError,
            "Invalid stock movement type.",
        ):
            apply_stock_movement(
                product=self.product,
                movement_type="INVALID",
                quantity=5,
                user=self.user,
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)

    def test_unauthenticated_user_is_rejected(self):
        with self.assertRaisesMessage(
            ValidationError,
            "An authenticated user is required.",
        ):
            apply_stock_movement(
                product=self.product,
                movement_type=StockMovement.MovementType.STOCK_IN,
                quantity=5,
                user=AnonymousUser(),
            )

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(StockMovement.objects.count(), 0)
