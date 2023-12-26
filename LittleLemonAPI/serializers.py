from rest_framework import serializers

from .models import Category
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug','title']


from .models import MenuItem
class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id','title','price','feactured','category', 'category_id']



from django.contrib.auth.models import Group
class GroupSerializer( serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name',]

from django.contrib.auth.models import User
class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name', 'email', 'groups']
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False}
        }


class UserSerializerForCart(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']  

from .models import Cart
class CartSerializer(serializers.ModelSerializer):
    user = UserSerializerForCart(read_only=True)
    menuitems = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['user','menuitems', 'menuitem_id','quantity','unit_price','price']
        extra_kwargs = {
            'unit_price': {'required': False,},
            'price': {'required':False,},
        }


from .models import OrderItem
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'price']


from .models import Order
class OrderSerializer(serializers.ModelSerializer):
    orderitem = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew','status', 'date', 'total', 'orderitem']