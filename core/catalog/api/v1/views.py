from rest_framework.viewsets import ReadOnlyModelViewSet
from ...models import Product, Category
from .serializers import CategorySerializer,ProductSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter,OrderingFilter
from .paginations import DefaultPagination
from .permissions import IsOwnerReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields = ["title"]
    pagination_class =DefaultPagination
    permission_classes= [IsOwnerReadOnly]

    @action(detail=True, methods=["get"])
    def products(self, request, slug=None):
        category = self.get_object()
        products = category.products.filter(status=True)  # یا product_set
        serializer = ProductSerializer(products, many=True, context={"request": request})
        return Response(serializer.data)


class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.filter(status=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_date"]
    ordering = ["title"]
    pagination_class=DefaultPagination
    permission_classes = [IsOwnerReadOnly]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def toggle_wishlist(self, request, slug=None):
        product = self.get_object()
        user = request.user
        
        # بررسی وجود محصول در لیست علاقه‌مندی‌ها
        wishlist_item = WishlistProductModel.objects.filter(user=user, product=product)
        
        if wishlist_item.exists():
            wishlist_item.delete()
            return Response({"message": "از لیست علاقه‌مندی‌ها حذف شد."}, status=status.HTTP_200_OK)
        else:
            WishlistProductModel.objects.create(user=user, product=product)
            return Response({"message": "به لیست علاقه‌مندی‌ها اضافه شد."}, status=status.HTTP_201_CREATED)
        
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]


    