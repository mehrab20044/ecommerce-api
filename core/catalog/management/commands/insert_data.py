import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction
from django.utils.text import slugify
from faker import Faker

from accounts.models import Profile, User
from cart.models import CartItemModel, CartModel
from catalog.models import Category, Product, ProductStatusType
from order.models import OrderItemModel, OrderModel, OrderStatus
from payment.models import PaymentModel, PaymentStatus


CATEGORY_LIST = [
    "Electronics",
    "Mobile",
    "Laptop",
    "Computer",
    "Accessories",
    "Gaming",
    "Smart Home",
]


class Command(BaseCommand):
    help = "Insert fake ecommerce data for development and payment testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=5,
            help="Number of fake users to create.",
        )
        parser.add_argument(
            "--products",
            type=int,
            default=30,
            help="Number of fake products to create.",
        )
        parser.add_argument(
            "--carts",
            type=int,
            default=5,
            help="Number of fake carts with items to create.",
        )
        parser.add_argument(
            "--orders",
            type=int,
            default=10,
            help="Number of fake orders with order items to create.",
        )
        parser.add_argument(
            "--payments",
            type=int,
            default=5,
            help="Number of fake payments to create for generated orders.",
        )
        parser.add_argument(
            "--password",
            default="a/@1234567",
            help="Password used for all generated users.",
        )
        parser.add_argument(
            "--locale",
            default="en_US",
            help="Faker locale, for example en_US or fa_IR.",
        )

    def handle(self, *args, **options):
        self.fake = Faker(options["locale"])
        users_count = max(options["users"], 0)
        products_count = max(options["products"], 0)
        carts_count = max(options["carts"], 0)
        orders_count = max(options["orders"], 0)
        payments_count = max(options["payments"], 0)
        password = options["password"]

        with transaction.atomic():
            categories = self._create_categories()
            users = self._create_users(users_count, password)
            products = self._create_products(products_count, categories)
            users = self._available_users(users, users_count, password)
            products = self._available_products(products, categories)
            self._create_carts(carts_count, users, products)
            orders = self._create_orders(orders_count, users, products)
            payments = self._create_payments(payments_count, orders)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully inserted fake data: "
                f"{users_count} users, {len(categories)} categories, "
                f"{products_count} products, {carts_count} carts, "
                f"{orders_count} orders, {payments} payments."
            )
        )

    def _create_categories(self):
        categories = []
        for title in CATEGORY_LIST:
            category, _ = Category.objects.get_or_create(
                slug=slugify(title),
                defaults={"title": title},
            )
            categories.append(category)
        return categories

    def _create_users(self, count, password):
        users = []
        for _ in range(count):
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            user = User.objects.create_user(
                phone_number=self._unique_phone_number(),
                email=self._unique_email(),
                password=password,
                first_name=first_name,
                is_active=True,
                is_verified=True,
            )
            users.append(user)

            Profile.objects.filter(user=user).update(
                first_name=first_name,
                last_name=last_name,
                email=user.email,
                description=self.fake.paragraph(nb_sentences=5),
            )
        return users

    def _create_products(self, count, categories):
        products = []
        for _ in range(count):
            title = self.fake.unique.sentence(nb_words=4).rstrip(".")
            product = Product.objects.create(
                title=title,
                slug=self._unique_product_slug(title),
                description=self.fake.paragraph(nb_sentences=10),
                price=Decimal(random.randint(100_000, 90_000_000)),
                discount_percent=random.choice([0, 5, 10, 15, 20, 25, 30]),
                stock=random.randint(0, 30),
                status=random.choice(
                    [
                        ProductStatusType.publish.value,
                        ProductStatusType.draft.value,
                    ]
                ),
                category=random.choice(categories),
            )
            products.append(product)
        return products

    def _available_users(self, created_users, requested_count, password):
        if created_users:
            return created_users

        existing_users = list(User.objects.order_by("-id")[:5])
        if existing_users:
            return existing_users

        return self._create_users(max(requested_count, 1), password)

    def _available_products(self, created_products, categories):
        products = [
            product
            for product in created_products
            if product.status == ProductStatusType.publish.value
        ]
        if products:
            return products

        existing_products = list(
            Product.objects.filter(status=ProductStatusType.publish.value)
            .order_by("-id")[:20]
        )
        if existing_products:
            return existing_products

        title = self.fake.unique.sentence(nb_words=4).rstrip(".")
        product = Product.objects.create(
            title=title,
            slug=self._unique_product_slug(title),
            description=self.fake.paragraph(nb_sentences=8),
            price=Decimal(random.randint(100_000, 90_000_000)),
            discount_percent=0,
            stock=random.randint(5, 30),
            status=ProductStatusType.publish.value,
            category=random.choice(categories),
        )
        return [product]

    def _create_carts(self, count, users, products):
        for user in random.sample(users, min(count, len(users))):
            cart, _ = CartModel.objects.get_or_create(user=user)
            selected_products = random.sample(
                products,
                min(random.randint(1, 4), len(products)),
            )
            for product in selected_products:
                CartItemModel.objects.update_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": random.randint(1, 3)},
                )

    def _create_orders(self, count, users, products):
        orders = []
        for _ in range(count):
            user = random.choice(users)
            first_name = self.fake.first_name()
            last_name = self.fake.last_name()
            order = OrderModel.objects.create(
                user=user,
                status=OrderStatus.pending,
                first_name=first_name,
                last_name=last_name,
                phone_number=user.phone_number,
                address=self.fake.address(),
                postal_code=self.fake.postcode(),
            )

            selected_products = random.sample(
                products,
                min(random.randint(1, 4), len(products)),
            )
            for product in selected_products:
                OrderItemModel.objects.create(
                    order=order,
                    product=product,
                    product_title=product.title,
                    product_price=product.get_price,
                    quantity=random.randint(1, 3),
                )
            orders.append(order)
        return orders

    def _create_payments(self, count, orders):
        payable_orders = [
            order
            for order in orders
            if order.total_price > 0
            and not PaymentModel.objects.filter(order=order).exists()
        ]
        payments_count = min(count, len(payable_orders))

        for order in random.sample(payable_orders, payments_count):
            payment_status = random.choice(
                [
                    PaymentStatus.PENDING,
                    PaymentStatus.SUCCESS,
                    PaymentStatus.FAILED,
                ]
            )
            payment = PaymentModel.objects.create(
                user=order.user,
                order=order,
                amount=order.total_price,
                status=payment_status,
                authority=f"A{random.randint(10**20, 10**21 - 1)}",
            )

            if payment.status == PaymentStatus.SUCCESS:
                payment.ref_id = str(random.randint(10**8, 10**10 - 1))
                payment.save(update_fields=["ref_id"])
                order.status = OrderStatus.paid
                order.save(update_fields=["status"])
            elif payment.status == PaymentStatus.FAILED:
                order.status = OrderStatus.canceled
                order.save(update_fields=["status"])

        return payments_count

    def _unique_email(self):
        while True:
            email = self.fake.unique.email()
            if not User.objects.filter(email=email).exists():
                return email

    def _unique_phone_number(self):
        while True:
            phone_number = f"09{random.randint(100_000_000, 999_999_999)}"
            if not User.objects.filter(phone_number=phone_number).exists():
                return phone_number

    def _unique_product_slug(self, title):
        base_slug = slugify(title) or "product"

        for _ in range(10):
            slug = f"{base_slug}-{random.randint(1000, 9999)}"
            if not Product.objects.filter(slug=slug).exists():
                return slug

        raise IntegrityError("Could not generate a unique product slug.")
