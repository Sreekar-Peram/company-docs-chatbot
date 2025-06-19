from django.db import models
from django.contrib.auth.models import User

# 1. Company model
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# 2. Client model (linked to Company and User)
class Client(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clients_client')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='clients')

    class Meta:
        unique_together = ('name', 'company')  # ensures client names are unique per company

    def __str__(self):
        return f"{self.name} ({self.company.name})"

# 3. Upload path logic
def upload_to(instance, filename):
    company_name = instance.client.company.name.replace(" ", "_")
    client_name = instance.client.name.replace(" ", "_")
    return f"pdfs/{company_name}/{client_name}/{filename}"

# 4. Document model
class Document(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to=upload_to)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
