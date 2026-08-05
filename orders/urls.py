from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', views.CartAddView.as_view(), name='cart_add'),
    path('cart/delete/<int:product_id>/', views.CartDeleteView.as_view(), name='cart_delete'),
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('detail/<int:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('payment/<int:order_id>/', views.OrderPaymentView.as_view(), name='order_payment'),
    path('verify/', views.OrderVerifyPaymentView.as_view(), name='order_verify_payment'),
]
