from time import sleep
from alfalfa_jobs.job import Job, message
import os
class TestJob(Job):
    """Job to test functionality of the dispatcher"""

    # This is wrapped by the metaclass which pops off arguments which are not relevant to the job
    def __init__(self, interesting_info) -> None:
        print(interesting_info)

    def run(self) -> None:
        print("running!")

    @message
    def something(self):
        """Does Something"""
        print("something")

        path = self.path('something')
        os.mkdir(path)
        print(path)

        output_file_path = self.path('something', 'output.txt')
        output_file = open(output_file_path, 'w+')
        output_file.write('hello this is a test of the logging system')
        output_file.close()

        self.add_results_path('something/*')
        sleep(1)

    @message
    def stop(self) -> None:
        """Stop Job"""
        print("stopping")
        return super().stop()