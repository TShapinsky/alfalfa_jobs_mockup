import json
from importlib import import_module
import uuid

from alfalfa_jobs.job import Job

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
        """Send message to Job
        mocks up redis"""
        if job_id in self.jobs.keys():
            self.jobs[job_id]._message_queue.put(message)

    def get_status(self, job_id):
        """Get job status"""
        if job_id in self.jobs.keys():
            return self.jobs[job_id].status()

    def start_job(self, job_name):
        """Start job in thread by Python class path"""
        klazz = Dispatcher.find_class(job_name)
        job = klazz()
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = job
        job.start()
        return job_id

    def find_class(path):
        """Gets class from class path"""
        components = path.split('.')
        module = import_module('.'.join(components[:-1]))
        klazz = getattr(module, components[-1])
        return klazz

    def print_job(job_name):
        klazz = Dispatcher.find_class(job_name)
        # Create an instance of the job witout calling the init to get doc fields
        job_instance = Job.__new__(klazz)
        print(f"Name: \t{job_instance.name()}")
        print(f"Description: \t{job_instance.description()}")
        print("Message Handlers:")
        for message_handler in job_instance.messages():
            print(f"{message_handler.message_id}: \t {message_handler.doc_string}")