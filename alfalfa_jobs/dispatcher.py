import json
from importlib import import_module
import uuid
import threading
class Dispatcher:
    def __init__(self):
        self.jobs = {}
        pass

    def process_message(self, message):
        message_body = json.loads(message)
        op = message_body.get('op')
        if op == 'InvokeAction':
            action = message_body.get('action')
            return self.start_job(action)
    
    def send_message(self, job_id, message):
        if job_id in self.jobs.keys():
            self.jobs[job_id].message_queue.put(message)

    def get_status(self, job_id):
        if job_id in self.jobs.keys():
            return self.jobs[job_id].status()

    def start_job(self, job_name):
        klazz = Dispatcher.find_class(job_name)
        job = klazz()
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = job
        job_thread = threading.Thread(target = job.start)
        job_thread.start()
        return job_id

    def find_class(path):
        components = path.split('.')
        module = import_module('.'.join(components[:-1]))
        klazz = getattr(module, components[-1])
        
        return klazz
