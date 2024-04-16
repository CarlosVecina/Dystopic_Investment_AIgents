from kafka import KafkaProducer
import json

from typing import Any

from src.data_ingestion.configs import LOCAL_KAFKA_SERVER


# https://medium.com/@cloud_geek/run-kafka-cluster-zookeeper-using-docker-kafdrop-docker-compose-52309c9f9e51
json_producer = KafkaProducer(bootstrap_servers=LOCAL_KAFKA_SERVER, value_serializer=lambda m: json.dumps(m).encode('ascii'))

def send_new(new: dict[str, Any], producer: KafkaProducer = json_producer, topic: str = "news-topic") -> bool:
    producer.send(topic, new)

