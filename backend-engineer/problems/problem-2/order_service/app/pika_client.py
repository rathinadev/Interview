import pika
import json
from shared.app.settings import Settings

settings = Settings()

def publish_order_created(order_id, items):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='order_created_queue', durable=True)
        
        message_body = {
            "id": order_id,
            "items": [item.model_dump() for item in items]
        }
        
        channel.basic_publish(
            exchange='',
            routing_key='order_created_queue',
            body=json.dumps(message_body),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print(f"Order Service: Sent 'order_created' event for order ID: {order_id}")
        connection.close()
    except Exception as e:
        print(f"Order Service: FAILED to send message to RabbitMQ: {e}")