import asyncio
from dask.distributed import Future
from enum import Enum
import hashlib
import json
import random
import time
import typing
from unit.my_global import Global
import warnings


class Task(object):
    class CallbackMode(Enum):
        HTTP = 1,
        MQ = 2

    def __init__(self,
                 function: typing.Callable,
                 callback_mode: CallbackMode,
                 *args, **kwargs):
        self.function = function
        self.callback_mode = callback_mode
        self.args = args
        self.kwargs = kwargs

        self.key = self.generate_key()
        self.future: typing.Optional[Future] = None
        self.task_info = {}

    def __call__(self):
        self.function(*self.args, **self.kwargs)

    def generate_key(self):
        cur_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())
        hashable_string = f'{cur_time}_{random.random()}_{self.function.__name__}'
        for value in self.args:
            try:
                hashable_string += f'_{value}'
            except BaseException as error:
                warnings.warn(f'An error occurred when using Task.add_task()! \n'
                              f'Error type: {type(error)}. \n'
                              f'Error info: {error}')
        for key, value in self.kwargs.items():
            try:
                hashable_string += f'_{key}:{value}'
            except BaseException as error:
                warnings.warn(f'An error occurred when using Task.add_task()! \n'
                              f'Error type: {type(error)}. \n'
                              f'Error info: {error}')
        key = hashlib.md5(hashable_string.encode('utf-8')).hexdigest()
        key = f'{cur_time}_{key}'
        return key


class TaskManager(object):
    def __init__(self,
                 finished_task_callback_function: typing.Callable,
                 failed_task_callback_function: typing.Callable):
        self.finished_task_callback_function = finished_task_callback_function
        self.failed_task_callback_function = failed_task_callback_function

        self.task_dict: typing.Dict[str, Task] = {}

        Global.redis_mq.subscribe('finished_task_channel', finished_task_callback_function)
        Global.redis_mq.subscribe('failed_task_channel', failed_task_callback_function)

    def dask_done_callback(self,
                           future: Future) -> None:
        task = self.task_dict[future.key]
        result = task.future.result()
        new_task_info = {
            'Status': task.future.status,
            'Complete_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'Result': result,
        }
        task.task_info.update(new_task_info)
        Global.persistence.update(task.key, new_task_info)
        message_string = json.dumps(result)

        if task.callback_mode == Task.CallbackMode.HTTP:
            if task.future.status == 'finished':
                self.finished_task_callback_function(message_string)
            else:
                self.failed_task_callback_function(message_string)
        elif task.callback_mode == Task.CallbackMode.MQ:
            if task.future.status == 'finished':
                Global.redis_mq.strict_redis.publish('finished_task_channel', message_string)
            else:
                Global.redis_mq.strict_redis.publish('failed_task_channel', message_string)
        self.task_dict.pop(task.key)

    def add_task(self,
                 task: Task) -> None:
        postfix = 0
        while True:
            new_key = f'{task.key}_{postfix}'
            if new_key in self.task_dict.keys() or Global.persistence.exist(new_key):
                postfix += 1
            else:
                task.key = new_key
                break

        task.future = Global.dask_client.add_task(task, self.dask_done_callback)
        task.task_info = {
            'Task_key': task.key,
            'Function_name': task.function.__name__,
            'Parameters': {
                'args': task.args,
                'kwargs': task.kwargs
            },
            'Status': 'pending',
            'Submit_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'Complete_time': None,
            'Result': None,
        }

        Global.persistence.insert(task.key, task.task_info)
        self.task_dict[task.key] = task

    def get_task_info(self,
                      task_key: str,
                      target_info_names: list[str]):
        if task_key in self.task_dict.keys():
            return {target_info_name: self.task_dict[task_key].task_info[target_info_name]
                    for target_info_name in target_info_names}
        else:
            query_result = Global.persistence.query(task_key, target_info_names)
            return {target_info_name: query_result[target_info_name]
                    for target_info_name in target_info_names and query_result.keys()}
