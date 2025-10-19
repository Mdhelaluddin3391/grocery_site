# store/models.py

from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories'
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    icon = models.URLField(blank=True, null=True)
    show_on_homepage = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name_plural = "Categories"

    def __str__(self):
        if self.parent:
            return f"{self.name} (Sub-category of {self.parent.name})"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # --- YEH FIELDS ADD KIYE HAIN ---
    old_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    discount = models.CharField(max_length=20, blank=True, null=True) # e.g., "10% OFF"
    quantity = models.CharField(max_length=50, blank=True, null=True) # e.g., "500 ml"
    time = models.CharField(max_length=50, blank=True, null=True) # e.g., "25 MINS"
    # -----------------------------------

    is_special = models.BooleanField(default=False)
    is_hot = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)