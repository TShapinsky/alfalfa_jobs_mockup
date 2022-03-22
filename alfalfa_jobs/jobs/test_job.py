from time import sleep
from alfalfa_jobs.job import Job, MessageHandler
class TestJob(Job):
    def run(self) -> None:
        print("running!")

    def name(self) -> str:
        return "Test Job"

    def description(self) -> str:
        return "Job to test functionality of the dispatcher"
    
    def something(self):
        print("something")
        sleep(1)

    def stop(self) -> None:
        print("stopping")
        return super().stop()
    
    def messages(self):
        # Message handlers are added to super().messages(), this inherits "stop" functionality
        return super().messages() + [MessageHandler("something", self.something, "does something")]