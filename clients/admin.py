from django.contrib import admin
from .models import Company, Client, Document

# 1. Company Admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

# 2. Client Admin
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "company")
    list_filter = ("company",)
    search_fields = ("name", "user__username", "company__name")

# 3. Document Admin
@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("file", "client", "uploaded_at")
    list_filter = ("client__company",)
    search_fields = ("file", "client__name", "client__company__name")
