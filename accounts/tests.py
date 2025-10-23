from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Address, UserProfile

# User model ko get karein
User = get_user_model()

class AccountsViewsTestCase(TestCase):
    def setUp(self):
        """Har test se pehle initial data set up karein."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.user.is_active = True # Test ke liye user ko active maan rahe hain
        self.user.save()

    def test_login_view(self):
        """Test karein ki login page sahi se kaam kar raha hai."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200) # Check karein ki page khul raha hai
        self.assertTemplateUsed(response, 'accounts/login.html') # Check karein ki sahi template use ho raha hai

        # Sahi details se login karke dekhein
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, 302) # Login ke baad redirect hona chahiye
        self.assertRedirects(response, reverse('home'))

        # Galat details se login karke dekhein
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200) # Page reload hona chahiye
        self.assertContains(response, 'Please enter a correct username and password.') # Error message aana chahiye

    def test_profile_view_redirects_if_not_logged_in(self):
        """Test karein ki bina login ke profile page access nahi ho sakta."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302) # Redirect hona chahiye
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")

    def test_profile_view_accessible_if_logged_in(self):
        """Test karein ki login ke baad profile page access ho raha hai."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertContains(response, self.user.username)

    def test_logout_view(self):
        """Test karein ki logout sahi se kaam kar raha hai."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
        # Check karein ki user ab login nahi hai
        self.assertFalse('_auth_user_id' in self.client.session)


class AddressModelTestCase(TestCase):
    def setUp(self):
        """Address model test ke liye user banayein."""
        self.user = User.objects.create_user(
            username='addressuser',
            password='password123'
        )

    def test_address_creation(self):
        """Test karein ki address sahi se create ho raha hai."""
        address = Address.objects.create(
            user=self.user,
            address_line_1="123 Test Street",
            city="Testville",
            state="Testland",
            pincode="123456"
        )
        self.assertEqual(address.user, self.user)
        self.assertEqual(address.city, "Testville")
        self.assertEqual(str(address), "123 Test Street, Testville (addressuser)")

    def test_first_address_is_default(self):
        """Test karein ki user ka pehla address automatically default ban jata hai."""
        address1 = Address.objects.create(
            user=self.user,
            address_line_1="First Address",
            city="Testville",
            state="Testland",
            pincode="123456"
        )
        self.assertTrue(address1.is_default)

    def test_new_default_address_unsets_old_one(self):
        """Test karein ki naya default address banane par purana wala non-default ho jata hai."""
        address1 = Address.objects.create(
            user=self.user,
            address_line_1="First Address",
            city="Testville",
            state="Testland",
            pincode="123456",
        )
        address2 = Address.objects.create(
            user=self.user,
            address_line_1="Second Address",
            city="Testville",
            state="Testland",
            pincode="654321",
            is_default=True
        )

        # address1 ko database se dobara fetch karein
        address1.refresh_from_db()

        self.assertFalse(address1.is_default)
        self.assertTrue(address2.is_default)