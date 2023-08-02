import concurrent.futures
import time


class WorkerPool:
    def __init__(self, num_of_workers: int) -> None:
        self.num_of_workers = num_of_workers

    def run(self) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_of_workers) as executor:
            results = executor.map(process_job, jobs)
