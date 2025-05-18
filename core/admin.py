from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Drug, Sale, Debtor  # Import all at once
from .models import Acknowledgement, Investor

# Register models
admin.site.register(User, UserAdmin)
admin.site.register(Drug)
admin.site.register(Sale)
admin.site.register(Debtor)
admin.site.register(Acknowledgement)
admin.site.register(Investor)