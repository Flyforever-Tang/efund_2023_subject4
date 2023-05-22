from dask.distributed import Client, Future
from task import Task
import typing


class DaskClient(object):
    def __init__(self,
                 scheduler_address: str):
        self.scheduler_address = None if scheduler_address == '' else scheduler_address
        self.client = Client(self.scheduler_address, asynchronous=False)

    def __del__(self):
        print('Close client!')
        self.client.close()

    def add_task(self,
                 task: Task,
                 task_done_callback: typing.Callable[[Future], None]) -> Future:
        task_future = self.client.submit(task.function, *task.args, **task.kwargs, key=task.key)
        task_future.add_done_callback(task_done_callback)
        return task_future
