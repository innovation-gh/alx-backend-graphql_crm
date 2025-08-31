from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
import os
from django.db import connection
from graphene import Schema
from graphene.test import Client
from .schema import schema
import logging

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    """
    Generate a weekly CRM report using GraphQL queries and log to file.
    """
    try:
        # Create GraphQL client
        client = Client(schema)
        
        # GraphQL query to fetch report data
        query = """
        query {
            customers {
                id
            }
            orders {
                id
                totalAmount
            }
        }
        """
        
        # Execute the query
        result = client.execute(query)
        
        if result.get('errors'):
            logger.error(f"GraphQL query errors: {result['errors']}")
            return "Error executing GraphQL query"
        
        data = result.get('data', {})
        
        # Calculate metrics
        total_customers = len(data.get('customers', []))
        orders = data.get('orders', [])
        total_orders = len(orders)
        total_revenue = sum(float(order.get('totalAmount', 0) or 0) for order in orders)
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create report message
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue."
        
        # Log to file
        log_file_path = '/tmp/crm_report_log.txt'
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # Write to log file
        with open(log_file_path, 'a') as log_file:
            log_file.write(report_message + '\n')
        
        # Also log to Django logger
        logger.info(f"CRM Report generated: {report_message}")
        
        return report_message
        
    except Exception as e:
        error_message = f"Error generating CRM report: {str(e)}"
        logger.error(error_message)
        
        # Still try to log the error to file
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_log = f"{timestamp} - Error: {error_message}"
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(error_log + '\n')
        except:
            pass
        
        return error_message

@shared_task
def test_task():
    """
    Simple test task to verify Celery is working.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"{timestamp} - Celery test task executed successfully"
    
    with open('/tmp/crm_report_log.txt', 'a') as log_file:
        log_file.write(message + '\n')
    
    return message