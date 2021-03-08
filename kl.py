from database import Database
from task import Task
from argparse import ArgumentParser
import json
import os
import glob
import sys
import datetime
from dateutil.relativedelta import relativedelta
import time

class Main:
    def __init__(self, args):
        self.args = args
        self.database = Database()
        self.load_database()
        if args.cmd == "add":
            date = None
            if args.d:
                date = args.d[0]
            elif args.dd:
                date = args.dd[0]
            self.database.add_task(Task(task=args.task_name,
                                        dt=self.parse_due_date(datetime.datetime.today().strftime("%m/%d/%Y")
                                                               if args.td else date, args.d[1] if args.d else "23:59:00"),
                                        recurrence=(args.r if args.r else None),
                                        labels=args.l if args.l else None
                                        ))
            self.save_database()
        elif args.cmd == "del":
            for task_id in args.task_id:
                self.database.remove_task_id(str(task_id))
            self.save_database()
        elif args.cmd == "list":
            td = datetime.datetime.today()
            self.list_tasks(due_dates=([td.date(), self.parse_duration(duration=args.n[0], start_datetime=td, return_string=False).date()] if args.n else None),
                            completed=(None if args.a else (True if args.c else False)))
        elif args.cmd == "today" or args.cmd == "agenda":
            self.list_tasks(due_dates=[datetime.datetime.today().date(), datetime.datetime.today().date()],
                            completed=(None if (args.c == args.u) else (args.c or not args.u)))
        elif args.cmd in ["tick", "untick"]:
            for task_id in args.task_id:
                self.database.tick_task_id(str(task_id), True if args.cmd == "tick" else False)
            self.save_database()
        # os.system("cls")

    def load_database(self):
        try:
            os.chdir(os.getcwd()+r"\saves")
            max_save = max([int(file.strip("save-.json")) for file in glob.glob("*.json")])
            with open("save-{}.json".format(str(max_save)), 'r') as file:
                self.database.set_database(json.load(file))
            file.close()
            Task.num_tasks_generated = self.database.get_length()
        except FileNotFoundError as _:
            Task.num_tasks_generated = 0
            pass
        except ValueError as _:
            Task.num_tasks_generated = 0
            pass

    def save_database(self):

        with open("save-{}.json".format(int(time.time())), 'w') as file:
            file.write(json.dumps(self.database.get_database()))
        file.close()

    def add_task(self):
        self.database.add_task(Task(task='Testing a long phrase'))

    def query_tasks(self, due_dates=None, labels=None, completed=None):
        tasks = {}
        for key, task_dict in self.database.get_database().items():
            dt = self.parse_due_date(task_dict['due_date'], task_dict['due_time'])
            # If we specify due dates, but task doesn't have one, disregard it
            if due_dates is not None and dt is None:
                continue
            if ((due_dates is None) or (due_dates[0] <= dt.date() <= due_dates[1])) \
                    and ((labels is None) or (any([label in task_dict['labels'] for label in labels]))) and \
                    ((completed is None) or task_dict['done'] == completed):
                tasks[key] = task_dict
        return tasks

    def list_tasks(self, due_dates=None, labels=None, completed=None):
        spacings = self._find_max_spacing()
        db = self.query_tasks(due_dates=due_dates, labels=labels, completed=completed)
        if len(db) > 0:
            keys = db[[key for key in db.keys()][0]].keys()
            header = " id | "
            for key in keys:
                header += key.center(spacings[key])
                header += " | "
            print(header)
            print("-" * len(header))
        else:
            print("No matching tasks!")
        for key, task_dict in db.items():
            line = (str(key) + ".").center(4) + "| "
            for key, val in task_dict.items():
                if key == 'done':
                    line += ("[ ]" if not val else "[X]").center(spacings[key])
                elif key == 'recurrence':
                    line += self.parse_recurrence(task_dict['recurrence']).ljust(spacings[key])
                elif key == 'labels' and val is not None:
                    label_str = ""
                    for label in val:
                        label_str += label
                    line += label_str.strip(",").ljust(spacings[key])
                else:
                    line += str(val).center(spacings[key])
                line += " | "
            print(line)

    def parse_due_date(self, due_date, due_time=None):
        if not due_date:
            return None
        sep = ""
        if "/" in due_date:
            sep = "/"
        elif "-" in due_date:
            sep = "-"
        m, d, y = [int(num) for num in due_date.split(sep)]
        if not due_time:
            return datetime.datetime(month=m, day=d, year=y)
        hr, mn, _ = due_time.split(":")
        return datetime.datetime(month=m, day=d, year=y, hour=int(hr), minute=int(mn))

    def parse_duration(self, duration, start_datetime=datetime.datetime.today(), return_string=True):
        dt = start_datetime
        if duration[-1] == 'd':
            dt += relativedelta(days=int(duration[0]))
        elif duration[-1] == 'w':
            dt += relativedelta(weeks=int(duration[0]))
        elif duration[-1] == 'm':
            dt += relativedelta(months=int(duration[0]))
        elif duration[-1] == 'y':
            dt += relativedelta(years=int(duration[0]))
        if return_string:
            return dt.strftime("%m/%d/%Y")
        else:
            return dt

    def parse_recurrence(self, string):
        """
        Takes string of form [interval between weeks][days of the week][duration]
        :param string:
        :return:
        """
        if string is None or string == "None":
            return "None"
        else:
            "Get first number in string"
            parsed = ""
            interval = ""
            days = ""
            i = 0
            while string[i].isdigit():
                interval += string[i]
                i += 1
            while not string[i].isdigit():
                days += string[i]
                i += 1
            duration = string[i:]
            if days == "MTWRFSU" or days == "A":
                parsed += "every day"
            elif int(interval) == 1:
                parsed += "every week, on "
            else:
                parsed += "every {} weeks, on ".format(int(interval))
            parsed += days + " until "
            dt = datetime.datetime.today()
            parsed += self.parse_duration(duration, dt)
            return parsed

    def _find_max_spacing(self):
        """
        Returns longest length entry for each property
        :return:
        """
        db = self.database.get_database()
        keys = db["1"].keys()
        spacings = {key: max(max([len(str(entry)) for entry in self.database.get_column(key)]), len(key)) for key in
                    keys}
        spacings['recurrence'] = max(
            max([len(self.parse_recurrence(str(entry))) for entry in self.database.get_column('recurrence')]),
            len("recurrence"))
        return spacings


