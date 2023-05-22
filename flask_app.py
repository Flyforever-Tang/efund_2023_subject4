from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from unit.my_global import Global


class FlaskApp(object):
    def __init__(self,
                 port: int,
                 static_folder: str = '',
                 json_as_ascii: bool = False,
                 socketio_namespace: str = '/test'):
        self.port = port
        self.app = Flask(__name__, static_folder=static_folder)
        self.app.config['JSON_AS_ASCII'] = json_as_ascii

        CORS(self.app)

        self.socketio = SocketIO(self.app, async_mode='eventlet')
        self.socketio_namespace = socketio_namespace

        @self.app.route('/')
        def index():
            return 'Index API'

        @self.app.route('/get_status', methods=['GET', 'POST'])
        def get_status_api():
            task_key = request.values.get('task_key')
            return jsonify(Global.task_manager.get_task_info(task_key, ['Status']))

        @self.app.route('/get_result', methods=['GET', 'POST'])
        def get_result_api():
            task_key = request.values.get('task_key')
            return jsonify(Global.task_manager.get_task_info(task_key, ['Result']))

        @self.app.errorhandler(404)
        def url_error(error):
            return f'Wrong URL! <pre>{error}</pre>', 404

        @self.app.errorhandler(500)
        def server_error(error):
            return f'An internal error occurred: <pre>{error}</pre>. \n' \
                   f'See logs for full stacktrace.', 500

        @self.socketio.on('connect', namespace=self.socketio_namespace)
        def connected_msg():
            print('client connected.')

    def run(self):
        self.socketio.run(self.app, '0.0.0.0', self.port)

    def finished_response(self,
                          result: str):
        print('finished')
        print(result)
        self.socketio.emit('server_response', {'data': result}, namespace=self.socketio_namespace)

    def failed_response(self,
                        result: str):
        print('failed')
        print(result)
        self.socketio.emit('server_response', {'data': result}, namespace=self.socketio_namespace)
