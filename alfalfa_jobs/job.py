from enum import Enum
from glob import glob
import threading
from queue import SimpleQueue
import os
import tarfile
import shutil

def message(func):
    """Decorator for methods which are triggered by messages.
    Overriding a function that has a decorator in the base class (like 'stop') will need to be decorated again."""
    setattr(func,'message_handler', True)
    return func

class JobMetaclass(type):

    # Wrap Subclass __init__
    def __new__(cls, name, bases, cls_dicts):
        if '__init__' in cls_dicts.keys():
            __old_init__ = cls_dicts['__init__']
        else:
            __old_init__ = None
        def __new_init__(self, working_dir, *args, **kwargs):
            self.working_dir = working_dir
            self._message_handlers = {}
            self._status = JobStatus.CREATED
            self._message_queue = SimpleQueue()
            self._result_paths = []

            for attr_name in dir(self):
                attr = getattr(self, attr_name)
                if hasattr(attr, 'message_handler'):
                    self._message_handlers[attr_name] = attr
            if __old_init__:
                __old_init__(self, *args, **kwargs)
        cls_dicts['__init__'] = __new_init__
        klazz = super().__new__(cls, name, bases, cls_dicts)
        
        if len(bases) == 0:
            klazz.jobs = []
        if len(bases) > 0:
            Job.jobs.append(klazz)
        return klazz

class Job(metaclass=JobMetaclass):

    def start(self, *args, **kwargs):
        if 'THREADED_JOBS' in os.environ.keys() and os.environ['THREADED_JOBS'] == '1':
            self.thread = threading.Thread(target=self._start, args=args, kwargs=kwargs)
            self.thread.start()
        else:
            self._start(*args, **kwargs)

    def _start(self) -> None:
        """Job workflow"""
        try:
            self._set_status(JobStatus.STARTING)
            self._set_status(JobStatus.RUNNING)
            self.run()
            self._set_status(JobStatus.WAITING)
            self._message_loop()
            self._set_status(JobStatus.CLEANING_UP)
            self.cleanup()
            self._set_status(JobStatus.STOPPED)
        except Exception as e:
            print(e)
            self._set_status(JobStatus.ERROR)
            raise

    def run(self) -> None:
        """Runs job
        called by start()"""
        pass

    @message
    def stop(self) -> None:
        """Stop job"""
        self._set_status(JobStatus.STOPPING)
    
    def cleanup(self) -> None:
        """Clean up job
        called after stopping"""
        self.tar_working_dir()
        self.delete_working_dir()

    def add_results_path(self, path):
        if len(os.path.commonpath([self.working_dir, path])) == 0:
            path = os.path.join(self.working_dir, path)
        self._result_paths.append(path)

    def path(self, *args):
        return os.path.join(self.working_dir, *args)

    def tar_working_dir(self) -> str:
        """tars job working dir
        if results_paths has stuff just add those, if not tar whole directory"""
        dir_name = os.path.split(self.working_dir)[-1]
        tar_path = os.path.join(self.working_dir, '..',f'{dir_name}.tar')
        tar = tarfile.TarFile(tar_path, 'w')
        if len(self._result_paths) > 0:
            for path in self._result_paths:
                files = glob(path)
                for file in files:
                    tar.add(file, arcname=os.path.relpath(file, start=self.working_dir))
        else:
            tar.add(self.working_dir, arcname='.')
        tar.close()
        return tar_path

    def delete_working_dir(self):
        shutil.rmtree(self.working_dir)

    def status(self) -> "JobStatus":
        """Get job status
        gives general status of job workflow"""
        return self._status

    def _set_status(self, status: "JobStatus"):
        # A callback could be added here to tell the client what the status is
        self._status = status

    def _message_loop(self):
        while self._status.value < JobStatus.STOPPING.value:
            self._status = JobStatus.WAITING
            message = self._message_queue.get()
            if message in self._message_handlers.keys():
                self._status = JobStatus.RUNNING
                self._message_handlers[message]()

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