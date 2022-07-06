import asyncio
from enum import Enum


class TaskTypes(Enum):
    STARTUP = 'Startup'
    INTERVAL = 'Interval'
    SHUTDOWN = 'Shutdown'


class BaseTask:
    def __init__(self):
        self._name = self.__class__.__name__
        self._type = next(iter(self.__class__.__bases__)).__name__


class Startup(BaseTask):
    priority = None

    def delay(self, **kwargs):
        '''Overwrite this method to add a delay before executing the startup task.
        This will also delay subsequent tasks from starting.'''
        return 0

    async def execute(self, **kwargs):
        'Overwrite this method to create custom tasks.'
        raise Exception(f'[ERROR] Task {self.__class__.__name__} execute method not implemented')


class Interval(BaseTask):
    def timer(self, **kwargs) -> int:
        '''
        Overwrite this function to return the interval of time between task executions in seconds
        as an integer.
        '''
        raise Exception(f'[ERROR] Task {self._name} timer method not implemented')

    async def execute(self, **kwargs):
        'Overwrite this method to create custom tasks.'
        raise Exception(f'[ERROR] Task {self.__class__.__name__} execute method not implemented')


class Shutdown(BaseTask):
    priority = None

    async def execute(self, **kwargs):
        'Overwrite this method to create custom tasks.'
        raise Exception(f'[ERROR] Task {self.__class__.__name__} execute method not implemented')


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

    def execute_startup_tasks(self, **kwargs):
        for task in self.__tasks__[TaskTypes.STARTUP.value]:
            task.execute(**kwargs)

    async def schedule_task(self, task, **kwargs):
        await asyncio.sleep(task.timer(**kwargs))
        await task.execute(**kwargs)
        self.__tasks__[TaskTypes.INTERVAL.value].append(task)

    async def execute_interval_tasks(self, **kwargs):
        while True:
            await asyncio.sleep(0.1)
            if self.__tasks__[TaskTypes.INTERVAL.value]:
                task = self.__tasks__[TaskTypes.INTERVAL.value].pop()
                asyncio.ensure_future(self.schedule_task(task, **kwargs))

    def execute_shutdown_tasks(self, **kwargs):
        for task in self.__tasks__[TaskTypes.SHUTDOWN.value]:
            task.execute(**kwargs)
