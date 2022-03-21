from dataclasses import dataclass
from enum import Enum
from types import FunctionType
from typing import List
from queue import SimpleQueue

class Job:
    def __init__(self):
        self.message_handlers = {}
        self._status = JobStatus.CREATED
        self.message_queue = SimpleQueue()

    def setup(self, *args):
        pass

    def start(self) -> None:
        self._status = JobStatus.STARTING
        self._setup_message_handlers()
        self._status = JobStatus.RUNNING
        self.run()
        self._status = JobStatus.WAITING
        self._message_loop()
        self._status = JobStatus.CLEANING_UP
        self.cleanup()
        self._status = JobStatus.STOPPED

    def run(self) -> None:
        pass

    def stop(self) -> None:
        self._status = JobStatus.STOPPING

    def cleanup(self) -> None:
        pass

    def name() -> str:
        raise NotImplementedError

    def description() -> str:
        raise NotImplementedError

    def messages() -> List["MessageHandler"]:
        return [MessageHandler('stop', lambda self: self.stop(), '')]

    def status(self) -> "JobStatus":
        return self._status

    def _setup_message_handlers(self):
        for handler in self.__class__.messages():
            message_id = handler.message_id
            callback_func = handler.callback_func.__get__(self)
            self.message_handlers[message_id] = callback_func

    def _message_loop(self):
        while self._status.value < JobStatus.STOPPING.value:
            message = self.message_queue.get()
            if message in self.message_handlers.keys():
                self.message_handlers[message]()

@dataclass(frozen=True)
class MessageHandler:
    message_id: str
    callback_func: FunctionType
    doc_string: str

class JobStatus(Enum):
    CREATED = 0,
    STARTING = 2,
    RUNNING = 3,
    WAITING = 4,
    STOPPING = 8,
    CLEANING_UP = 9,
    STOPPED = 10,