from flask_restful import reqparse, Resource

from extensions import my_redis, config
from workers.ConsoleWriter import ConsoleWriter
from workers.EventHubWriter import EventHubWriter
from workers.RedisNotifier import RedisNotifier
from workers.UrlFileReader import UrlFileReader


class RedisController(Resource):

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("url")

        self.url_file_reader = UrlFileReader()
        self.redis_notifier = RedisNotifier(my_redis)
        self.console_writer = ConsoleWriter(self.redis_notifier)
        self.event_hub_writer = EventHubWriter(self.redis_notifier)

    def post(self):
        url = self.parser.parse_args().get('url')
        data = self.url_file_reader.read_file_from_url(url)
        filename = url.split('/')[-1].split('?')[0]

        if config['writer'] == 'event_hub':
            self.event_hub_writer.write_to_event_hub(filename, data)
        elif config['writer'] == 'console':
            self.console_writer.write_to_console(filename, data)

        return "Done", 200
