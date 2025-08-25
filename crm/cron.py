import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm CRM application health.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    Optionally queries GraphQL hello field to verify endpoint responsiveness.
    """
    
    # Get current timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Log file path
    log_file = '/tmp/crm_heartbeat_log.txt'
    
    # Base heartbeat message
    heartbeat_message = f"{timestamp} CRM is alive"
    
    try:
        # Optional: Query GraphQL hello field to verify endpoint is responsive
        graphql_url = "http://localhost:8000/graphql"
        
        # Setup GraphQL client
        transport = RequestsHTTPTransport(url=graphql_url)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # GraphQL query for hello field
        query = gql("""
            query {
                hello
            }
        """)
        
        # Execute the query
        result = client.execute(query)
        
        if result and 'hello' in result:
            heartbeat_message += " - GraphQL endpoint responsive"
        else:
            heartbeat_message += " - GraphQL endpoint available but hello field not found"
            
    except Exception as e:
        # If GraphQL query fails, still log the basic heartbeat
        heartbeat_message += f" - GraphQL endpoint unavailable: {str(e)}"
    
    # Append heartbeat message to log file
    try:
        with open(log_file, 'a') as f:
            f.write(heartbeat_message + '\n')
    except Exception as e:
        # If logging fails, at least try to print to console
        print(f"Failed to write heartbeat log: {str(e)}")
        print(heartbeat_message)

def update_low_stock():
    """
    Executes the UpdateLowStockProducts GraphQL mutation every 12 hours.
    Updates products with stock < 10 by incrementing stock by 10.
    Logs updated product names and new stock levels.
    """
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    
    # Log file path
    log_file = '/tmp/low_stock_updates_log.txt'
    
    try:
        # GraphQL endpoint
        graphql_url = "http://localhost:8000/graphql"
        
        # Setup GraphQL client
        transport = RequestsHTTPTransport(url=graphql_url)
        client = Client(transport=transport, fetch_schema_from_transport=False)
        
        # GraphQL mutation for updating low stock products
        mutation = gql("""
            mutation UpdateLowStockProducts {
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
        """)
        
        # Execute the mutation
        result = client.execute(mutation)
        
        # Process the result
        mutation_result = result.get('updateLowStockProducts', {})
        success = mutation_result.get('success', False)
        message = mutation_result.get('message', 'No message')
        count = mutation_result.get('count', 0)
        updated_products = mutation_result.get('updatedProducts', [])
        
        # Log the results
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Stock update job executed\n")
            f.write(f"[{timestamp}] Success: {success}, Message: {message}\n")
            f.write(f"[{timestamp}] Updated {count} products:\n")
            
            for product in updated_products:
                product_name = product.get('name', 'Unknown')
                old_stock = product.get('oldStock', 0)
                new_stock = product.get('newStock', 0)
                product_id = product.get('id', 'Unknown')
                
                f.write(f"[{timestamp}] Product: {product_name} (ID: {product_id}) - Stock updated from {old_stock} to {new_stock}\n")
            
            f.write(f"[{timestamp}] Stock update job completed\n\n")
            
    except Exception as e:
        # Log any errors
        with open(log_file, 'a') as f:
            f.write(f"[{timestamp}] Error executing stock update: {str(e)}\n\n")