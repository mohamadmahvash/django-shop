from django.urls import path , include
from . import views

app_name = 'home'

bucket_urls = [
    path('', views.BucketHomeView.as_view(), name='bucket'),
    path('download_obj/<str:key>/',views.DownloadBucketObjectView.as_view(), name='download_object_bucket'),
    path('delete_obj/<str:key>/', views.DeleteBucketObjectView.as_view(), name='delete_object_bucket'),
]

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('bucket/' , include(bucket_urls)),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
