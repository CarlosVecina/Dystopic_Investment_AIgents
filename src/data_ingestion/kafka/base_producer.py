from pydantic import BaseModel
from kafka import KafkaProducer
import json 


class BaseProducer(BaseModel):
    _kafka_producer: KafkaProducer

    class Config:
        arbitrary_types_allowed=True

    def __init__(self, **kw):
        super().__init__(**kw)
        self._kafka_producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'), **kw)

    def produce(self, topic: str, key: str, msg: str) -> bool:
        self._kafka_producer.send(topic, msg)