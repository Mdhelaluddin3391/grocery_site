# accounts/managers.py (FINAL CODE: Dual User Creation Logic)

from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """
    Custom user model manager jo customer (phone_number) aur admin (username/password)
    dono ko support karta hai.
    """
    def create_user(self, username=None, phone_number=None, password=None, **extra_fields):
        # 1. Check if this is a Staff/Superuser creation (via Django Admin or createsuperuser)
        if extra_fields.get('is_staff') or extra_fields.get('is_superuser'):
            # Admin/Staff: Username aur password required hain.
            if not username:
                raise ValueError('Staff/Superuser must have a username')
            
            user = self.model(
                username=username,
                phone_number=phone_number, # Admin ke liye optional
                **extra_fields
            )
            user.set_password(password) # Admin uses password
        
        # 2. Customer creation (only phone_number is provided from the custom flow)
        elif phone_number:
            user = self.model(
                phone_number=phone_number,
                username=phone_number, # AbstractUser ki zaroorat poori karne ke liye dummy username
                **extra_fields
            )
            user.set_unusable_password() # Customer uses OTP
        
        else:
            raise ValueError('A phone number (Customer) or username (Admin) must be provided.')

        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Default Django Superuser flow (username/password based)
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # create_user ko call karein. phone_number is waqt optional hai.
        user = self.create_user(username=username, password=password, **extra_fields)
        return user