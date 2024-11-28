from django.contrib import admin
from .models import aerobo_member, Barang, Peminjaman

admin.site.register(aerobo_member)
admin.site.register(Barang)
admin.site.register(Peminjaman)