from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import date

# Categories with class base view
from .models import Category
from .serializers import CategorySerializer
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# MenuItems with modify class base views for request methods
from .models import MenuItem
from .serializers import MenuItemSerializer
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get(self, request):
        if request.user.is_authenticated:
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
        else:
            return JsonResponse({"error": "User is not authenticated"}, status=403)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if request.user.is_authenticated:
                if request.user.groups.filter(name='Manager'):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error":"You are not authorized"}, status=403)
            else:
                return JsonResponse({"error": "User is not authenticated"}, status=403)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        if (instance):
            if request.user.is_authenticated:
                if request.user.groups.filter(name='Manager'):
                    
                    self.perform_destroy(instance)
                else:
                    return Response({"error":"You are not authorized"}, status=403)
            else:
                return JsonResponse({"error": "User is not authenticated"}, status=403)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            if request.user.is_authenticated:
                if request.user.groups.filter(name='Manager'):
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error":"You are not authorized"}, status=403)
            else:
                return JsonResponse({"error": "User is not authenticated"}, status=403)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


# User group management
from django.contrib.auth.models import  User, Group
from .serializers import UserSerializer
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ManagerView(request):
    if request.user.groups.filter(name='Manager'):
        if (request.method == 'GET'):
            users = User.objects.filter(groups=Group.objects.get(name='Manager'))
            serialized_users = UserSerializer(users, many=True)
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "user doesnt exist"}, status=status.HTTP_404_NOT_FOUND)
            manager_group = Group.objects.get(name='Manager')
            manager_group.user_set.add(user)
        return Response({"message": "User has been addded to the manager group"}, status=status.HTTP_200_OK)
    else:
        return Response({"error":"You are not authorized"}, status=403)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def RemoveFromManager(request, id):
    if request.user.groups.filter(name='Manager'):
        user = get_object_or_404(User, pk=id)
        manager_group = Group.objects.get(name='Manager')
        user.groups.remove(manager_group)
        return Response({"message": "User has been removed from the manager group"}, status=200)
    else:
        return Response({"error":"You are not authorized"}, status=403)
    

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def CrewView(request):
    if request.user.groups.filter(name='Manager'):
        if (request.method == 'GET'):
            users = User.objects.filter(groups=Group.objects.get(name='Delivery Crew'))
            serialized_users = UserSerializer(users, many=True)
            return Response(serialized_users.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({"error": "user not provided or doesnt exist"}, status=status.HTTP_404_NOT_FOUND)
            crew_group = Group.objects.get(name='Delivery Crew')
            crew_group.user_set.add(user)
        return Response({"message": "User has been addded to the Delivery Crew group"}, status=status.HTTP_200_OK)
    else:
        return Response({"error":"You are not authorized"}, status=403)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def RemoveFromDeliveryCrew(request, id):
    if request.user.groups.filter(name='Manager'):
        user = get_object_or_404(User, pk=id)
        manager_group = Group.objects.get(name='Delivery Crew')
        user.groups.remove(manager_group)
        return Response({"message": "User has been removed from the Delivery Crew group"}, status=200)
    else:
        return Response({"error":"You are not authorized"}, status=403)


# Cart management 
    
from .models import Cart
from .serializers import CartSerializer
class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Cart.objects.filter(user=user)
    

    def perform_create(self, serializer):
        user = self.request.user
        menuitem_id = self.request.data.get('menuitem_id')
        menuitem = MenuItem.objects.get(pk=menuitem_id)
        quantity = int(self.request.data.get('quantity'))
        unit_price = float(menuitem.price)
      
        existing_cart_item = Cart.objects.filter(user=user, menuitem_id=menuitem_id).first()

        if existing_cart_item:
            existing_cart_item.quantity += quantity
            existing_cart_item.save()
        else:
            serializer.save(user=user, quantity=quantity, unit_price=unit_price, price=(quantity*unit_price))



# Orders
from .models import Order, OrderItem
from .serializers import OrderSerializer          

class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.groups.filter(name='Manager'):
            return Order.objects.all()
        elif self.request.user.groups.count()==0:
            return Order.objects.all().filter(user=self.request.user)
        elif self.request.user.groups.filter(name='Delivery Crew'): 
            return Order.objects.all().filter(delivery_crew=self.request.user)
        else: 
            return Order.objects.all()

    def create(self, request, *args, **kwargs):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)
        if cart_items.count() == 0:
            return Response({"message:": "no items in the cart"})

        new_order = Order.objects.create(
            user=user,
            status=False,
            total= self.get_total_price(self.request.user),
            date=date.today() 
        )

        total_price = 0 
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=new_order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price
            )
            total_price += cart_item.price


        new_order.total = total_price
        new_order.save()

        cart_items.delete()

        serializer = self.get_serializer(new_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
    def get_total_price(self, user):
        total = 0
        items = Cart.objects.all().filter(user=user).all()
        for item in items.values():
            total += item['price']
        return total


class SingleOrderView(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def update(self, request, *args, **kwargs):
        if self.request.user.groups.count()==0: 
            return Response('Not allow', status=401)
        else: 
            return super().update(request, *args, **kwargs)