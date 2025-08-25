import os
from datetime import datetime
import requests
import json

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
        
        # GraphQL query for hello field
        query = {
            "query": "{ hello }"
        }
        
        # Make request to GraphQL endpoint
        response = requests.post(
            graphql_url,
            json=query,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'hello' in data['data']:
                heartbeat_message += " - GraphQL endpoint responsive"
            else:
                heartbeat_message += " - GraphQL endpoint available but hello field not found"
        else:
            heartbeat_message += f" - GraphQL endpoint returned status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        # If GraphQL query fails, still log the basic heartbeat
        heartbeat_message += f" - GraphQL endpoint unavailable: {str(e)}"
    except Exception as e:
        # Handle any other exceptions
        heartbeat_message += f" - Error checking GraphQL: {str(e)}"
    
    # Append heartbeat message to log file
    try:
        with open(log_file, 'a') as f:
            f.write(heartbeat_message + '\n')
    except Exception as e:
        # If logging fails, at least try to print to console
        print(f"Failed to write heartbeat log: {str(e)}")
        print(heartbeat_message)