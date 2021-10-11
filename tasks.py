import asyncio
from enum import Enum
from datetime import datetime, timedelta

from utils import Object, ServerTime


class TaskTypes(Enum):
    STARTUP = "Startup"
    INTERVAL = "Interval"
    SHUTDOWN = "Shutdown"


class BaseTask:
    complete: bool = False

    def __init__(self):
        self._name = self.__class__.__name__
        self._type = super().__name__

    def completed(self):
        self.complete = True


class Startup(BaseTask):
    def __init__(self, priority: int = None):
        self.priority = priority

    async def execute(self, **kwargs):
        "Overwrite this method to create custom tasks."
        raise Exception(f"[ERROR] Task {self.__class__.__name__} execute method not implimented")


class Interval(BaseTask):
    interval = lambda **kwargs: 60*60  # One hour

    async def execute(self, **kwargs):
        "Overwrite this method to create custom tasks."
        raise Exception(f"[ERROR] Task {self.__class__.__name__} execute method not implimented")


class Shutdown(BaseTask):
    priority = None

    async def execute(self, **kwargs):
        "Overwrite this method to create custom tasks."
        raise Exception(f"[ERROR] Task {self.__class__.__name__} execute method not implimented")


class Task:
    Startup = Startup
    Interval = Interval
    Shutdown = Shutdown


class TaskManager:
    def __init__(self, *tasks: BaseTask):
        self._types = TaskTypes

        self.__tasks__ = {
            TaskTypes.STARTUP: [],
            TaskTypes.INTERVAL: [],
            TaskTypes.SHUTDOWN: [],
        }

        for task in tasks:
            task_instance = task()
            self.__tasks__[task_instance._type].append(task_instance)

        self.sort_tasks(TaskTypes.STARTUP)
        self.sort_tasks(TaskTypes.SHUTDOWN)

    def sort_tasks(self, type: str):
        self.__tasks__[type].sort(key=lambda task: task.priority if task.priority else len(self.__tasks__[type]))

    def execute_startup_tasks(self, **kwargs):
        for task in self.__tasks__[TaskTypes.STARTUP]:
            asyncio.ensure_future(task.execute(**kwargs))

    async def execute_interval_tasks(self, **kwargs):
        while True:
            for task in self.__tasks__[TaskTypes.INTERVAL]:
                asyncio.sleep(task.interval(**kwargs))
                await task.execute(**kwargs)

            if not self.__tasks__[TaskTypes.INTERVAL]:
                break


    def execute_shutdown_tasks(self, **kwargs):
        for task in self.__tasks__[TaskTypes.SHUTDOWN]:
            asyncio.ensure_future(task.execute(**kwargs))
