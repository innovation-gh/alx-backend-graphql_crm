# CRM GraphQL Application with Celery Beat

A Django-based Customer Relationship Management (CRM) system with GraphQL API and automated task scheduling using Celery Beat.

## Features

- GraphQL API for customers, orders, and products
- Automated task scheduling with Celery Beat
- Background report generation
- System health monitoring
- Automated cleanup and reminder tasks

## Prerequisites

- Python 3.8+
- Redis server
- Git

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start Redis

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Windows:
Download and install Redis from: https://github.com/microsoftarchive/redis/releases

### 5. Configure Django Settings

Ensure your `crm/settings.py` includes:

```python
INSTALLED_APPS = [
    # ... other apps
    'django_celery_beat',
    'graphene_django',
]

# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}
```

### 6. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py migrate django_celery_beat
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Make Cron Scripts Executable

```bash
chmod +x crm/cron_jobs/clean_inactive_customers.sh
chmod +x crm/cron_jobs/send_order_reminders.py
```

## Running the Application

### 1. Start Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at: http://localhost:8000/graphql

### 2. Start Redis Server

```bash
redis-server
```

### 3. Start Celery Worker

In a new terminal:
```bash
celery -A crm worker --loglevel=info
```

### 4. Start Celery Beat Scheduler

In another terminal:
```bash
celery -A crm beat --loglevel=info
```

### 5. Install System Cron Jobs (Optional)

For system-level cron jobs:

```bash
# Install customer cleanup cron job
crontab crm/cron_jobs/customer_cleanup_crontab.txt

# Install order reminders cron job  
crontab crm/cron_jobs/order_reminders_crontab.txt

# View installed cron jobs
crontab -l
```

### 6. Setup django-crontab Jobs

```bash
# Add django-crontab jobs to system crontab
python manage.py crontab add

# Show current crontab jobs
python manage.py crontab show

# Remove crontab jobs (if needed)
python manage.py crontab remove
```

## Verification Steps

### 1. Test GraphQL Endpoint

Visit http://localhost:8000/graphql and run:

```graphql
query {
  customers {
    id
    name
    email
  }
  orders {
    id
    totalAmount
    orderDate
  }
}
```

### 2. Verify Celery Tasks

```bash
# Test the CRM report task manually
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()
```

### 3. Check Log Files

Monitor the following log files to verify everything is working:

```bash
# CRM report logs
tail -f /tmp/crm_report_log.txt

# Customer cleanup logs  
tail -f /tmp/customer_cleanup_log.txt

# Order reminder logs
tail -f /tmp/order_reminders_log.txt

# Heartbeat logs
tail -f /tmp/crm_heartbeat_log.txt

# Low stock update logs
tail -f /tmp/low_stock_updates_log.txt
```

## Scheduled Tasks Overview

| Task | Schedule | Description | Log File |
|------|----------|-------------|----------|
| CRM Report | Weekly (Mon 6AM) | Generate weekly report via Celery Beat | `/tmp/crm_report_log.txt` |
| Customer Cleanup | Weekly (Sun 2AM) | Remove inactive customers | `/tmp/customer_cleanup_log.txt` |
| Order Reminders | Daily (8AM) | Send order reminders | `/tmp/order_reminders_log.txt` |
| Heartbeat Logger | Every 5 minutes | System health check | `/tmp/crm_heartbeat_log.txt` |
| Low Stock Updates | Every 12 hours | Update low stock products | `/tmp/low_stock_updates_log.txt` |

## Project Structure

```
crm/
├── __init__.py
├── celery.py                 # Celery app configuration
├── settings.py               # Django settings with Celery config
├── tasks.py                  # Celery tasks
├── cron.py                   # django-crontab functions
├── schema.py                 # GraphQL schema and mutations
├── urls.py                   # URL configuration
├── wsgi.py                   # WSGI configuration
├── cron_jobs/
│   ├── clean_inactive_customers.sh
│   ├── customer_cleanup_crontab.txt
│   ├── send_order_reminders.py
│   └── order_reminders_crontab.txt
└── README.md                 # This file
```

## Troubleshooting

### Redis Connection Issues

1. Check if Redis is running:
   ```bash
   redis-cli ping
   ```
   Should return: `PONG`

2. Check Redis server status:
   ```bash
   sudo systemctl status redis-server  # Linux
   brew services list | grep redis     # macOS
   ```

### Celery Issues

1. Check worker status:
   ```bash
   celery -A crm inspect active
   ```

2. Purge all tasks:
   ```bash
   celery -A crm purge
   ```

3. Monitor task execution:
   ```bash
   celery -A crm events
   ```

### Cron Job Issues

1. Check system cron logs:
   ```bash
   sudo tail -f /var/log/syslog | grep CRON  # Linux
   tail -f /var/log/cron                     # macOS
   ```

2. Test scripts manually:
   ```bash
   ./crm/cron_jobs/clean_inactive_customers.sh
   python crm/cron_jobs/send_order_reminders.py
   ```

### Django-crontab Issues

1. Check if jobs are added:
   ```bash
   python manage.py crontab show
   ```

2. Test cron functions manually:
   ```bash
   python manage.py shell
   >>> from crm.cron import log_crm_heartbeat
   >>> log_crm_heartbeat()
   ```

## Environment Variables

Create a `.env` file for production settings:

```bash
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
REDIS_URL=redis://localhost:6379/0
```

## Production Deployment

For production deployment:

1. Use environment variables for sensitive settings
2. Set up proper logging configuration
3. Use process managers like Supervisor or systemd for Celery processes
4. Configure Redis for persistence and security
5. Set up monitoring for task failures

## Development Commands

```bash
# Run Django server
python manage.py runserver

# Run Celery worker
celery -A crm worker --loglevel=info

# Run Celery Beat
celery -A crm beat --loglevel=info

# Add django-crontab jobs
python manage.py crontab add

# Create migrations
python manage.py makemigrations

# Apply migrations  
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Support

For issues and questions:
- Check the troubleshooting section above
- Review Django, Celery, and Redis documentation
- Check log files for detailed error messages

## License

This project is for educational purposes as part of the ALX Backend Specialization program.