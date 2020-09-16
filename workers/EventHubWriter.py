import logging

from azure.eventhub import EventData

from extensions import event_hub_client


class EventHubWriter:

    def __init__(self, redis_notifier, redis_write_step=100):
        super(EventHubWriter, self).__init__()
        self.redis_notifier = redis_notifier
        self.redis_write_step = redis_write_step

    def write_to_event_hub(self, filename, data):
        write_allowed = self.redis_notifier.notify_start_record(filename)

        if write_allowed:

            with event_hub_client:
                for idx, line in enumerate(data, start=1):

                    # Create a batch.
                    event_data_batch = event_hub_client.create_batch()

                    event_data_batch.add(EventData(line))

                    event_hub_client.send_batch(event_data_batch)

                    if idx % self.redis_write_step == 0:  # write to redis every n lines
                        self.redis_notifier.notify_read_lines(filename, f"{idx-100}..{idx}")

            completed = self.redis_notifier.notify_completed(filename)

        else:
            logging.info(f"=====Attempted duplicate write for file: {filename} =====")
