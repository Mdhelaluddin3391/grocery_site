from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)

    def __str__(self):
        return f'{self.user.username} Profile'


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='Home')
    is_default = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.address_line_1}, {self.city} ({self.user.username})"

    class Meta:
        verbose_name_plural = "Addresses"

    def save(self, *args, **kwargs):
        # Agar user ka koi address nahi hai, to isey default bana do
        if not self.user.addresses.exists():
            self.is_default = True
        
        # Agar is address ko default banaya ja raha hai
        elif self.is_default:
            # To user ke baaki sabhi addresses ko non-default kar do
            self.user.addresses.exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)


# Jab bhi koi naya User bane, uska UserProfile automatically ban jaye
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# --- YEH FUNCTION HATA DIYA GAYA HAI KYUNKI YEH ERROR DE RAHA THA ---
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()