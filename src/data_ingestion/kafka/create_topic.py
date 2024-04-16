from kafka.admin import KafkaAdminClient, NewTopic

from src.data_ingestion.configs import LOCAL_KAFKA_SERVER


admin_client = KafkaAdminClient(
    bootstrap_servers=LOCAL_KAFKA_SERVER, 
)

topic_list = []
topic_list.append(NewTopic(name="example_topic", num_partitions=1, replication_factor=1))
admin_client.create_topics(new_topics=topic_list, validate_only=False)
