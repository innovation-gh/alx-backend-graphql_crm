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