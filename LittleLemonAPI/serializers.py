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