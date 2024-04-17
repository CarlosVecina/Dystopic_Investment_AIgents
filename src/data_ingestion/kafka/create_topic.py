import os
import dotenv
from kafka.admin import KafkaAdminClient, NewTopic

dotenv.load_dotenv()

admin_client = KafkaAdminClient(
    bootstrap_servers=os.environ["LOCAL_BOOSTRAP_SERVER"], 
)

topic_list = []
topic_list.append(NewTopic(name="example_topic", num_partitions=1, replication_factor=1))
admin_client.create_topics(new_topics=topic_list, validate_only=False)
