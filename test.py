from time import sleep
from alfalfa_jobs import Dispatcher
import json
import os

os.environ['THREADED_JOBS'] = '1'

dispatcher = Dispatcher()
dispatcher.print_job("alfalfa_jobs.jobs.TestJob")
jobs = dispatcher.get_jobs()
for job in jobs:
    print (f"{job.__module__}.{job.__qualname__}")
# Send message to create job
job_id = dispatcher.process_message(json.dumps({"op":"InvokeAction",
 "action":"alfalfa_jobs.jobs.TestJob",
 "parameters": {"interesting_info": "This is very interesting"}}))
sleep(1)
print(dispatcher.get_status(job_id).name)
# Send "something" message
dispatcher.send_message(job_id, 'something')
sleep(1)
print(dispatcher.get_status(job_id).name)
# Send "stop" message
dispatcher.send_message(job_id, 'stop')
sleep(1)
print(dispatcher.get_status(job_id).name)
