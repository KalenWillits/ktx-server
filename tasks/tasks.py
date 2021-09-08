class Task:
    def __init__(self, type):
        self.type = type

    def run(self):
        '''
        Overwrite this method to create custom tasks.
        Tasks in startup and shutdown are syncronous tasks,
        tasks in loop are asyncronous.
        '''
        raise Exception(f"[{self.__name__}] - Task - Run method not implimented")


class TaskManager:
    def __init__(self, type: str = "", tasks: list = list()):
        self.startup_queue = list()
        self.loop_queue = list()
        self.shutdown_queue = list()

        for task in tasks:
            if task.type == 'startup':
                self.startup_queue.append(task)
            elif task.type == 'loop':
                self.loop_queue.append(task)
            elif task.type == 'shutdown':
                self.shutdown_queue.append(task)
            else:
                raise Exception(f'{task.type} is an invalid task type. task type is required.')

    def run_startup_tasks(self):
        for task in self.startup_queue:
            task.run()

    async def run_loop_tasks(self):
        while True:
            for task in self.loop_queue:
                await task.run()

    def run_shutdown_tasks(self):
        for task in self.shutdown_queue:
            task.run()
