import abc
import json
import os
import pymysql
import warnings
import typing


class Persistence(object):
    def __init__(self):
        pass

    @abc.abstractmethod
    def insert(self,
               key: str,
               values_dict: dict) -> bool:
        pass

    @abc.abstractmethod
    def update(self,
               key: str,
               new_values_dict: dict) -> bool:
        pass

    @abc.abstractmethod
    def query(self,
              key: str,
              target_column: str) -> dict[str, typing.Any]:
        pass

    @abc.abstractmethod
    def exist(self,
              target_key: str) -> bool:
        pass


class LocalPersistence(Persistence):
    def __init__(self,
                 save_folder: str):
        super(LocalPersistence, self).__init__()

        if not os.path.exists(save_folder):
            try:
                os.makedirs(save_folder)
            except BaseException as error:
                save_folder = './tasks'
                warnings.warn(f'An error occurred when making dir in the path of {save_folder}! \n'
                              f'Error type: {type(error)}. \n'
                              f'Error info: {error} \n'
                              f'Try to make dir in the current path of "./tasks". \n')
                os.makedirs(save_folder)
        self.save_folder = save_folder

    def insert(self,
               target_key: str,
               values_dict: dict[str, typing.Any]) -> bool:
        print('insert', target_key, values_dict)

        json_file_path = os.path.join(self.save_folder, target_key + '.json')
        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(values_dict, json_file, indent=4, separators=(',', ': '))
            return True
        except BaseException as error:
            warnings.warn(f'An error occurred when using LocalPersistence.insert()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            return False

    def update(self,
               target_key: str,
               new_values_dict: dict[str, typing.Any]) -> bool:
        print('update', target_key, new_values_dict)

        json_file_path = os.path.join(self.save_folder, target_key + '.json')
        try:
            with open(json_file_path, 'r') as json_file:
                ori_values_dict = json.load(json_file)
                if not isinstance(ori_values_dict, dict):
                    ori_values_dict = {}
        except BaseException as error:
            warnings.warn(f'An error occurred when using LocalPersistence.update()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            ori_values_dict = {}

        try:
            for key, value in new_values_dict.items():
                ori_values_dict[key] = value
            with open(json_file_path, 'w') as json_file:
                json.dump(ori_values_dict, json_file, indent=4, separators=(',', ': '))
            return True
        except BaseException as error:
            warnings.warn(f'An error occurred when using LocalPersistence.update()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            return False

    def query(self,
              target_key: str,
              target_columns: typing.Optional[list[str]] = None) -> dict[str, typing.Any]:
        print('query', target_key, target_columns)

        json_file_path = os.path.join(self.save_folder, target_key + '.json')
        try:
            with open(json_file_path, 'r') as json_file:
                values_dict = json.load(json_file)
                if not isinstance(values_dict, dict):
                    return {}
        except BaseException as error:
            warnings.warn(f'An error occurred when using LocalPersistence.query()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            values_dict = {}

        if target_columns is None:
            return values_dict
        else:
            return {key: values_dict[key] for key in target_columns}

    def exist(self,
              target_key: str) -> bool:
        print('exist', target_key)

        json_file_path = os.path.join(self.save_folder, target_key + '.json')
        return os.path.exists(json_file_path) and os.path.isfile(json_file_path)


class MySQLPersistence(Persistence):
    def __init__(self,
                 host: str,
                 user: str,
                 password: str,
                 database: str,
                 table: str,
                 primary_key: str = 'Task_key'):
        super(MySQLPersistence, self).__init__()

        self.database = pymysql.connect(host=host,
                                        user=user,
                                        password=password,
                                        database=database)
        self.cursor = self.database.cursor()
        self.table = table
        self.primary_key = primary_key

    def __del__(self):
        print('Close database!')
        self.database.close()

    @staticmethod
    def list2string(array: typing.Iterable,
                    left_bracket: str = '(',
                    right_bracket: str = ')'):
        result = left_bracket
        for item in array:
            result += f'{item}, '
        result = result[:-2] + right_bracket
        return result

    def insert(self,
               target_key: str,
               values_dict: dict[str, typing.Any]) -> bool:
        print('insert', target_key, values_dict)

        try:
            key_string = '('
            value_string = '('
            for key, value in values_dict.items():
                key_string += f'{key}, '
                if value is None:
                    value_string += f'NULL, '
                else:
                    value_string += f'"{value}", '
            key_string = key_string[:-2] + ')'
            value_string = value_string[:-2] + ')'

            sql_cmd = f'INSERT INTO {self.table} {key_string} VALUES {value_string};'
            print('sql: ', sql_cmd)
            self.cursor.execute(sql_cmd)
            self.database.commit()
            return True
        except BaseException as error:
            warnings.warn(f'An error occurred when using MySQLPersistence.insert()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            self.database.rollback()
            return False

    def update(self,
               target_key: str,
               new_values_dict: dict[str, typing.Any]) -> bool:
        print('update', target_key, new_values_dict)

        try:
            sql_cmd = f'UPDATE {self.table} SET '
            for key, value in new_values_dict.items():
                if value is None:
                    sql_cmd += f'{key}=NULL, '
                else:
                    sql_cmd += f'{key}="{value}", '
            sql_cmd = sql_cmd[:-2] + f' WHERE {self.primary_key}="{target_key}";'
            print('sql: ', sql_cmd)
            self.cursor.execute(sql_cmd)
            self.database.commit()
            return True
        except BaseException as error:
            warnings.warn(f'An error occurred when using MySQLPersistence.update()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            self.database.rollback()
            return False

    def query(self,
              target_key: str,
              target_columns: typing.Optional[list[str]] = None) -> dict[str, typing.Any]:
        print('query', target_key, target_columns)

        try:
            column_string = '('
            for column in target_columns:
                column_string += f'{column}, '
            column_string = column_string[:-2] + ')'

            sql_cmd = f'SELECT {column_string if target_columns is not None else "*"} ' \
                      f'FROM {self.table} WHERE {self.primary_key}="{target_key}";'
            print('sql: ', sql_cmd)
            self.cursor.execute(sql_cmd)
            sql_results = self.cursor.fetchall()
            if len(sql_results) == 0:
                return {}
            else:
                return {column: sql_result for column, sql_result in zip(target_columns, sql_results[0])}
        except BaseException as error:
            warnings.warn(f'An error occurred when using MySQLPersistence.query()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            return {}

    def exist(self,
              target_key: str) -> bool:
        print('exist', target_key)

        try:
            sql_cmd = f'SELECT EXISTS (SELECT * FROM {self.table} WHERE {self.primary_key}="{target_key}");'
            print('sql: ', sql_cmd)
            self.cursor.execute(sql_cmd)
            sql_results = self.cursor.fetchall()
            if len(sql_results) == 0:
                return False
            else:
                return bool(sql_results[0][0])
        except BaseException as error:
            warnings.warn(f'An error occurred when using MySQLPersistence.exist()! \n'
                          f'Error type: {type(error)}. \n'
                          f'Error info: {error}')
            return False
