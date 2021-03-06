import datetime

class Task:
    num_tasks_generated = 0

    def __init__(self, task="", done=False, dt=None, recurrence=None, priority=3,
                 labels=None):
        """
        :param done: Whether taks is doned
        :param due_date: Date on which task should be doned
        :param due_time Time by which task should be doned
        :param recurrence: Boolean indicating whether task recurs
        :param priority: Float score based on urgency and importance of task
        :param labels: List of strings to help categorize tasks
        """
        Task.num_tasks_generated += 1
        self.task = task
        self.task_id = str(Task.num_tasks_generated)
        self.done = done
        self.due_date = "{}/{}/{}".format(dt.month, dt.day, dt.year) if dt else None
        self.due_time = str(dt.time()) if dt else None
        self.recurrence = recurrence
        self.priority = priority
        self.labels = labels

    def set_info(self, task_id, task_dict):
        """
        Sets all information given an id and a task dictionary
        :param task_dict:
        :return: returns whether operation was successful
        """
        if task_id == self.task_id:
            self.task = task_dict['task']
            self.done = task_dict['done']
            self.due_date = task_dict['due_date']
            self.due_time = task_dict['due_time']
            self.recurrence = task_dict['recurrence']
            self.priority = task_dict['priority']
            self.labels = task_dict['labels']
            return True
        else:
            return False

    def get_info(self):
        """
        :return: id, and dictionary of all properties
        """
        return self.task_id, {'task': self.task, 'done': self.done, 'due_date': self.due_date,
                              'due_time': self.due_time, 'recurrence': self.recurrence, 'priority': self.priority,
                              'labels': self.labels}

    def get_id(self):
        return self.task_id
