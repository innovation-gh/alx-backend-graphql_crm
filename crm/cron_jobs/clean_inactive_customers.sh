#!/bin/bash

# Customer cleanup script - deletes customers with no orders since a year ago
# Run via cron job every Sunday at 2:00 AM

# Get the current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Define the log file
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Navigate to the Django project directory (adjust path as needed)
# Assuming the script is in crm/cron_jobs and Django project root is two levels up
cd "$(dirname "$0")/../.." || exit 1

# Execute Django management command to delete inactive customers
# This command finds customers with no orders in the last year and deletes them
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from customers.models import Customer
from orders.models import Order

# Calculate date one year ago (365 days)
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders since 365 days ago
inactive_customers = Customer.objects.filter(
    orders__isnull=True
).union(
    Customer.objects.exclude(
        orders__created_at__gte=one_year_ago
    )
).distinct()

# Count customers to delete
count = inactive_customers.count()

# Delete inactive customers
inactive_customers.delete()

# Print the count for logging
print(count)
" 2>/dev/null)

# Check if the command was successful
if [ $? -eq 0 ]; then
    # Log the successful cleanup
    echo "[$TIMESTAMP] Successfully deleted $DELETED_COUNT inactive customers" >> "$LOG_FILE"
else
    # Log the error
    echo "[$TIMESTAMP] Error: Failed to delete inactive customers" >> "$LOG_FILE"
fi