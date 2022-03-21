from email.message import Message
from alfalfa_jobs.job import Job, MessageHandler
class TestJob(Job):
    def __init__(self, *args):
        super().__init__()
        pass

    def run(self) -> None:
        print("running!")

    def name():
        return "Test Job"

    def description() -> str:
        return "Job to test functionality of the dispatcher"
    
    def something(self):
        print("something")
    
    def messages():
        return Job.messages() + [MessageHandler("something", TestJob.something, "does something")]