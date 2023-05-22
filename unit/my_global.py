import typing


class Global(object):
    dask_client: typing.Optional['DaskClient'] = None
    default_callback_mode: typing.Optional[str] = None
    flask_app: typing.Optional['FlaskApp'] = None
    redis_mq: typing.Optional['RedisMQ'] = None
    persistence: typing.Optional['Persistence'] = None
    task_manager: typing.Optional['TaskManager'] = None


from dask_client import DaskClient
from flask_app import FlaskApp
from message_queue import RedisMQ
from persistence import Persistence
from task import TaskManager
