import pika
import json
import time
from . import crud, database
from shared.app.settings import Settings

settings = Settings()

def on_message_received(ch, method, properties, body):
    print("Product Service: Received new message from RabbitMQ", flush=True)
    try:
        order_data = json.loads(body)
        db_session = next(database.get_db())
        
        print(f"Product Service: Processing inventory update for order ID: {order_data.get('id')}", flush=True)
        for item in order_data.get('items', []):
            crud.decrease_product_quantity(db_session, item['product_id'], item['quantity'])
        
        print(f"Product Service: Inventory successfully updated for order ID: {order_data.get('id')}", flush=True)
        db_session.close()

    except Exception as e:
        print(f"Product Service: FAILED to process message. Error: {e}", flush=True)
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    while True:
        try:
            print("Product Service: Attempting to connect to RabbitMQ...", flush=True)
            connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
            channel = connection.channel()
            
            channel.queue_declare(queue='order_created_queue', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='order_created_queue', on_message_callback=on_message_received)
            
            print('Product Service: Started consuming from RabbitMQ. Waiting for messages.', flush=True)
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Product Service: Connection to RabbitMQ failed: {e}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)
        except Exception as e:
            print(f"Product Service: An unexpected error occurred: {e}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)