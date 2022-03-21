from email.message import Message
from alfalfa_jobs.job import Job, MessageHandler
class TestJob(Job):
    def run(self) -> None:
        print("running!")

    def name() -> str:
        return "Test Job"

    def description() -> str:
        return "Job to test functionality of the dispatcher"
    
    def something(self):
        print("something")

    def stop(self) -> None:
        print("stopping")
        return super().stop()
    
    def messages():
        # Message handlers are added to Job.messages(), this inherits "stop" functionality
        return Job.messages() + [MessageHandler("something", TestJob.something, "does something")]