# cart/tests.py (FINAL & BUG-FREE CODE)

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from store.models import Product, Category
from .models import Cart, CartItem, Order
from accounts.models import Address
from decimal import Decimal

User = get_user_model()

class CartViewsTestCase(TestCase):
    def setUp(self):
        """Har test se pehle initial data set up karein."""
        self.client = Client()
        self.user = User.objects.create_user(username='cartuser', password='password123')
        
        # FIX: Cart.DoesNotExist bug को हल करने के लिए Cart को यहां स्पष्ट रूप से बनाएं
        self.cart = Cart.objects.create(user=self.user)
        
        self.client.login(username='cartuser', password='password123')

        self.category = Category.objects.create(name='Fruits')
        self.product_in_stock = Product.objects.create(
            category=self.category,
            name='Apple',
            price=Decimal('100.00'),
            stock=5
        )
        self.product_out_of_stock = Product.objects.create(
            category=self.category,
            name='Banana',
            price=Decimal('50.00'),
            stock=0
        )
        self.address = Address.objects.create(
            user=self.user,
            address_line_1="123 Test Street",
            city="Testville",
            state="Testland",
            pincode="123456",
            is_default=True 
        )

    def test_add_to_cart(self):
        """Test karein ki item cart mein add ho raha hai aur stock check kaam kar raha hai."""
        # Cart item count 0 से शुरू होना चाहिए
        self.assertEqual(self.cart.get_total_items(), 0) 

        # Stock waale product ko add karke dekhein
        response = self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        self.assertEqual(response.status_code, 302) 
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.get_total_items(), 1)
        self.assertEqual(CartItem.objects.count(), 1)

        # Out of stock waale product ko add karne ki koshish karein
        response = self.client.get(reverse('add_to_cart', args=[self.product_out_of_stock.id]))
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.get_total_items(), 1) 

    def test_cart_view(self):
        """Test karein ki cart page sahi se dikh raha hai."""
        response = self.client.get(reverse('view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')

    def test_remove_from_cart(self):
        """Test karein ki item cart se remove ho raha hai."""
        self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        cart_item = CartItem.objects.get(product=self.product_in_stock)
        
        response = self.client.get(reverse('remove_from_cart', args=[cart_item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart.get_total_items(), 0)

    def test_increment_decrement_cart_item_ajax(self):
        """Test karein ki AJAX se quantity badh aur ghat rahi hai."""
        self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        cart_item = CartItem.objects.get(product=self.product_in_stock)
        
        response = self.client.get(reverse('increment_cart_item', args=[cart_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['item_quantity'], 2)

        response = self.client.get(reverse('decrement_cart_item', args=[cart_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['item_quantity'], 1)

    def test_stock_limit_in_cart(self):
        """Test karein ki user stock se zyaada item add na kar paaye."""
        for _ in range(5):
            self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        
        cart_item = CartItem.objects.get(product=self.product_in_stock)
        self.assertEqual(cart_item.quantity, 5)

        response = self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

    def test_checkout_cod_successful(self):
        """Test karein ki COD checkout process sahi se kaam kar raha hai."""
        self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        
        checkout_data = {
            'address_choice': 'existing', # FIX: 'address_choice' पैरामीटर ज़रूरी है
            'selected_address': self.address.id,
            'payment_method': 'COD'
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        order = Order.objects.get(user=self.user)
        
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order_successful', args=[order.order_id]))
        
        self.cart.refresh_from_db()
        self.assertEqual(self.cart.get_total_items(), 0)