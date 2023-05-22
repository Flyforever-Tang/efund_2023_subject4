def init():
    from dask_client import DaskClient
    from flask_app import FlaskApp
    import json
    from message_queue import RedisMQ
    from persistence import LocalPersistence, MySQLPersistence
    from task import TaskManager
    from unit.my_global import Global

    config_file_path = './config.json'
    with open(config_file_path, 'r') as config_file:
        config_json = json.load(config_file)

        Global.dask_client = DaskClient(config_json['DaskClient']['SchedulerAddress'])
        Global.default_callback_mode = config_json['Task']['DefaultCallbackMode']
        Global.flask_app = FlaskApp(config_json['FlaskApp']['Port'],
                                    config_json['FlaskApp']['StaticFolder'],
                                    config_json['FlaskApp']['JsonAsAscii'],
                                    config_json['FlaskApp']['SocketioNamespace'])

        persistence_type = config_json['Persistence']['Type']
        if persistence_type == 'LocalPersistence':
            Global.persistence = LocalPersistence(config_json['Persistence']['SaveFolder'])
        elif persistence_type == 'MySQLPersistence':
            Global.persistence = MySQLPersistence(config_json['Persistence']['Host'],
                                                  config_json['Persistence']['User'],
                                                  config_json['Persistence']['Password'],
                                                  config_json['Persistence']['Database'],
                                                  config_json['Persistence']['Table'],
                                                  config_json['Persistence']['PrimaryKey'])
        Global.redis_mq = RedisMQ(config_json['RedisMQ']['SleepTime'],
                                  config_json['RedisMQ']['IgnoreSubscribeMessages'])

        Global.task_manager = TaskManager(Global.flask_app.__getattribute__('finished_response'),
                                          Global.flask_app.__getattribute__('failed_response'))
