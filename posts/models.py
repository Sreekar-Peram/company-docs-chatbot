from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from clients.models import Client

class Post(models.Model):
    name = models.CharField(max_length=75)
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    # ✅ TEMP FIX: Make client field optional for initial migration
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)

    any_file = models.FileField(upload_to='pdfs/', default=None, blank=True)
    date = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.client.name if self.client else 'No Client'})"
