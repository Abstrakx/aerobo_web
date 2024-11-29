from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets
from functools import wraps
from .models import aerobo_member, Barang, Peminjaman
from .serializers import aerobo_member_serializer, barang_serializer, peminjaman_serializer
from .forms import aerobo_member_form, login_member_form, barang_form, PeminjamanForm

class aerobo_member_viewset(viewsets.ModelViewSet):
    queryset = aerobo_member.objects.all()
    serializer_class = aerobo_member_serializer

class barang_viewset(viewsets.ModelViewSet):
    queryset = Barang.objects.all()
    serializer_class = barang_serializer

class peminjaman_viewset(viewsets.ModelViewSet):
    queryset = Peminjaman.objects.all()
    serializer_class = peminjaman_serializer

class CustomLoginView(LoginView):
    template_name = 'login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)

@login_required(login_url='login')
def dashboard_anggota_list(request):
    # Fetch all members
    mahasiswas = aerobo_member.objects.all()
    
    if not mahasiswas.exists():
        mahasiswas = None

    # Handle form submission
    if request.method == 'POST':
        form = aerobo_member_form(request.POST, request.FILES)
        if form.is_valid():
            anggota = form.save(commit=False)
            anggota.password = make_password(form.cleaned_data['password'])
            anggota.save()
            return redirect('dashboard')  # Replace 'dashboard' with your actual URL name
        else:
            print(form.errors)  # Debugging, can be removed in production
    else:
        form = aerobo_member_form()

    context = {
        'form': form,
        'mahasiswas': mahasiswas,
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def delete_member(request):
    if request.method == 'POST':
        nim = request.POST.get('nim')
        try:
            mahasiswa = aerobo_member.objects.get(nim=nim)

            # Delete QR code for mahasiswa if it exists
            if mahasiswa.qr_code_aerobo:
                qr_mahasiswa_path = mahasiswa.qr_code_aerobo.name  # Get the relative path in MEDIA
                if default_storage.exists(qr_mahasiswa_path):  # Check if the file exists
                    default_storage.delete(qr_mahasiswa_path)  # Delete the file using default_storage

            # Delete the profile picture for mahasiswa if it exists
            if mahasiswa.profile_picture:
                profile_picture_path = mahasiswa.profile_picture.name
                if default_storage.exists(profile_picture_path):
                    default_storage.delete(profile_picture_path)

            mahasiswa.delete()
            messages.success(request, 'Data mahasiswa berhasil dihapus.')
        except aerobo_member.DoesNotExist:
            messages.error(request, 'Data mahasiswa tidak ditemukan.')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
            
    return redirect('dashboard')

@login_required(login_url='login')
def edit_member(request):
    # Fetch all members
    mahasiswas = aerobo_member.objects.all()
    
    if not mahasiswas.exists():
        mahasiswas = None

    # Handle form submission
    if request.method == 'POST':
        # Get data from the form
        id = request.POST.get('id')
        nim = request.POST.get('nim')
        nama = request.POST.get('nama')
        divisi = request.POST.get('divisi')
        username = request.POST.get('username')
        password = request.POST.get('password')
        profile_picture = request.FILES.get('profile_picture')

        # Debugging prints
        print("Received Data:")
        print("ID:", id)
        print("NIM:", nim)
        print("Nama:", nama)
        print("Divisi:", divisi)
        print("Username:", username)
        print("Password:", password)
        print("Profile Picture:", profile_picture)

        try:
            # Retrieve the member from the database
            mahasiswa = aerobo_member.objects.get(id=id)
            print(f"Found member: {mahasiswa}")

            # Update the member data
            mahasiswa.nim = nim
            mahasiswa.nama = nama
            mahasiswa.divisi = divisi
            mahasiswa.username = username

            # Check if a new profile picture was uploaded
            if profile_picture:
                print("New profile picture uploaded.")
                # Delete the old profile picture if it exists
                if mahasiswa.profile_picture:
                    if default_storage.exists(mahasiswa.profile_picture.name):
                        print(f"Deleting old profile picture: {mahasiswa.profile_picture.name}")
                        default_storage.delete(mahasiswa.profile_picture.name)
                # Assign the new profile picture to the member
                mahasiswa.profile_picture = profile_picture
            else:
                print("No new profile picture uploaded.")

            # Check if the password was provided and is different from the current one
            if password:
                if password != mahasiswa.password:
                    print("Updating password.")
                    mahasiswa.password = make_password(password)
                else:
                    print("Password not changed (same as current).")
            else:
                print("No new password provided.")

            # Save the updated member data to the database
            mahasiswa.save()
            print("Member data updated successfully.")

            messages.success(request, 'Mahasiswa updated successfully')
            return redirect('dashboard')

        except aerobo_member.DoesNotExist:
            print(f"Mahasiswa with NIM {nim} not found.")
            messages.error(request, 'Mahasiswa not found')
            return redirect('dashboard')

    return redirect('dashboard')



@login_required(login_url='login')
def dashboard_barang_list(request):
    # Fetch all members
    barangs = Barang.objects.all()
    
    if not barangs.exists():
        barangs = None

    # Handle form submission
    if request.method == 'POST':
        form = barang_form(request.POST, request.FILES)
        if form.is_valid():
            barang = form.save(commit=False)
            barang.save()
            return redirect('dashboard_barang_admin')  # Replace 'dashboard' with your actual URL name
        else:
            print(form.errors)  # Debugging, can be removed in production
    else:
        form = barang_form()

    context = {
        'form': form,
        'barangs': barangs,
    }

    return render(request, 'dashboard_barang_admin.html', context)

@login_required(login_url='login')
def delete_barang(request):
    # Pastikan permintaan menggunakan metode POST
    if request.method == 'POST':
        # Ambil nomor identitas barang dari form yang dikirim
        no_identitas = request.POST.get('no_identitas')
        
        try:
            # Cari objek Barang berdasarkan nomor identitas
            barang = Barang.objects.get(no_identitas=no_identitas)

            # Hapus screenshot barang jika ada
            if barang.screenshot_barang:
                screenshot_barang_path = barang.screenshot_barang.name

                # Periksa apakah file screenshot ada, kemudian hapus
                if default_storage.exists(screenshot_barang_path):
                    default_storage.delete(screenshot_barang_path)

            # Hapus objek barang dari database
            barang.delete()
            
            messages.success(request, 'Data barang berhasil dihapus.')
        
        except Barang.DoesNotExist:
            messages.error(request, 'Data barang tidak ditemukan.')
        
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    # Redirect kembali ke halaman dashboard barang admin
    return redirect('dashboard_barang_admin')

@login_required(login_url='login')
def edit_barang(request):
    if request.method == 'POST':
        # Retrieve 'no_identitas' from POST data
        no_identitas = request.POST.get('no_identitas')
        print(f"Received no_identitas: {no_identitas}")

        try:
            # Retrieve the Barang object from the database
            barang = Barang.objects.get(no_identitas=no_identitas)
            print(f"Found Barang: {barang}")

            # Update Barang data
            barang.nama_barang = request.POST.get('nama_barang')
            barang.jumlah = request.POST.get('jumlah')
            barang.divisi = request.POST.get('divisi')
            barang.status_kelayakan = request.POST.get('status_kelayakan')

            print("Updated fields:")
            print(f"Nama Barang: {barang.nama_barang}")
            print(f"Jumlah: {barang.jumlah}")
            print(f"Divisi: {barang.divisi}")
            print(f"Status Kelayakan: {barang.status_kelayakan}")

            # Check for new screenshot file
            screenshot_barang_new = request.FILES.get('screenshot_barang')
            print(f"New screenshot_barang file: {screenshot_barang_new}")

            if screenshot_barang_new:
                print("New screenshot_barang provided.")
                # Check for and delete the old screenshot file
                if barang.screenshot_barang:
                    print(f"Existing screenshot_barang: {barang.screenshot_barang.name}")
                    if default_storage.exists(barang.screenshot_barang.name):
                        print(f"Deleting old screenshot_barang: {barang.screenshot_barang.name}")
                        default_storage.delete(barang.screenshot_barang.name)

                # Replace with the new file
                barang.screenshot_barang = screenshot_barang_new
            else:
                print("No new screenshot_barang provided.")

            # Save the updated object to the database
            barang.save()
            print("Barang updated successfully.")

            messages.success(request, 'Barang updated successfully')
            return redirect('dashboard_barang_admin')

        except Barang.DoesNotExist:
            print(f"Barang with no_identitas {no_identitas} not found.")
            messages.error(request, 'Barang not found')
            return redirect('dashboard_barang_admin')

    print("Request method is not POST.")
    return redirect('dashboard_barang_admin')

@login_required(login_url='login')
def update_status(request, pk, new_status):
    peminjaman = get_object_or_404(Peminjaman, pk=pk)

    if new_status == 'Diterima' and peminjaman.barang.jumlah >= peminjaman.jumlah_pinjam:
        peminjaman.status = Peminjaman.Status.DITERIMA
    elif new_status == 'Dikembalikan':
        peminjaman.status = Peminjaman.Status.DIKEMBALIKAN
        peminjaman.tanggal_kembali = timezone.now()
    else:
        return render(request, 'error.html', {'message': 'Aksi tidak valid atau stok barang habis.'})

    peminjaman.save()
    return redirect('peminjaman_list')

@login_required(login_url='login')
def peminjaman_list(request):
    peminjamans = Peminjaman.objects.all()
    return render(request, 'dashboard_admin_peminjaman.html', {'peminjamans': peminjamans})

@login_required(login_url='login')
def delete_peminjaman(request):
    if request.method == 'POST':
        # Get the ID from the POST data
        id = request.POST.get('id')

        # Ensure the id is valid (check if it's not None or empty)
        if id:
            try:
                # Retrieve the peminjaman object based on the provided ID
                peminjaman = Peminjaman.objects.get(id=id)

                # Perform the deletion
                peminjaman.delete()

                # Add a success message
                messages.success(request, f'Peminjaman with ID {id} has been deleted.')
            except Peminjaman.DoesNotExist:
                # Handle the case where the object doesn't exist
                messages.error(request, 'Peminjaman not found.')
        else:
            messages.error(request, 'Invalid ID.')

    # Redirect to the peminjaman list page after deletion
    return redirect('peminjaman_list')

def mahasiswa_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'mahasiswa_id' not in request.session:
            return redirect('member_login')  
        return view_func(request, *args, **kwargs)
    return wrapper

def member_login(request):
    if request.method == 'POST':
        form = login_member_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Cek apakah username ada di database
            try:
                mahasiswa = aerobo_member.objects.get(username=username)
            except aerobo_member.DoesNotExist:
                return render(request, 'login_member.html', {
                    'form': form,
                    'error': 'Username tidak ditemukan.'
                })

            # Verifikasi password
            if check_password(password, mahasiswa.password):
                # Simpan sesi login
                request.session['mahasiswa_id'] = mahasiswa.id
                return redirect('dashboard/' + mahasiswa.nim)
            else:
                return render(request, 'login_member.html', {
                    'form': form,
                    'error': 'Password salah.'
                })
    else:
        form = login_member_form()

    return render(request, 'login_member.html', {'form': form})

def member_logout(request):
    if 'mahasiswa_id' in request.session:
        del request.session['mahasiswa_id']
    return redirect('member_login')

@mahasiswa_login_required
def dashboard_member(request, nim):
    # Get the member with the given NIM
    mahasiswa = get_object_or_404(aerobo_member, nim=nim)
    
    # Filter peminjaman hanya untuk mahasiswa yang sedang login
    peminjaman = Peminjaman.objects.filter(aerobo_member=mahasiswa)

    # Ensure the user is authorized (optional)
    if 'mahasiswa_id' not in request.session or request.session['mahasiswa_id'] != mahasiswa.id:
        return render(request, '403.html', status=403)  
    
    if request.method == 'POST':
        form = PeminjamanForm(request.POST)
        if form.is_valid():
            peminjaman_obj = form.save(commit=False)
            peminjaman_obj.aerobo_member = mahasiswa  # Assign the mahasiswa to the peminjaman
            peminjaman_obj.save()  # Save the peminjaman
            return redirect('dashboard_member', nim=mahasiswa.nim)  # Redirect to the dashboard
    else:
        form = PeminjamanForm()

    context = {
        'mahasiswa': mahasiswa,
        'peminjamans': peminjaman,  # Hanya data peminjaman milik mahasiswa ini
        'form': form,
    }

    # Render the dashboard
    return render(request, 'dashboard_member.html', context)


@mahasiswa_login_required
def dashboard_barang_member(request, nim):
    # Get the member with the given NIM
    mahasiswa = get_object_or_404(aerobo_member, nim=nim)
    barangs = Barang.objects.all()
    # Ensure the user is authorized (optional)
    if 'mahasiswa_id' not in request.session or request.session['mahasiswa_id'] != mahasiswa.id:
        return render(request, '403.html', status=403)  

    context = {
        'mahasiswa': mahasiswa,
        'barangs': barangs,
    }

    # Render the dashboard
    return render(request, 'dashboard_barang.html', context)

@mahasiswa_login_required
def peminjaman_barang_submit(request):
    if request.method == 'POST':
        form = PeminjamanForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('dashboard_member')  
    else:
        form = PeminjamanForm()
    return render(request, 'dashboard_member.html', {'form': form})

@mahasiswa_login_required
def update_status_member(request, pk, new_status):
    peminjaman = get_object_or_404(Peminjaman, pk=pk)

    if new_status == 'Diterima' and peminjaman.barang.jumlah >= peminjaman.jumlah_pinjam:
        peminjaman.status = Peminjaman.Status.DITERIMA
    elif new_status == 'Dikembalikan':
        peminjaman.status = Peminjaman.Status.DIKEMBALIKAN
        peminjaman.tanggal_kembali = timezone.now()
    else:
        return render(request, 'error.html', {'message': 'Aksi tidak valid atau stok barang habis.'})

    peminjaman.save()
    return redirect('dashboard_member')