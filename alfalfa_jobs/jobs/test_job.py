from time import sleep
from alfalfa_jobs.job import Job, message
class TestJob(Job):
    """Job to test functionality of the dispatcher"""

    # Because the base class uses the __new__ function to setup variables not calling init is inconsequential
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        print("running!")

    @message
    def something(self):
        """Does Something"""
        print("something")
        sleep(1)

    @message
    def stop(self) -> None:
        """Stop Job"""
        print("stopping")
        return super().stop()