from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime
import os
import requests
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
        
        # Calculate metrics with better error handling
        customers = data.get('customers', [])
        total_customers = len(customers) if customers else 0
        
        orders = data.get('orders', [])
        total_orders = len(orders) if orders else 0
        
        # More robust revenue calculation
        total_revenue = 0
        if orders:
            for order in orders:
                amount = order.get('totalAmount', 0)
                if amount:
                    try:
                        total_revenue += float(amount)
                    except (ValueError, TypeError):
                        pass  # Skip invalid amounts
        
        # Format timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create report message
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue:.2f} revenue."
        
        # Log to file
        log_file_path = '/tmp/crm_report_log.txt'
        
        # Ensure the directory exists
        log_dir = os.path.dirname(log_file_path)
        if log_dir:  # Only create if there's actually a directory
            os.makedirs(log_dir, exist_ok=True)
        
        # Write to log file with better error handling
        try:
            with open(log_file_path, 'a', encoding='utf-8') as log_file:
                log_file.write(report_message + '\n')
        except IOError as e:
            logger.error(f"Failed to write to log file: {e}")
            # Don't return error here, just log it
        
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
            with open('/tmp/crm_report_log.txt', 'a', encoding='utf-8') as log_file:
                log_file.write(error_log + '\n')
        except Exception:
            # If we can't even log the error, just pass
            pass
        
        return error_message

@shared_task
def test_task():
    """
    Simple test task to verify Celery is working.
    """
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        message = f"{timestamp} - Celery test task executed successfully"
        
        with open('/tmp/crm_report_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(message + '\n')
        
        logger.info(message)
        return message
        
    except Exception as e:
        error_message = f"Test task error: {str(e)}"
        logger.error(error_message)
        return error_message