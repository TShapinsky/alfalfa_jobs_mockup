from alfalfa_jobs import Dispatcher
import json

dispatcher = Dispatcher()
job_id = dispatcher.process_message(json.dumps({"op":"InvokeAction", "action":"alfalfa_jobs.jobs.TestJob"}))
print(dispatcher.get_status(job_id).name)
dispatcher.send_message(job_id, 'something')
print(dispatcher.get_status(job_id).name)
dispatcher.send_message(job_id, 'stop')
print(dispatcher.get_status(job_id).name)
