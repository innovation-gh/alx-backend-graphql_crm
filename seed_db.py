import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_data():
    # Clear existing data
    Customer.objects.all().delete()
    Product.objects.all().delete()
    Order.objects.all().delete()

    # Create customers
    customers = [
        Customer(name="John Doe", email="john@example.com", phone="+1234567890"),
        Customer(name="Jane Smith", email="jane@example.com", phone="987-654-3210"),
    ]
    Customer.objects.bulk_create(customers)

    # Create products
    products = [
        Product(name="Laptop", price=999.99, stock=10),
        Product(name="Phone", price=699.99, stock=15),
        Product(name="Tablet", price=399.99, stock=20),
    ]
    Product.objects.bulk_create(products)

    # Create orders
    customer = Customer.objects.first()
    products = list(Product.objects.all())
    order = Order(customer=customer)
    order.save()
    order.products.set(products[:2])  # Add first two products
    order.save()

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()