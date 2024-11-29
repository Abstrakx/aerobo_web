from django.urls import path, include
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from .views import aerobo_member_viewset, barang_viewset,  peminjaman_viewset ,CustomLoginView, dashboard_anggota_list, member_login, member_logout, dashboard_member, edit_member, delete_member, dashboard_barang_list, delete_barang, edit_barang, dashboard_barang_member, peminjaman_list, update_status, peminjaman_barang_submit, delete_peminjaman

router = DefaultRouter()
router.register(r'aerobo_member', aerobo_member_viewset)
router.register(r'barang', barang_viewset)
router.register(r'peminjaman', peminjaman_viewset)

urlpatterns = [
    path('login_admin/', CustomLoginView.as_view(), name='login'),  
    path('', member_login, name='member_login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('logout_member/', member_logout, name='logout_member'),
    path('dashboard/', dashboard_anggota_list, name='dashboard'),
    path('dashboard/<str:nim>/', dashboard_member, name='dashboard_member'),
    path('api/', include(router.urls)),
    path('edit-member/', edit_member, name='edit_member'),
    path('delete-member/', delete_member, name='delete_member'),
    path('dashboard-barang-admin/', dashboard_barang_list, name='dashboard_barang_admin'),
    path('delete-barang/', delete_barang, name='delete_barang'),
    path('edit-barang/', edit_barang, name='edit_barang'),
    path('dashboard-barang/<str:nim>/', dashboard_barang_member, name='dashboard_barang_member'),
    path('peminjaman/', peminjaman_list, name='peminjaman_list'),
    path('peminjaman/<int:pk>/status/<str:new_status>/', update_status, name='update_status'),
    path('peminjaman/submit/', peminjaman_barang_submit, name='peminjaman_barang_submit'),
    path('delete-peminjaman/', delete_peminjaman, name='delete_peminjaman'),
]