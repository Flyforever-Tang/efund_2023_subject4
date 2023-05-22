import redis
import typing
import warnings


class RedisMQ(object):
    def __init__(self,
                 sleep_time: float = 0.001,
                 ignore_subscribe_messages: bool = True):
        self.strict_redis = redis.StrictRedis(host='127.0.0.1')
        self.pubsub = self.strict_redis.pubsub(ignore_subscribe_messages=ignore_subscribe_messages)
        self.callback_function_dict = {}
        self.pubsub.run_in_thread(sleep_time=sleep_time)

    def callback_handler(self,
                         message: dict[str, typing.Any]) -> None:
        try:
            self.callback_function_dict[message['channel']](message['data'])
        except BaseException as error:
            warnings.warn(f'An error occurred when using RedisMQ.callback_handler()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')

    def subscribe(self,
                  channel_name: str,
                  callback_function: typing.Optional[typing.Callable[[dict[str, typing.Any]], None]] = None) -> None:
        self.callback_function_dict[channel_name] = callback_function
        self.pubsub.subscribe(channel_name, **{channel_name: self.callback_handler})
