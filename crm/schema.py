import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from .models import Customer, Product, Order

# Relay Node Types (with filtering)
class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        filter_fields = ["name", "email", "phone"]
        interfaces = (graphene.relay.Node,)

class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = ["name", "price", "stock"]
        interfaces = (graphene.relay.Node,)

class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = ["customer__name", "customer__email", "products__name", "total_amount"]
        interfaces = (graphene.relay.Node,)

# Regular Types (for non-relay queries/mutations)
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

# New types for stock update mutation
class UpdatedProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    old_stock = graphene.Int()
    new_stock = graphene.Int()

class UpdateLowStockProductsPayload(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(UpdatedProductType)
    count = graphene.Int()

# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        # Validate phone format
        if input.phone and not re.match(r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$', input.phone):
            raise ValidationError("Invalid phone format. Use +1234567890 or 123-456-7890")
        
        try:
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(customer=customer, message="Customer created successfully")
        except ValidationError as e:
            if hasattr(e, 'message_dict') and 'email' in e.message_dict:
                raise ValidationError("Email already exists")
            raise e

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        inputs = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    @transaction.atomic
    def mutate(cls, root, info, inputs):
        customers = []
        errors = []
        
        for input in inputs:
            try:
                # Validate phone format
                if input.phone and not re.match(r'^(\+\d{1,15}|\d{3}-\d{3}-\d{4})$', input.phone):
                    raise ValidationError("Invalid phone format")
                
                customer = Customer(
                    name=input.name,
                    email=input.email,
                    phone=input.phone
                )
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append("Failed to create customer " + input.email + ": " + str(e))
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            raise ValidationError("Price must be positive")
        if input.stock and input.stock < 0:
            raise ValidationError("Stock cannot be negative")
            
        product = Product(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        product.save()
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    @classmethod
    def mutate(cls, root, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer does not exist")
        
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(pk=product_id)
                products.append(product)
            except Product.DoesNotExist:
                raise ValidationError("Product with ID " + str(product_id) + " does not exist")
        
        if not products:
            raise ValidationError("At least one product is required")
        
        order = Order(customer=customer)
        order.save()  # First save to get ID
        order.products.set(products)  # Set many-to-many relationship
        order.total_amount = sum(p.price for p in products)
        order.save()  # Save again with calculated total
        
        return CreateOrder(order=order)

class UpdateLowStockProducts(graphene.Mutation):
    """
    GraphQL mutation that updates low-stock products (stock < 10)
    by incrementing their stock by 10 units.
    """
    
    class Arguments:
        pass  # No arguments needed for this mutation
    
    Output = UpdateLowStockProductsPayload
    
    @classmethod
    def mutate(cls, root, info):
        try:
            # Query products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            updated_products = []
            
            # Update each low stock product
            for product in low_stock_products:
                old_stock = product.stock
                # Increment stock by 10 (simulating restocking)
                product.stock += 10
                product.save()
                
                updated_products.append(UpdatedProductType(
                    id=product.id,
                    name=product.name,
                    old_stock=old_stock,
                    new_stock=product.stock
                ))
            
            return UpdateLowStockProductsPayload(
                success=True,
                message="Successfully updated " + str(len(updated_products)) + " low-stock products",
                updated_products=updated_products,
                count=len(updated_products)
            )
            
        except Exception as e:
            return UpdateLowStockProductsPayload(
                success=False,
                message="Error updating low-stock products: " + str(e),
                updated_products=[],
                count=0
            )

# Combine all mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    # Hello field for health checking
    hello = graphene.String()
    
    # Relay filterable connections
    all_customers = DjangoFilterConnectionField(CustomerNode)
    all_products = DjangoFilterConnectionField(ProductNode)
    all_orders = DjangoFilterConnectionField(OrderNode)

    # Regular queries
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_hello(self, info):
        return "Hello World!"

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)
