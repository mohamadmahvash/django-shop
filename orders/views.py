from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.conf import settings
from django.contrib import messages
import requests
import json

from products.models import Product
from .cart import Cart
from .forms import CartAddForm, CouponApplyForm
from .models import Order, OrderItem, Coupon


class CartView(View):
    def get(self, request):
        return render(request, 'orders/cart.html')


class CartAddView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cart.add(product, cd['quantity'])
            return redirect('orders:cart')
        return render(request, 'home/detail.html', {'form': form})


class CartDeleteView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.delete(product)
        return redirect('orders:cart')


class OrderDetailView(LoginRequiredMixin, View):
    form_class = CouponApplyForm

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'orders/order.html', {'order': order, 'form': self.form_class})


class OrderCreateView(LoginRequiredMixin, View):
    def get(self, request):
        cart = Cart(request)
        order = Order.objects.create(user=request.user)
        for item in cart:
            OrderItem.objects.create(order=order, product=item['product'],
                                     price=item['price'], quantity=item['quantity'])
        cart.clear()
        return redirect("orders:order_detail", order.id)


class OrderPaymentView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        request.session["order_pay"] = {"order_id": order.id}

        zp_req_header = {'accept': 'application/json', 'content-type': 'application/json'}
        zp_req_data = {
            'merchant_id': settings.ZP_MERCHANT_ID,
            'amount': order.get_total_price(),
            'currency': 'IRR',
            'description': f'user:{order.user} - time:{order.updated}',
            'callback_url': '***https://test.ir/orders/verify/***',
            'metadata': {
                'mobile': f'{request.user.phone_number}',
                'email': f'{request.user.email}',
            }
        }
        zp_req = requests.post(url=settings.ZP_API_REQUEST, data=json.dumps(zp_req_data), headers=zp_req_header)
        if zp_req.json()["data"]["code"] == 100:
            zp_authority = zp_req.json()["data"]["authority"]
            return redirect(f"https://payment.zarinpal.com/pg/StartPay/{zp_authority}")
        else:
            messages.error(request, 'Error, transaction aborted/ something else went wrong..!'
                           , extra_tags='danger')
            return redirect("home:home")


class OrderVerifyPaymentView(LoginRequiredMixin, View):
    def get(self, request):
        order_id = request.session["order_pay"]["order_id"]
        order = get_object_or_404(Order, id=order_id)
        zp_authority = request.GET.get("Authority")
        zp_status = request.GET.get("Status")
        if zp_status == "OK":
            zp_req_header = {'accept': 'application/json', 'content-type': 'application/json'}
            zp_req_data = {
                'merchant_id': settings.ZP_MERCHANT_ID,
                'amount': order.get_total_price(),
                'authority': zp_authority,
            }
            zp_verify_req = requests.post(url=settings.ZP_API_VERIFY,
                                          data=json.dumps(zp_req_data), headers=zp_req_header)
            if zp_verify_req.json()["data"]["code"] == 100:
                order.paid = True
                order.save()
                messages.success(request, 'your payment was successfully', extra_tags='success')
                return redirect("home:home")
            else:
                zp_error_code = zp_verify_req.json()["errors"]["code"]
                zp_error_message = zp_verify_req.json()["errors"]["message"]
                messages.error(request, f'Error{zp_error_code}, {zp_error_message}', extra_tags='danger')
                return redirect("home:home")
        else:
            messages.error(request, 'Error, transaction aborted/ something else went wrong..!'
                           , extra_tags='danger')
            return redirect("home:home")


class CouponApplyView(LoginRequiredMixin, View):
    form_class = CouponApplyForm

    def post(self, request, order_id):
        now = timezone.now()
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                coupon = Coupon.objects.get(code__exact=cd['code'], valid_from__lte=now, valid_to__gte=now)
            except Coupon.DoesNotExist:
                messages.warning(request, 'this coupon does not exist', extra_tags='warning')
                return redirect("orders:order_detail", order_id)
            order = Order.objects.get(id=order_id)
            order.discount = coupon.discount
            order.save()
            messages.success(request, f'{coupon.discount}% discount applied', extra_tags='success')
        return redirect("orders:order_detail", order_id)
