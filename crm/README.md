Here are the simplified steps for your CRM setup.

---

## CRM Setup

### Setup Steps

1.  **Install Redis and dependencies**
    * First, install the Python dependencies:
        `pip install -r requirements.txt`
    * Next, install and start Redis. Choose the command for your operating system:
        * **Ubuntu/Debian**:
            `sudo apt install redis-server`
            `sudo systemctl start redis-server`
        * **macOS**:
            `brew install redis`
            `brew services start redis`

2.  **Run migrations**
    `python manage.py migrate`

3.  **Start Celery worker**
    `celery -A crm worker -l info`

4.  **Start Celery Beat**
    `celery -A crm beat -l info`

5.  **Verify logs**
    `tail -f /tmp/crm_report_log.txt`