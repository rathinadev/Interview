import pika
import json
import time
from . import crud, database
from shared.app.settings import Settings

settings = Settings()

def on_message_received(ch, method, properties, body):
    print("Product Service: Received new message from RabbitMQ")
    order_data = json.loads(body)
    db = next(database.get_db())
    
    try:
        for item in order_data['items']:
            crud.decrease_product_quantity(db, item['product_id'], item['quantity'])
        print(f"Product Service: Inventory successfully updated for order ID: {order_data['id']}")
    except Exception as e:
        print(f"Product Service: FAILED to process inventory update for order ID {order_data['id']}: {e}")
        # In a real system, publish a 'InventoryUpdateFailed' event back to RabbitMQ
    finally:
        db.close()

def start_consuming():
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
            channel = connection.channel()
            channel.queue_declare(queue='order_created_queue', durable=True)
            channel.basic_consume(queue='order_created_queue', auto_ack=True, on_message_callback=on_message_received)
            print('Product Service: Started consuming from RabbitMQ...')
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("Connection to RabbitMQ failed. Retrying in 5 seconds...")
            time.sleep(5)