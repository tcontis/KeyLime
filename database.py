from task import Task


class Database:
    def __init__(self):
        self.database = {}

    def add_task(self, task):
        """
        :param task:
        :return: whether operation was sucessful
        """
        if isinstance(task, Task):
            task_id, task_dict = task.get_info()
            self.database[task_id] = task_dict
            return True
        return False

    def remove_task(self, task):
        self.remove_task_id(task.get_id())

    def remove_task_id(self, task_id):
        if isinstance(task_id, str) and 0 < int(task_id) <= max([int(key) for key in self.database.keys()]):
            del self.database[task_id]
            return True
        return False

    def tick_task_id(self, task_id, done):
        if isinstance(task_id, str) and 0 < int(task_id) <= max([int(key) for key in self.database.keys()]):
            print("!")
            self.database[task_id]["done"] = done
            return True
        return False

    def set_database(self, database):
        self.database = database

    def get_database(self):
        return self.database

    def get_length(self):
        return len(self.database)

    def get_column(self, property):
        return [task[property] for task in self.database.values()]

if __name__ == '__main__':
    d = Database()
    t = Task()