import config
from unit.my_global import Global
from flask import request
import random
from task import Task
import time
import socket

if __name__ == '__main__':
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        return ip

    print(get_ip())

    config.init()
    test_flask_app = Global.flask_app

    def get_randoms(n: int):
        results = []
        for i in range(n):
            results.append(random.random())
            time.sleep(1)
        return results


    @test_flask_app.app.route('/submit_task_get', methods=['GET'])
    def get_randoms_api():
        para = int(request.values.get('para'))
        callback_mode = request.values.get('callback_mode', Global.default_callback_mode)
        new_task = Task(get_randoms, Task.CallbackMode[callback_mode], para)
        Global.task_manager.add_task(new_task)
        return {'para': para,
                'callback_mode': callback_mode,
                'task_key': new_task.key}


    temp_task = Task(get_randoms, Task.CallbackMode['HTTP'], 10)
    Global.task_manager.add_task(temp_task)
    temp_task = Task(get_randoms, Task.CallbackMode['HTTP'], 3)
    Global.task_manager.add_task(temp_task)
    temp_task = Task(get_randoms, Task.CallbackMode['HTTP'], 5)
    Global.task_manager.add_task(temp_task)
    test_flask_app.run()
