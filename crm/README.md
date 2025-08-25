# CRM GraphQL Application with Celery Tasks

This Django application provides a GraphQL API for managing customers, products, and orders, with automated weekly reporting using Celery and Redis.

## Features

- GraphQL API with CRUD operations for customers, products, and orders
- Automated weekly CRM reports using Celery Beat
- Redis-based task queue
- Bulk operations support
- Stock management and low-stock alerts

## Prerequisites

- Python 3.8+
- Redis server
- Django 4.2+

## Installation and Setup

### 1. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS (with Homebrew):**
```bash
brew install redis
brew services start redis
```

**Windows:**
Download and install from [Redis official website](https://redis.io/download)

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Django Settings

Ensure your `crm/settings.py` includes:
- `django_celery_beat` in `INSTALLED_APPS`
- Celery configuration with Redis broker
- Celery Beat schedule configuration

### 4. Run Database Migrations

```bash
python manage.py migrate
```

This will create the necessary database tables including those for django-celery-beat.

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Running the Application

### 1. Start Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at: `http://127.0.0.1:8000/graphql/`

### 2. Start Celery Worker

Open a new terminal and run:

```bash
celery -A crm worker -l info
```

This starts the Celery worker process that will execute tasks.

### 3. Start Celery Beat Scheduler

Open another terminal and run:

```bash
celery -A crm beat -l info
```

This starts the Celery Beat scheduler that will trigger periodic tasks.

### 4. Verify Setup

Check that Redis is running:
```bash
redis-cli ping
```
Should return `PONG`.

## Monitoring and Logs

### CRM Report Logs

Weekly reports are logged to `/tmp/crm_report_log.txt`. Each entry includes:
- Timestamp
- Total number of customers
- Total number of orders  
- Total revenue

Example log entry:
```
2024-01-15 06:00:01 - Report: 25 customers, 150 orders, 5420.50 revenue.
```

### Django Logs

Application logs are written to `/tmp/django_crm.log`.

### Viewing Logs

```bash
# View CRM report logs
tail -f /tmp/crm_report_log.txt

# View Django application logs
tail -f /tmp/django_crm.log
```

## GraphQL Operations

### Sample Queries

**Get all customers:**
```graphql
query {
  customers {
    id
    name
    email
    phone
  }
}
```

**Get all orders with customer details:**
```graphql
query {
  orders {
    id
    customer {
      name
      email
    }
    products {
      name
      price
    }
    totalAmount
    orderDate
  }
}
```

### Sample Mutations

**Create a customer:**
```graphql
mutation {
  createCustomer(input: {
    name: "John Doe"
    email: "john@example.com"
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
    }
    message
  }
}
```

**Update low stock products:**
```graphql
mutation {
  updateLowStockProducts {
    success
    message
    count
    updatedProducts {
      id
      name
      oldStock
      newStock
    }
  }
}
```

## Celery Tasks

### Available Tasks

1. **`generate_crm_report`** - Generates weekly CRM report (scheduled for Mondays at 6:00 AM)
2. **`test_task`** - Simple test task to verify Celery is working

### Manual Task Execution

You can manually trigger tasks using Django shell:

```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report, test_task

# Execute report generation
result = generate_crm_report.delay()
print(result.get())

# Execute test task
result = test_task.delay()
print(result.get())
```

## Troubleshooting

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis server is running: `redis-cli ping`
   - Check Redis configuration in settings.py

2. **Celery Worker Not Processing Tasks**
   - Restart Celery worker: `celery -A crm worker -l info`
   - Check for error messages in worker logs

3. **Tasks Not Scheduled**
   - Ensure Celery Beat is running: `celery -A crm beat -l info`
   - Check database for scheduled tasks: `python manage.py shell` then `from django_celery_beat.models import PeriodicTask; print(PeriodicTask.objects.all())`

4. **Permission Error on Log Files**
   ```bash
   sudo touch /tmp/crm_report_log.txt
   sudo chmod 666 /tmp/crm_report_log.txt
   ```

### Development vs Production

For production deployment:
- Remove the test task from `CELERY_BEAT_SCHEDULE`
- Use a proper message broker setup (Redis Cluster, RabbitMQ)
- Configure proper logging with log rotation
- Use process managers like Supervisor for Celery processes
- Set up monitoring with tools like Flower

## File Structure

```
crm/
├── __init__.py              # Celery app initialization
├── celery.py               # Celery configuration
├── settings.py             # Django settings with Celery config
├── tasks.py                # Celery task definitions
├── models.py               # Django models
├── schema.py               # GraphQL schema
├── urls.py                 # URL configuration
└── README.md               # This file
requirements.txt            # Python dependencies
```

## Testing

Run Django tests:
```bash
python manage.py test
```

Test Celery tasks:
```bash
python manage.py shell
>>> from crm.tasks import test_task
>>> result = test_task.delay()
>>> result.get()
```