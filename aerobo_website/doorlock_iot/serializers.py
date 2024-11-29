from rest_framework import serializers
from .models import aerobo_member, Barang, Peminjaman

class aerobo_member_serializer(serializers.ModelSerializer):
    class Meta:
        model = aerobo_member
        fields = ['id', 'username', 'nama', 'nim', 'divisi', 'qr_code_aerobo', 'last_in', 'profile_picture']

class barang_serializer(serializers.ModelSerializer):
    class Meta:
        model = Barang
        fields = '__all__'

class peminjaman_serializer(serializers.ModelSerializer):
    class Meta:
        model = Peminjaman
        fields = '__all__'