def check_args(args):
    error = False
    if args.cmd not in ["add", "agenda", "del", "list", "tick", "today", "untick"]:
        error = True
    if error:
        sys.exit(0)


if __name__ == '__main__':
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='cmd')

    parser_add = subparsers.add_parser("add")
    parser_add.add_argument("task_name", action="store")
    parser_add.add_argument("-d", action="store", nargs=2, help="Specify due date and time")
    parser_add.add_argument("-dd", action="store", nargs=1, help="Specify due date only")
    parser_add.add_argument("-l", action="store", nargs='+', help="Specify labels")
    parser_add.add_argument("-td", action="store_true", help="Specify due date as today")
    parser_add.add_argument("-r", action="store",
                            help="Specify a recurrence string of form [interval][days of the week][duration]")

    parser_del = subparsers.add_parser("del")
    parser_del.add_argument("task_id", type=int, action="store", nargs='+')

    parser_list = subparsers.add_parser("list", help="Show list of all uncompleted tasks")
    parser_list.add_argument("-a", action="store_true", help="Show both completed and uncompleted tasks")
    parser_list.add_argument("-c", action="store_true", help="Show only completed tasks")
    parser_list.add_argument("-n", action="store", nargs=1, help="Show all uncompleted tasks in specified duration from today")

    parser_set = subparsers.add_parser("set")
    parser_set.add_argument("-r", action="store")

    parser_tick = subparsers.add_parser("tick")
    parser_tick.add_argument("task_id", type=int, action="store", nargs='+')

    parser_today = subparsers.add_parser("today", help='Show agenda of tasks due today', aliases=["agenda"])
    parser_today.add_argument("-c", action="store_true", help="Show only completed tasks")
    parser_today.add_argument("-u", action="store_true", help="Show only uncompleted tasks")

    parser_untick = subparsers.add_parser("untick")
    parser_untick.add_argument("task_id", type=int, action="store", nargs='+')

    args = parser.parse_args()
    check_args(args)
    main = Main(args=args)
