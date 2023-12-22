from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin


# Categories
from .models import Category
from .serializers import CategorySerializer
class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SingleCategoryView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# MenuItems
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
                    return Response({"error":"You are not authorized"}, status=401)
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
                    return Response({"error":"You are not authorized"}, status=401)
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
                    return Response({"error":"You are not authorized"}, status=401)
            else:
                return JsonResponse({"error": "User is not authenticated"}, status=403)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  


