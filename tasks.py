import asyncio
from enum import Enum


class TaskTypes(Enum):
    STARTUP = "Startup"
    INTERVAL = "Interval"
    SHUTDOWN = "Shutdown"


class BaseTask:
    def __init__(self):
        self._name = self.__class__.__name__
        self._type = next(iter(self.__class__.__bases__)).__name__

    def completed(self):
        self.complete = True


class Startup(BaseTask):
    priority = None

    async def execute(self, **kwargs):
        "Overwrite this method to create custom tasks."
        raise Exception(f"[ERROR] Task {self.__class__.__name__} execute method not implimented")


class Interval(BaseTask):
    def set(self, **kwargs) -> int:
        """
        Overwrite this function to return the interval of time between task executions in seconds
        as an integer.
        """
        raise Exception(f"[ERROR] Task {self._name} set method not implimented")

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
            TaskTypes.STARTUP.value: [],
            TaskTypes.INTERVAL.value: [],
            TaskTypes.SHUTDOWN.value: [],
        }

        for task in tasks:
            task_instance = task()
            self.__tasks__[task_instance._type].append(task_instance)

        self.sort_tasks(TaskTypes.STARTUP.value)
        self.sort_tasks(TaskTypes.SHUTDOWN.value)

    def sort_tasks(self, type: str):
        self.__tasks__[type].sort(key=lambda task: task.priority if task.priority else len(self.__tasks__[type]))

    async def execute_startup_tasks(self, **kwargs):
        for task in self.__tasks__[TaskTypes.STARTUP.value]:
            asyncio.ensure_future(task.execute(**kwargs))

    async def execute_interval_tasks(self, **kwargs):
        while True:
            for task in self.__tasks__[TaskTypes.INTERVAL.value]:
                await asyncio.sleep(task.set(**kwargs))
                asyncio.ensure_future(task.execute(**kwargs))

            if not self.__tasks__[TaskTypes.INTERVAL.value]:
                break

    async def execute_shutdown_tasks(self, **kwargs):
        for task in self.__tasks__[TaskTypes.SHUTDOWN.value]:
            asyncio.ensure_future(task.execute(**kwargs))
