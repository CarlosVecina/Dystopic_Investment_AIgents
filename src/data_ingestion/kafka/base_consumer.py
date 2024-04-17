from pydantic import BaseModel
from kafka import KafkaConsumer
import json 


class BaseConsumer(BaseModel):
    _kafka_consumer: KafkaConsumer

    class Config:
        arbitrary_types_allowed=True

    def __init__(self, **kw):
        super().__init__(**kw)
        self._kafka_consumer = KafkaConsumer(**kw)

    def consume(self) -> bool:
        event_list = list()
        for e in self._kafka_consumer:
            event_list.append(e)
        return event_list
        
    def consume_next(self) -> bool:
        return next(self._kafka_consumer)