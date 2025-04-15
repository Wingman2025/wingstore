from django.test import TestCase
from .models import Product

# Create your tests here.

class ProductModelTest(TestCase):
    def test_create_product(self):
        product = Product.objects.create(
            name="Tabla Wingfoil Pro",
            description="Tabla ligera para riders avanzados.",
            stock=5
        )
        self.assertEqual(product.name, "Tabla Wingfoil Pro")
        self.assertEqual(product.stock, 5)
        self.assertTrue(isinstance(product, Product))
