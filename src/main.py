import auth
from flask import Flask, request
import json
from google.cloud import pubsub_v1

from data_service import DataService

app = Flask(__name__)

project_id = "yonidev"
topic_name = "llm-topic"


@app.route('/', methods=['POST'])
def pubsub_handler():
    req_data = request.get_data().decode('utf-8')
    pubsub_message = json.loads(req_data)
    new_list = auth.get_list()
    DataService.update_data(pubsub_message['chat_id'] + "_list", new_list)
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    message_bytes = json.dumps(
        {"chat_id": pubsub_message['chat_id'], "source": "list_generator"}
    ).encode("utf-8")
    try:
        publish_future = publisher.publish(topic_path, data=message_bytes)
        publish_future.result()
    except Exception as e:
        print(f"Error publishing message: {e}")

    return 'OK', 200
