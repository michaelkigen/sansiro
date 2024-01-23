from rest_framework.routers import DefaultRouter
from .views import CartViewSet, MenuAPiView, MenuupdateAPiView,Orderdetailed, AddToCartViewSet,CheckoutView,ProcessOrderView,OrdererdFood,webhook_notification
#from rest_framework_nested.routers import DefaultRouter, NestedSimpleRouter
from django.urls import path, include

# Create the main router
router = DefaultRouter()

# router.register('food', MenuAPiView)
router.register('cart', CartViewSet , basename='cart' )

#router.register('carting', Add_to_cart)

# Create the nested router for cart items
# cart_router = NestedSimpleRouter(router, 'cart', lookup='cart')
# cart_router.register('item', AddToCartViewSet, basename='items')

nested_routes = [ 
    path('cart/<cart_id>/item/<pk>/', AddToCartViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy', 'patch':'partial_update'}), name='cart-item-detail'),
    path('cart/<cart_id>/item/', AddToCartViewSet.as_view({'get': 'list', 'post': 'create' , 'delete': 'destroy' }), name='cart-item-list'),
]

urlpatterns = [
    path("", include(router.urls)),
    path("", include(nested_routes)),
    path("order/", CheckoutView.as_view()),
    path("process/", ProcessOrderView.as_view()),
    path("food/", MenuAPiView.as_view({'get': 'list','post': 'create'})),
    path("food/<uuid:food_id>/", MenuupdateAPiView.as_view()),
    path("order/<uuid:order_id>/", Orderdetailed.as_view()),
    path('webhook/notification/', webhook_notification, name='webhook_notification'),
    path("orderd-food/", OrdererdFood.as_view())
]