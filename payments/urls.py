from django.contrib import admin
from django.urls import path
from .views import SubmitView, CheckTransactionOnline, ConfirmView , PaymentTransactionListView,Redeem_points,SearchTransaction

urlpatterns = [
    path('send/', SubmitView.as_view(), name='submit'),
    path('confirm/', ConfirmView.as_view(), name='confirm'),
    path('check-online/', CheckTransactionOnline.as_view(), name='confirm-online'),
    path('transactions/',PaymentTransactionListView.as_view(), name = 'transaction_history' ),
    path('searchtrans/<int:trans_id>/',SearchTransaction.as_view(), name = 'search_trans' ),
    path('redeem/',Redeem_points.as_view(),name='redeem_points')
]