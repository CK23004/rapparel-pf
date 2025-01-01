from celery import shared_task
import requests, json
from datetime import datetime
import os
import requests
import json , time, ijson
import logging
from datetime import datetime, timedelta
from django.utils.timezone import now
from .models import Payment
from rapparel.settings import BASE_DIR
from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from threading import Event
from django.shortcuts import redirect
from .models import Product, Order



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@shared_task(bind=True)
def wizapp_products_data(self, mode):
    """
    Task to fetch inventory data from the API and print start and end times.
    """
    base_url = "https://wizapp.in/restWizappservice"
    group_code = "WZKI000002"
    username =  "online"
    password = "online"
    api_key =  "fynd"
    
    store_rapparelid = "1"
    logger.info("Data fetching started at %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    now = datetime.now()
    if 10 <= now.hour < 21:
        try:
            # Step 1: Get Refresh Token
            refresh_payload = {"userName": username, "passwd": password}
            refresh_response = requests.post(
                f"{base_url}/validateUser?GroupCode={group_code}",
                data=json.dumps(refresh_payload),
                headers={"Content-Type": "application/json"},
                timeout=10,  # Add a timeout
            )
            refresh_response.raise_for_status()
            refresh_token = refresh_response.json().get("refreshToken")
            logger.info("Refresh token obtained successfully.")

            # Step 2: Get Access Token
            access_headers = {"Authorization": f"Bearer {refresh_token}"}
            access_response = requests.get(
                f"{base_url}/getAccessToken?GroupCode={group_code}",
                headers=access_headers,
                timeout=10,
            )
            access_response.raise_for_status()
            access_token = access_response.json().get("accessToken")
            logger.info("Access token obtained successfully.")

            # Step 3: Fetch Inventory Data
            headers = {"Authorization": f"Bearer {access_token}"}
            inventory_response = requests.get(
                f"{base_url}/GetInvStockData?cUserId={username}&cPassword={password}&cApiKey={api_key}&mode={mode}",
                headers=headers,
                timeout=600,
                stream=True,
            )
            inventory_response.raise_for_status()
            processed_data = []
            buffer = ""

            for chunk in inventory_response.iter_content(chunk_size=1024*1024):  # 1 MB per chunk (adjustable)
                if chunk:
                    buffer += chunk.decode('utf-8')
                    try:
                        data = json.loads(buffer)
                        processed_data.extend(data)
                        buffer = ""  # Clear buffer after processing
                    except json.JSONDecodeError:
                        continue
            
            mode_directory = f"mode_{mode}"  # Create a folder for the corresponding mode

            # Set base directory and create the required subdirectory
            directory = os.path.join(BASE_DIR, "quickcommerce", "wizapp_data", mode_directory)
            os.makedirs(directory, exist_ok=True)
            # Save the processed data to a JSON file
            filename = os.path.join(directory, f"store_{store_rapparelid}.json")
            with open(filename, 'w', encoding='utf-8') as json_file:
                json.dump(processed_data, json_file, ensure_ascii=False, indent=4)

            logger.info("Data fetching ended at %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            logger.info("Data saved to %s", filename)
            return True  # Optionally return the data if needed

        except requests.exceptions.RequestException as req_err:
            logger.error("Request error occurred: %s", str(req_err))
            raise self.retry(countdown=60)  # Retry the task after 60 seconds on failure
        except Exception as e:
            logger.error("An unexpected error occurred: %s", str(e))
            raise self.retry(countdown=60)  # Retry on unexpected errors
    else:
        logger.info("Data Fetching Skipped")


# Helper function to check status with retries
def check_status_with_retries(payment, retry_count=0):
    from .views import phonepe_client, phonepe_refund

    # Define the intervals for retries
    retry_intervals = [
        25,  # First check at 20-25 seconds
        3,  # Next 30 seconds: every 3 seconds
        6,  # Next 60 seconds: every 6 seconds
        10,  # Next 60 seconds: every 10 seconds
        30,  # Next 60 seconds: every 30 seconds
        60,  # Every 1 minute
    ]
    
    # Determine the correct interval based on retry count
    if retry_count < 1:
        interval = retry_intervals[0]
    elif retry_count < 4:
        interval = retry_intervals[1]
    elif retry_count < 7:
        interval = retry_intervals[2]
    elif retry_count < 10:
        interval = retry_intervals[3]
    elif retry_count < 13:
        interval = retry_intervals[4]
    else:
        interval = retry_intervals[5]
    
    # Sleep for the interval before retrying
    if retry_count < len(retry_intervals):
        from time import sleep
        sleep(interval)  # Sleep for the calculated interval
    
    # Call the status check API after the delay
    status_response = phonepe_client.check_status(payment.transaction_id)
    return status_response

@shared_task
def check_payment_status(payment_id):
    from .views import phonepe_client, phonepe_refund

    try:
        payment = Payment.objects.get(id=payment_id)
        order = payment.order
        if payment.status == 'pending':
            # First, call the status check API
            try: 
                status_response = phonepe_client.check_status(payment.transaction_id)
                transaction_state = status_response.get("data", {}).get("PgTransactionStatusResponse", {}).get("state")
                amount_received = status_response.get("data", {}).get("PgTransactionStatusResponse", {}).get("amount")
                amount_initiated = payment.amount  # The amount used to initiate the transaction
                if amount_received != amount_initiated:
                    order.payment_status = 'failed'
                    order.save()
                    payment.status = 'failed'
                    payment.save()
                    return
            except Exception as e:
                print(e)
            # Validate the amount
            

            # Handle the different states based on the transaction status
            if transaction_state == 'COMPLETED':
                order.payment_status = 'failed'
                order.save()
                payment.status = 'completed'
                payment.save()
            elif transaction_state in ['PAYMENT_PENDING', 'INTERNAL_SERVER_ERROR']:
                # Reconciliation process for 'PAYMENT_PENDING' or 'INTERNAL_SERVER_ERROR'
                # Retry checking the status multiple times with intervals
                
                retry_count = 0
                timeout = now() + timedelta(minutes=15)  # Set the timeout for 15 minutes

                while now() < timeout:
                    retry_count += 1
                    # Check the status with retries
                    status_response = check_status_with_retries(payment, retry_count)
                    transaction_state = status_response.get("data", {}).get("PgTransactionStatusResponse", {}).get("state")

                    # If the transaction reaches a final state, stop the retries
                    if transaction_state == 'COMPLETED':
                        order.payment_status = 'failed'
                        order.save()
                        payment.status = 'failed'
                        payment.save()
                        phonepe_refund(payment.transaction_id)
                        break
                    elif transaction_state == 'FAILED':
                        order.payment_status = 'failed'
                        order.save()
                        payment.status = 'failed'
                        payment.save()
                        break
                    elif transaction_state == 'PAYMENT_PENDING':
                        # Continue waiting until we reach a terminal state
                        pass
                    elif transaction_state == 'INTERNAL_SERVER_ERROR':
                        # Continue waiting until we reach a terminal state
                        pass

                    # Check again after the next interval
                    retry_count += 1

                else:
                    # If the timeout is reached without a terminal status, mark as failed
                    order.payment_status = 'failed'
                    order.save()
                    payment.status = 'failed'
                    payment.save()

                    return redirect('landing_page')

    except Payment.DoesNotExist:
        pass




SFX_BASE_URL = "https://hlbackend.staging.shadowfax.in"
SFX_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "YSYLPTJ445C0M4Y3KVYDUW2FWSWF8Q"
}

# Shared dictionary to store callback data
CALLBACK_DATA = {}
CALLBACK_EVENT = Event()


@shared_task
def sfx_place_order(order_data):
    """
    Task to handle the order creation, tracking, and cancellation process.
    """
    try:
        # Step 1: Create the order
        create_order_url = f"{SFX_BASE_URL}/order/create/"
        response = requests.post(create_order_url, json=order_data, headers=SFX_HEADERS)
        response_data = response.json()

        if not response.ok or not response_data.get("is_order_created"):
            logging.ERROR(f"Order creation failed. {order_id}")

        order_id = order_data["order_details"]["order_id"]

        # Step 2: Get order details
        track_order_url = f"{SFX_BASE_URL}/order/track/{order_id}/"
        response = requests.get(track_order_url, headers=SFX_HEADERS)
        order_details = response.json()

        if not response.ok:
            logging.ERROR(f"Failed to fetch order details. {order_id}")

        # Pass the tracking URL to the UI
        tracking_url = order_details.get("tracking_url")
        print(f"Tracking URL: {tracking_url}")
        order_no = order_id[3:]
        order_obj = Order.objects.get(order_no=order_no) 
        order_obj.tracking_id = tracking_url
        # Step 3: Wait for callback and check conditions
        CALLBACK_EVENT.clear()
        deadline = now() + timedelta(minutes=20)

        while now() < deadline:
            if CALLBACK_EVENT.is_set() and order_id in CALLBACK_DATA:
                callback_data = CALLBACK_DATA.pop(order_id)
                if callback_data.get("status") == "ACCEPTED" and callback_data.get("rider_id") and callback_data.get("rider_name"):
                    return  # Callback conditions satisfied

            time.sleep(5)  # Check every 5 seconds

        # Step 4: Cancel the order
        cancel_order_url = f"{SFX_BASE_URL}/order/cancel/"
        cancel_response = requests.post(cancel_order_url, json={"order_id": order_id}, headers=SFX_HEADERS)

        if not cancel_response.ok:
            logging.ERROR(f"Order cancellation failed. {order_id}")

        # Send email to admin with order details
        admin_email = settings.ADMIN_EMAIL
        subject = "SFX Order Cancellation Notification"
        message = f"Order {order_id} has been cancelled due to no rider availability.\n\nDetails:\n{order_data}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])

    except Exception as e:
        # Handle exceptions (optional: send email to admin for errors)
        admin_email = settings.ADMIN_EMAIL
        subject = "SFX Order Processing Error"
        message = f"An error occurred while processing the order.\n\nError: {str(e)}\n\nOrder Data: {order_data}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])
        pass



@shared_task
def sync_inventory_task(mode, store_id):
    try:
        # Step 1: Try to open the store's JSON file (store_{store_id}.json) 
        #pass rapaprel store id
        file_path = f'{settings.BASE_DIR}/quickcommerce/wizapp_data/mode_{mode}/store_{store_id}.json'  # Assuming the file is in the BASE_DIR
        try:
            with open(file_path, 'r') as file:
                # Initialize the JSON parser to read the file incrementally
                objects = ijson.items(file, 'Section Name')  # 'item' is the root element for each product in your JSON
                
                products_updated = 0
                # Step 2: Iterate over the JSON objects (products/variants)
                for obj in objects:
                    sku = obj.get('SKU')
                    if not sku:
                        continue  # Skip if SKU is not present in the variant
                    
                    # Step 3: Find the product variant matching the SKU
                    product = product = Product.objects.filter(variant__contains=[{'sku': sku}])
                     # Get the product matching the SKU
                    if not product:
                        continue  # If no product is found for this SKU, skip the update
                    
                    # Step 4: Update the inventory in the variant
                    stock_qty = obj.get('Stock Qty')
                    if stock_qty is not None:
                        try:
                            stock_qty = int(stock_qty)  # Convert to int
                        except ValueError:
                            stock_qty = 0 
                    for variant in product.variants:
                        if variant.get('sku') == sku:
                            variant['inventory'] = stock_qty
                            product.save()  # Save the product to reflect inventory changes
                            products_updated += 1

        except FileNotFoundError:
            return {'error': f'File store_{store_id}.json not found'}

        return {'message': f'Inventory sync completed successfully. {products_updated} products updated.'}

    except Exception as e:
        return {'error': f'Error syncing inventory: {str(e)}'}



# # Hyperlocal serviceability check
# @shared_task(bind=True)
# def sfx_hyperlocal_placeorder(self, store_code, coid, drop_latitude, drop_longitude, order_value, customer_details, product_details, misc):
#     urls = {
#         "serviceability": "https://hlbackend2.staging.shadowfax.in/api/v2/store_serviceability/",
#         "create_order": "https://hlbackend2.staging.shadowfax.in/api/v2/stores/orders/",
#     }
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": "Token d273c9a881871b8be293b0b4af273521b8f2972e",
#     }

#     logger.info("Starting Hyperlocal serviceability check...")

#     body = {
#         "store_code": store_code,
#         "COID": coid,
#         "paid": "true",
#         "stage_of_check": "pre_order",
#         "drop_latitude": drop_latitude,
#         "drop_longitude": drop_longitude,
#         "order_value": order_value,
#     }

#     try:
#         response = requests.put(urls["serviceability"], headers=headers, json=body)
#         response_data = response.json()

#         available_rider_count = response_data.get("available_rider_count", 0)
#         free_riders = response_data.get("free_riders", 0)

#         if available_rider_count > 0 and free_riders > 0:
#             logger.info("Riders available. Proceeding to place order...")

#             create_order_body = {
#                 "pickup_contact_number": misc.get("pickup_contact_number"),
#                 "store_code": store_code,
#                 "order_details": {
#                     "scheduled_time": misc.get("scheduled_time"),
#                     "order_value": order_value,
#                     "paid": True,
#                     "client_order_id": coid,
#                     "store_manager_number": misc.get("store_manager_number"),
#                     "delivery_geofence_radius": misc.get("delivery_geofence_radius"),
#                     "delivery_instruction": misc.get("delivery_instruction"),
#                 },
#                 "customer_details": customer_details,
#                 "misc": misc,
#                 "product_details": product_details,
#             }

#             create_order_response = requests.post(
#                 urls["create_order"], headers=headers, json=create_order_body
#             )
#             return create_order_response.json()

#         logger.info("No available riders for Hyperlocal service.")
#     except Exception as e:
#         logger.error(f"Error during Hyperlocal serviceability check: {e}")

#     return {"status": "failed", "message": "Not serviceable in Hyperlocal."}
