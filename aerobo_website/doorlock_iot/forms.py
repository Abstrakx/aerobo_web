from django import forms
from .models import aerobo_member, Barang, Peminjaman

class login_member_form(forms.Form):
    username = forms.CharField(label="Username", max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, label="Password", required=True)

class aerobo_member_form(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Konfirmasi Password"
    )

    class Meta:
        model = aerobo_member
        fields = ['username', 'nama', 'nim', 'divisi', 'profile_picture']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Password dan Konfirmasi Password tidak cocok.")
        return cleaned_data

class barang_form(forms.ModelForm):
    class Meta:
        model = Barang
        fields = '__all__'

class PeminjamanForm(forms.ModelForm):
    class Meta:
        model = Peminjaman
        fields = ['barang', 'jumlah_pinjam']
        widgets = {
            'barang': forms.Select(attrs={'class': 'form-control'}), 
            'jumlah_pinjam': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Jumlah barang'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        barang = cleaned_data.get('barang')
        jumlah_pinjam = cleaned_data.get('jumlah_pinjam')

        if barang and jumlah_pinjam:
            if jumlah_pinjam > barang.jumlah:
                raise forms.ValidationError("Jumlah barang yang diminta melebihi stok tersedia.")
        return cleaned_data
