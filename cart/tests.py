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
        self.client.login(username='cartuser', password='password123')

        self.category = Category.objects.create(name='Fruits')
        self.product_in_stock = Product.objects.create(
            category=self.category,
            name='Apple',
            price=Decimal('100.00'),
            stock=5 # Yeh stock mein hai
        )
        self.product_out_of_stock = Product.objects.create(
            category=self.category,
            name='Banana',
            price=Decimal('50.00'),
            stock=0 # Yeh out of stock hai
        )
        self.address = Address.objects.create(
            user=self.user,
            address_line_1="123 Test Street",
            city="Testville",
            state="Testland",
            pincode="123456"
        )

    def test_add_to_cart(self):
        """Test karein ki item cart mein add ho raha hai aur stock check kaam kar raha hai."""
        # Stock waale product ko add karke dekhein
        response = self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        self.assertEqual(response.status_code, 302) # Redirect hona chahiye
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.get_total_items(), 1)
        self.assertEqual(CartItem.objects.first().product, self.product_in_stock)

        # Out of stock waale product ko add karne ki koshish karein
        response = self.client.get(reverse('add_to_cart', args=[self.product_out_of_stock.id]))
        self.assertEqual(cart.get_total_items(), 1) # Item count badhna nahi chahiye

    def test_cart_view(self):
        """Test karein ki cart page sahi se dikh raha hai."""
        response = self.client.get(reverse('view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/cart_detail.html')

    def test_remove_from_cart(self):
        """Test karein ki item cart se remove ho raha hai."""
        # Pehle ek item add karein
        self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        cart_item = CartItem.objects.get(product=self.product_in_stock)
        
        # Ab use remove karein
        response = self.client.get(reverse('remove_from_cart', args=[cart_item.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Cart.objects.get(user=self.user).get_total_items(), 0)

    def test_increment_decrement_cart_item_ajax(self):
        """Test karein ki AJAX se quantity badh aur ghat rahi hai."""
        self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        cart_item = CartItem.objects.get(product=self.product_in_stock)
        
        # Increment karein
        response = self.client.get(reverse('increment_cart_item', args=[cart_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['item_quantity'], 2)

        # Decrement karein
        response = self.client.get(reverse('decrement_cart_item', args=[cart_item.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['item_quantity'], 1)

    def test_stock_limit_in_cart(self):
        """Test karein ki user stock se zyaada item add na kar paaye."""
        # product ka stock 5 hai. 5 baar add karein.
        for _ in range(5):
            self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        
        cart_item = CartItem.objects.get(product=self.product_in_stock)
        self.assertEqual(cart_item.quantity, 5)

        # Ab chhati baar add karne ki koshish karein
        response = self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5) # Quantity 5 hi rehni chahiye

    def test_checkout_cod_successful(self):
        """Test karein ki COD checkout process sahi se kaam kar raha hai."""
        # Pehle cart mein item daalein
        self.client.get(reverse('add_to_cart', args=[self.product_in_stock.id]))
        
        # Checkout page par POST request bhejein
        checkout_data = {
            'selected_address': self.address.id,
            'payment_method': 'COD'
        }
        response = self.client.post(reverse('checkout'), checkout_data)
        
        # Check karein ki order ban gaya hai
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        order = Order.objects.get(user=self.user)
        
        # Check karein ki safal page par redirect hua
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('order_successful', args=[order.order_id]))
        
        # Check karein ki cart khaali ho gaya hai
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.get_total_items(), 0)