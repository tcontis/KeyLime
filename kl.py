from database import Database
from task import Task
from argparse import ArgumentParser
import json
import os
import sys
import datetime
from dateutil.relativedelta import relativedelta

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
                                        dt=self.parse_due_date(date, args.d[1] if args.d else None),
                                        recurrence=(args.r if args.r else None),
                                        labels=args.l if args.l else None
                                        ))
        elif args.cmd == "del":
            for task_id in args.task_id:
                self.database.remove_task_id(str(task_id))
        elif args.cmd in ["tick", "untick"]:
            for task_id in args.task_id:
                self.database.tick_task_id(str(task_id), True if args.cmd == "tick" else False)
        # os.system("cls")
        self.list_tasks()

    def load_database(self):
        try:
            with open("save.json", 'r') as file:
                self.database.set_database(json.load(file))
            file.close()
            Task.num_tasks_generated = self.database.get_length()
        except FileNotFoundError as _:
            Task.num_tasks_generated = 0
            pass

    def save_database(self):
        with open("save.json", 'w') as file:
            file.write(json.dumps(self.database.get_database()))
        file.close()

    def add_task(self):
        self.database.add_task(Task(task='Testing a long phrase'))

    def list_tasks(self):
        spacings = self._find_max_spacing()
        db = self.database.get_database()
        if self.database.get_length() > 0:
            keys = db["1"].keys()
            header = " id | "
            for key in keys:
                header += key.center(spacings[key])
                header += " | "
            print(header)
            print("-" * len(header))
        else:
            print("No tasks!")
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
        hr, mn = due_time.split(":")
        return datetime.datetime(month=m, day=d, year=y, hour=int(hr), minute=int(mn))

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
            duration = [ch for ch in string[i:]]
            if days == "MTWRFSU" or days == "A":
                parsed += "every day"
            elif int(interval) == 1:
                parsed += "every week, on "
            else:
                parsed += "every {} weeks, on ".format(int(interval))
            """
            if days != "MTWRFSU" and days != "A":
                day_dict = {"M": "Mondays", "T": "Tuesdays", "W": "Wednesdays", "R": "Thursdays", "F": "Fridays",
                            "S": "Saturdays", "U": "Sundays"}
                day_string = ""
                for day in days:
                    if len(days) > 2 and days[-1] == day:
                        day_string += "and "
                        day_string += day_dict[day] + ", "
                    elif len(days) == 2 and days[0] == day:
                        day_string += day_dict[day] + " and "
                    else:
                        day_string += day_dict[day] + ", "
                parsed += day_string.strip(", ") + " until "

            """
            parsed += days + " until "

            dt = datetime.datetime.today()
            if duration[-1] == 'd':
                dt += relativedelta(days=int(duration[0]))
            elif duration[-1] == 'w':
                dt += relativedelta(weeks=int(duration[0]))
            elif duration[-1] == 'm':
                dt += relativedelta(months=int(duration[0]))
            elif duration[-1] == 'y':
                dt += relativedelta(years=int(duration[0]))
            parsed += "{}/{}/{}".format(dt.month, dt.day, dt.year)
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
        spacings['recurrence'] = max(max([len(self.parse_recurrence(str(entry))) for entry in self.database.get_column('recurrence')]), len("recurrence"))
        return spacings


def check_args(args):
    error = False
    if args.cmd not in ["add", "del", "tick", "untick"]:
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
    parser_add.add_argument("-r", action="store", help="Specify a recurrence string of form [number days]")

    parser_del = subparsers.add_parser("del")
    parser_del.add_argument("task_id", type=int, action="store", nargs='+')

    parser_set = subparsers.add_parser("set")
    parser_set.add_argument("-r", action="store")

    parser_tick = subparsers.add_parser("tick")
    parser_tick.add_argument("task_id", type=int, action="store", nargs='+')

    parser_untick = subparsers.add_parser("untick")
    parser_untick.add_argument("task_id", type=int, action="store", nargs='+')

    args = parser.parse_args()
    check_args(args)
    main = Main(args=args)
    main.save_database()
