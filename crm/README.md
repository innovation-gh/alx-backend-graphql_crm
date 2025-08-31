# CRM GraphQL Application with Celery Beat

A Django-based CRM system with GraphQL API and automated task scheduling.

## Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Redis
```bash
# Ubuntu/Debian
sudo apt install redis-server && sudo systemctl start redis-server

# macOS  
brew install redis && brew services start redis
```

### 3. Run Migrations
```bash
python manage.py migrate
python manage.py migrate django_celery_beat
```

### 4. Start Services

**Terminal 1 - Django:**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
celery -A crm worker --loglevel=info
```

**Terminal 3 - Celery Beat:**
```bash
celery -A crm beat --loglevel=info
```

### 5. Setup django-crontab (Optional)
```bash
python manage.py crontab add
```

## Verification

Check logs to verify tasks are running:
```bash
tail -f /tmp/crm_report_log.txt
```

## Configuration

All Celery Beat schedules and django-crontab jobs are configured in `crm/settings.py`:
- Celery broker/backend settings
- CELERY_BEAT_SCHEDULE for periodic tasks  
- CRONJOBS for django-crontab tasks

## GraphQL Endpoint

Access GraphQL interface at: http://localhost:8000/graphql

## Scheduled Tasks

| Task | Frequency | Log File |
|------|-----------|----------|
| CRM Report | Weekly (Mon 6AM) | `/tmp/crm_report_log.txt` |
| Heartbeat | Every 5 min | `/tmp/crm_heartbeat_log.txt` |
| Stock Updates | Every 12 hours | `/tmp/low_stock_updates_log.txt` |