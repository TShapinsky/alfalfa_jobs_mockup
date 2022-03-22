from dataclasses import dataclass
from enum import Enum
import threading
from types import FunctionType
from typing import List
from queue import SimpleQueue
import alfalfa_jobs

def message(func):
    setattr(func,'message_handler', True)
    return func

class Job():

    def __init__(self):
        self._message_handlers = {}
        self._status = JobStatus.CREATED
        self._message_queue = SimpleQueue()

    def setup(self, *args):
        """setup variables and files for job"""
        pass

    def start(self):
        if alfalfa_jobs.__threaded_jobs__:
            self.thread = threading.Thread(target=self._start)
            self.thread.start()
        else:
            self._start()

    def _start(self) -> None:
        """Job workflow"""
        try:
            self._status = JobStatus.STARTING
            self._setup_message_handlers()
            self._status = JobStatus.RUNNING
            self.run()
            self._status = JobStatus.WAITING
            self._message_loop()
            self._status = JobStatus.CLEANING_UP
            self.cleanup()
            self._status = JobStatus.STOPPED
        except Exception as e:
            print(e)
            self._status = JobStatus.ERROR

    def run(self) -> None:
        """Runs job
        called by start()"""
        pass

    @message
    def stop(self) -> None:
        """Stop job"""
        self._status = JobStatus.STOPPING
    
    def cleanup(self) -> None:
        """Clean up job
        called after stopping"""
        pass

    def status(self) -> "JobStatus":
        """Get job status
        gives general status of job workflow"""
        return self._status

    def _setup_message_handlers(self):
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, 'message_handler'):
                self._message_handlers[attr_name] = attr

    def _message_loop(self):
        while self._status.value < JobStatus.STOPPING.value:
            self._status = JobStatus.WAITING
            message = self._message_queue.get()
            if message in self._message_handlers.keys():
                self._status = JobStatus.RUNNING
                self._message_handlers[message]()

@dataclass(frozen=True)
class MessageHandler:
    """Dataclass for message handler"""
    message_id: str
    callback_func: FunctionType
    doc_string: str

class JobStatus(Enum):
    """Enumeration of job states"""
    CREATED = 0,
    STARTING = 2,
    RUNNING = 3,
    WAITING = 4,
    STOPPING = 8,
    CLEANING_UP = 9,
    STOPPED = 10,
    ERROR = 63