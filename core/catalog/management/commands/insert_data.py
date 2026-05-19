from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import datetime
from django.utils.text import slugify

from accounts.models import User, Profile
from catalog.models import Product, Category

category_list = [
    'IT',
    'Design',
    'Fun',
    'Mobile',
    'computer',
    'laptop',
    'graphic card',
]

class Command(BaseCommand):
    help = 'inserting dummy data'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        user = User.objects.create_user(email=self.fake.email(),password="a/@1234567")
        profile = Profile.objects.get(user=user)
        profile.first_name = self.fake.first_name()
        profile.last_name = self.fake.last_name()
        profile.description = self.fake.paragraph(nb_sentences=5)
        profile.save()

        categories_by_slug = {}
        for title in category_list:
            slug = slugify(title)
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'title': title}
            )
            categories_by_slug[slug] = category

        category_instances = list(categories_by_slug.values())

        for _ in range(10):
            chosen_category = random.choice(category_instances)
            slug = slugify(title) + f'-{random.randint(100, 999)}'
            try:
                Product.objects.create(
                    title = self.fake.paragraph(nb_sentences=1),
                    slug = slug,
                    description = self.fake.paragraph(nb_sentences=10),
                    price = random.randint(100000, 100000000),
                    stock = random.randint(0, 30),
                    is_active = random.choice([True,False]),
                    category = chosen_category,
                    created_date = datetime.now(),
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating product: {e}'))

        self.stdout.write(self.style.SUCCESS('Successfully inserted dummy data'))