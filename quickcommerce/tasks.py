from celery import shared_task
import requests, json
from datetime import datetime

@shared_task
def fetch_api_data():
    """
    Task to fetch inventory data from the API and print start and end times.
    """
    base_url = "https://wizapp.in/restWizappservice"
    group_code = "WZKI000002"

    print(f"Data fetching started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Step 1: Get Refresh Token
        refresh_payload = {"userName": "online", "passwd": "online"}
        refresh_response = requests.post(
        f"{base_url}/validateUser?GroupCode={group_code}",
        data=json.dumps(refresh_payload),
        headers={"Content-Type": "application/json"},  # Add headers if required
         )
    
    # Print response details for debugging
        print("Status Code:", refresh_response.status_code)
        print("Response Content:", refresh_response.text)
        
        print(2)
        refresh_token = refresh_response.json().get("refreshToken")
        print(refresh_token)
        # Step 2: Get Access Token
        access_headers = {"Authorization": f"Bearer {refresh_token}"}
        access_response = requests.get(
            f"{base_url}/getAccessToken?GroupCode={group_code}", headers=access_headers
        )
        access_token = access_response.json().get("accessToken")
        print(access_token)
        # Step 3: Fetch Inventory Data
        headers = {"Authorization": f"Bearer {access_token}"}
        inventory_response = requests.get(
            f"{base_url}/GetInvStockData?cUserId=online&cPassword=online&cApiKey=fynd&mode=2",
            headers=headers,
            timeout=600, stream=True
        )
        processed_data = []
        # Process each chunk of data as it arrives
        for chunk in inventory_response.iter_content(chunk_size=3000000):  # 1 KB per chunk
            if chunk:
                # Assuming the response is JSON, decode and process it
                data = json.loads(chunk.decode('utf-8'))
                print(data)
                # Process the chunk (example: extend processed data)
                processed_data.extend(data)

        print(f"Data fetching ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(inventory_response.status_code)
        print(inventory_response.text)
        if inventory_response.status_code == 200:
            return inventory_response.json()

    except Exception as e:
        print( str(e))
        return []

    return []
