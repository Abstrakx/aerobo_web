from django.db import models
from django.core.files import File
from django.conf import settings
from model_utils import FieldTracker
from io import BytesIO
import qrcode
import os

# Model Anggota
class aerobo_member(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=255)
    nama = models.CharField(max_length=255)
    nim = models.CharField(max_length=255)
    divisi = models.CharField(max_length=255)
    qr_code_aerobo = models.ImageField(upload_to='qr_code_aerobo/', blank=True, null=True)
    last_in = models.JSONField(default=list)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True, null=True)

    # Field tracker untuk melacak perubahan field tertentu
    tracker = FieldTracker(fields=['nama', 'nim', 'divisi'])

    def save(self, *args, **kwargs):
        nama_depan = self.nama.split(" ")[0]

        # Logika untuk Auntentikasi QR Code
        if not self.qr_code_aerobo or self._state.adding or self.tracker.has_changed('nama') or self.tracker.has_changed('nim') or self.tracker.has_changed('divisi'):
            # Hapus file QR mahasiswa lama
            if self.qr_code_aerobo:
                qr_path = os.path.join(settings.MEDIA_ROOT, self.qr_code_aerobo.name)
                if os.path.exists(qr_path):
                    os.remove(qr_path)
                self.qr_code_aerobo.delete(save=False)

            # Generate QR mahasiswa baru
            qrcode_img = qrcode.make(f'{self.nim}-{nama_depan}-{self.divisi}')
            qr_io = BytesIO()
            qrcode_img.save(qr_io, 'PNG')
            qr_file = File(qr_io, name=f'{self.nim}-{nama_depan}-{self.divisi}.png')
            self.qr_code_aerobo.save(qr_file.name, qr_file, save=False)
    
        # Simpan objek ke database
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nama} ({self.nim})"
    
# Model Barang
class Barang(models.Model):
    class Status(models.TextChoices):
        VTOL = 'VTOL', 'VTOL'
        RP = 'RP', 'RP'
        TD = 'TD', 'TD'
        Umum = 'Umum', 'Umum'
    
    class Kelayakan(models.TextChoices):
        Rusak = 'Rusak', 'Rusak'
        Normal = 'Normal', 'Normal'

    no_identitas = models.AutoField(primary_key=True)
    nama_barang = models.CharField(max_length=100)
    jumlah = models.PositiveIntegerField()
    screenshot_barang = models.ImageField(upload_to='screenshot_barang/', blank=True, null=True)
    status_kelayakan = models.CharField(
        max_length=20,
        choices=Kelayakan.choices,
        default=Kelayakan.Normal
    )
    divisi = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.Umum,
    )

    def __str__(self):
        return self.nama_barang

# Model Peminjaman
class Peminjaman(models.Model):
    class Status(models.TextChoices):
        DIAJUKAN = 'Diajukan', 'Diajukan'
        DITERIMA = 'Diterima', 'Diterima'
        DIKEMBALIKAN = 'Dikembalikan', 'Dikembalikan'

    aerobo_member = models.ForeignKey(aerobo_member, on_delete=models.CASCADE)
    barang = models.ForeignKey(Barang, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField(auto_now_add=True)
    tanggal_kembali = models.DateField(null=True, blank=True)
    jumlah_pinjam = models.PositiveIntegerField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DIAJUKAN,  
    )

    def __str__(self):
        return f"{self.aerobo_member.nama} meminjam {self.barang.nama_barang}"

    def is_terlambat(self):
        if self.tanggal_kembali and self.tanggal_kembali > self.tanggal_pinjam:
            return True
        return False
    
    def is_tersedia(self, jumlah_pinjam):
        return self.jumlah >= jumlah_pinjam
    
    def save(self, *args, **kwargs):
        # Reduce barang quantity on acceptance
        if self.status == self.Status.DITERIMA and self.pk is None:  # New entry
            if self.barang.jumlah < self.jumlah_pinjam:
                raise ValueError("Barang tidak mencukupi!")
            self.barang.jumlah -= self.jumlah_pinjam
            self.barang.save()

        # Return barang quantity when returned
        if self.status == self.Status.DIKEMBALIKAN:
            self.barang.jumlah += self.jumlah_pinjam
            self.barang.save()

        super().save(*args, **kwargs)