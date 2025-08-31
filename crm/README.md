# CRM GraphQL Application Setup

## Setup Instructions

### 1. Install Redis and dependencies
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

### 2. Run migrations
```bash
python manage.py migrate
```

### 3. Start Celery worker
```bash
celery -A crm worker -l info
```

### 4. Start Celery Beat
```bash
celery -A crm beat -l info
```

### 5. Verify logs in /tmp/crm_report_log.txt
```bash
tail -f /tmp/crm_report_log.txt
```