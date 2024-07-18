from django.db import models
from rest_framework.response import Response
from rest_framework import viewsets

from products.models import Review, Category, Product
from products.serializer import ProductSerializer, CategorySerializer, ReviewSerializer
from rest_framework.decorators import action
from rest_framework import status


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        product = request.data.get('product')

        if Review.objects.filter(user=user, product=product).exists():
            return Response(
                {"detail": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def list(self, request, *args, **kwargs):
        category = request.query_params.get('categories', None)
        if category:
            self.queryset = self.queryset.filter(category=category)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        related_products = Product.objects.filter(category=instance.category).exclude(id=instance.id)[:5]
        related_serializer = ProductSerializer(related_products, many=True)
        return Response({
            'product': serializer.data,
            'related_products': related_serializer.data
        })

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        category = request.query_params.get('categories', None)
        if category:
            top_products = Product.objects.filter(category=category).annotate(avg_rating=models.Mvg('reviews__rating')).order_by('-avg_rating')[:5]
            serializer = ProductSerializer(top_products, many=True)
            return Response(serializer.data)
        top_products = Product.objects.annotate(avg_rating=models.Avg('reviews__rating')).order_by('-avg_rating')[:5]
        serializer = ProductSerializer(top_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def average_rating(self, request, pk=None):
        product = self.get_object()
        reviews = product.reviews.all()

        if reviews.count() == 0:
            return Response({"average_rating": "No reviews yet!"})

        avg_rating = sum([review.rating for review in reviews]) / reviews.count()        # 49:00
        return Response({"average_rating": avg_rating})
