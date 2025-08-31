# CRM Setup

## Setup Steps

### Install Redis and dependencies

```bash
pip install -r requirements.txt
```

Install Redis:

```bash
# Ubuntu/Debian
sudo apt install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis
```

### Run migrations

```bash
python manage.py migrate
```

### Start Celery worker

```bash
celery -A crm worker -l info
```

### Start Celery Beat

```bash
celery -A crm beat -l info
```

### Verify logs in /tmp/crm_report_log.txt

```bash
tail -f /tmp/crm_report_log.txt
```