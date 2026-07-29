from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages

from utils import IsAdminUserMixin
from products.models import Product
from . import tasks


class HomeView(View):
    def get(self, request):
        products = Product.objects.filter(available=True)
        return render(request, 'home/index.html', {'products': products})


class BucketHomeView(IsAdminUserMixin,View):
    template_name = 'home/bucket.html'

    def get(self, request):
        objects = tasks.get_all_bucket_objects()
        return render(request, self.template_name, {'objects': objects})


class DeleteBucketObjectView(IsAdminUserMixin,View):
    def get(self, request, key):
        tasks.delete_object_task.delay(key)
        messages.success(request, 'Object deleted successfully', extra_tags='info')
        return redirect('home:bucket')


class DownloadBucketObjectView(IsAdminUserMixin,View):
    def get(self, request, key):
        tasks.download_object_task.delay(key)
        messages.success(request, 'Object downloaded successfully', extra_tags='info')
        return redirect('home:bucket')


class ProductDetailView(View):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        return render(request, 'home/detail.html', {'product': product})
