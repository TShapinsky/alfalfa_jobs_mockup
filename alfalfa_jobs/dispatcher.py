import json
from importlib import import_module
import uuid
import os
import alfalfa_jobs.job

class Dispatcher:
    def __init__(self):
        self.jobs = {}
        self.workdir = os.environ['ALFALFA_JOB_WD'] if 'ALFALFA_JOB_WD' in os.environ else './jobs'
        if not os.path.isdir(self.workdir):
            os.mkdir(self.workdir)

    def process_message(self, message):
        message_body = json.loads(message)
        op = message_body.get('op')
        if op == 'InvokeAction':
            action = message_body.get('action')
            parameters = message_body.get('parameters')
            return self.start_job(action, parameters)
    
    def send_message(self, job_id, message):
        """Send message to Job
        mocks up redis"""
        if job_id in self.jobs.keys():
            self.jobs[job_id]._message_queue.put(message)

    def get_status(self, job_id):
        """Get job status"""
        if job_id in self.jobs.keys():
            return self.jobs[job_id].status()

    def start_job(self, job_name, parameters):
        """Start job in thread by Python class path"""
        klazz = self.find_class(job_name)
        job_id = str(uuid.uuid4())
        job_dir = os.path.join(self.workdir, job_id)
        os.mkdir(job_dir)
        parameters['working_dir'] = job_dir
        job = klazz(**parameters)
        self.jobs[job_id] = job
        job.start()
        return job_id

    @staticmethod
    def find_class(path):
        """Gets class from class path"""
        components = path.split('.')
        module = import_module('.'.join(components[:-1]))
        klazz = getattr(module, components[-1])
        return klazz

    @staticmethod
    def print_job(job_name):
        klazz = Dispatcher.find_class(job_name)
        print(f"Name: \t{klazz.__name__}")
        print(f"Description: \t{klazz.__doc__}")
        print("Message Handlers:")
        for attr_name in dir(klazz):
            attr = getattr(klazz, attr_name)
            if hasattr(attr, 'message_handler'):
                print(f"{attr.__name__}: \t {attr.__doc__}")

    @staticmethod
    def get_jobs():
        for klazz in alfalfa_jobs.job.Job.jobs:
            print(f"Name: \t {klazz.__name__}")