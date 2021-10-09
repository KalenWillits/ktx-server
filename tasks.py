class Task:
    type = None

    def execute(self, **kwargs):
        '''
        Overwrite this method to create custom tasks.
        Tasks in startup and shutdown are syncronous tasks,
        tasks in loop are asyncronous.
        '''
        raise Exception("Task - execute method not implimented")


class TaskManager:
    def __init__(self, *tasks):
        self.startup_queue = []
        self.loop_queue = []
        self.shutdown_queue = []

        for task in tasks:
            if task.type == 'startup':
                self.startup_queue.append(task())
            elif task.type == 'periodic':
                self.loop_queue.append(task())
            elif task.type == 'shutdown':
                self.shutdown_queue.append(task())
            else:
                raise Exception(f'{task.type} is an invalid task type. task type is required.')

    def execute_startup_tasks(self, **kwargs):
        for task in self.startup_queue:
            task.execute(**kwargs)

    async def execute_periodic_tasks(self, **kwargs):
        while True:
            for task in self.loop_queue:
                await task.execute(**kwargs)

            if not self.loop_queue:
                break

    def execute_shutdown_tasks(self, **kwargs):
        for task in self.shutdown_queue:
            task.execute(**kwargs)
