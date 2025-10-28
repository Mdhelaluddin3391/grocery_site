# dashboard/models.py
from django.db import models

class AuthorizedStaff(models.Model):
    email = models.EmailField(
        unique=True,
        help_text="The personal email address (e.g., Gmail) of the staff member to grant dashboard access."
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Optional: Name of the staff member for reference."
    )
    role = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Optional: Role like 'Store Manager', 'Incharge' etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Authorized Staff Email"
        verbose_name_plural = "Authorized Staff Emails"
        ordering = ['-created_at']

    def __str__(self):
        return self.email