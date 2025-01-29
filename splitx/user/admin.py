from django.contrib import admin
from .models import User, Batch, Group, Transaction, Settlement, Collage

# Register your models here.
admin.site.register(User)
admin.site.register(Batch)
admin.site.register(Group)
admin.site.register(Transaction)
admin.site.register(Settlement)
admin.site.register(Collage)

