#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def main():
    # GraphQL endpoint
    graphql_url = "http://localhost:8000/graphql"
    
    # Log file path
    log_file = "/tmp/order_reminders_log.txt"
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    try:
        # Setup GraphQL client
        transport = RequestsHTTPTransport(url=graphql_url)
        client = Client(transport=transport, fetch_schema_from_transport=True)
        
        # GraphQL query to find orders within last 7 days
        query = gql("""
            query GetRecentOrders($dateFrom: String!) {
                orders(orderDate_Gte: $dateFrom) {
                    id
                    orderDate
                    customer {
                        email
                    }
                }
            }
        """)
        
        # Execute the query
        variables = {"dateFrom": seven_days_ago}
        result = client.execute(query, variable_values=variables)
        
        # Process the orders
        orders = result.get('orders', [])
        
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Processing {len(orders)} pending orders from last 7 days\n")
            
            for order in orders:
                order_id = order.get('id')
                customer_email = order.get('customer', {}).get('email', 'No email')
                order_date = order.get('orderDate')
                
                # Log order ID and customer email
                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}, Order Date: {order_date}\n"
                f.write(log_entry)
        
        # Print success message to console
        print("Order reminders processed!")
        
    except Exception as e:
        # Log any errors
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Error processing order reminders: {str(e)}\n")
        
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()