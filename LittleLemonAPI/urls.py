from django.urls import path
from . import views

urlpatterns = [
    #category
    path('category', views.CategoryView.as_view()),
    path('category/<int:pk>', views.SingleCategoryView.as_view()),
    
    #Menu items
    path('menu-items', views.MenuItemView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),

    #User management
    path('groups/manager/users', views.ManagerView),
    path('groups/manager/users/<int:id>', views.RemoveFromManager),
    path('groups/delivery-crew/users', views.CrewView),
    path('groups/delivery-crew/users/<int:id>', views.RemoveFromDeliveryCrew),

    #Cart management
    path('cart/menu-items', views.CartView.as_view()),

    #Orders
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
]