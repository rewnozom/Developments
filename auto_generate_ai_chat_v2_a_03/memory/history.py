import json

from custom_logging.logger import logger

class AgentEventTypeError(Exception):
    """Custom exception for invalid agent event types."""
    pass

class ShortTermHistory:
    def __init__(self):
        self.events = []

    def add_event(self, event_dict: dict):
        if not isinstance(event_dict, dict):
            raise AgentEventTypeError()
        self.events.append(event_dict)

    def get_events(self):
        return self.events

    def get_total_length(self):
        total_length = 0
        for t in self.events:
            try:
                total_length += len(json.dumps(t))
            except TypeError as e:
                logger.error('Error serializing event: %s', str(e), exc_info=False)
        return total_length
