from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from cart.models import Order, OrderItem
from store.models import Product, Category

class DashboardViewsTestCase(TestCase):
    def setUp(self):
        """Har test se pehle zaroori data set up karein."""
        
        # Do tarah ke user banayein: ek staff aur ek normal customer
        self.staff_user = User.objects.create_user(username='staffuser', password='password123', is_staff=True)
        self.customer_user = User.objects.create_user(username='customer', password='password123')
        
        self.client = Client()

        # Kuch products banayein
        self.category = Category.objects.create(name='Fruits')
        self.product1 = Product.objects.create(category=self.category, name='Apple', price=Decimal('100.00'))
        self.product2 = Product.objects.create(category=self.category, name='Banana', price=Decimal('50.00'))

        # Kuch orders banayein taaki data test kar sakein
        self.order1 = Order.objects.create(
            user=self.customer_user, 
            total_amount=Decimal('150.00'), 
            status='Delivered' # Revenue test ke liye
        )
        self.order2 = Order.objects.create(
            user=self.customer_user, 
            total_amount=Decimal('50.00'), 
            status='Pending' # Pending orders test ke liye
        )

    def test_dashboard_access_for_staff(self):
        """Test karein ki staff user dashboard ke pages access kar sakta hai."""
        self.client.login(username='staffuser', password='password123')
        
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('dashboard_order_list'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(reverse('dashboard_customer_list'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_redirect_for_non_staff(self):
        """Test karein ki normal user dashboard access nahi kar sakta."""
        self.client.login(username='customer', password='password123')
        
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302) # Redirect hona chahiye
        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')
        
    def test_dashboard_kpi_calculations(self):
        """Test karein ki dashboard home page par KPI data sahi aa raha hai."""
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('dashboard_home'))
        
        self.assertEqual(response.status_code, 200)
        # Check karein ki context mein data sahi hai
        self.assertEqual(response.context['total_revenue'], Decimal('150.00'))
        self.assertEqual(response.context['total_orders_count'], 2)
        self.assertEqual(response.context['pending_orders_count'], 1)
        self.assertEqual(response.context['total_customers_count'], 1) # Sirf ek customer hai

    def test_order_list_filtering(self):
        """Test karein ki All Orders page par filtering kaam kar rahi hai."""
        self.client.login(username='staffuser', password='password123')
        
        # 'Pending' status ke liye filter karein
        response = self.client.get(reverse('dashboard_order_list') + '?status=Pending')
        self.assertEqual(response.status_code, 200)
        # Check karein ki sirf ek order (pending wala) dikh raha hai
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0].id, self.order2.id)

        # 'Delivered' status ke liye filter karein
        response = self.client.get(reverse('dashboard_order_list') + '?status=Delivered')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['orders']), 1)
        self.assertEqual(response.context['orders'][0].id, self.order1.id)

    def test_customer_list_page(self):
        """Test karein ki customer list page par sirf customers dikh rahe hain."""
        self.client.login(username='staffuser', password='password123')
        response = self.client.get(reverse('dashboard_customer_list'))
        
        self.assertEqual(response.status_code, 200)
        # Check karein ki list mein sirf ek customer hai (staff user nahi hai)
        self.assertEqual(len(response.context['customers']), 1)
        self.assertEqual(response.context['customers'][0].username, 'customer')