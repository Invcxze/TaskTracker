class TaskService:
    @staticmethod
    def add_watcher(task, user):
        task.watchers.add(user)

    @staticmethod
    def remove_watcher(task, user):
        task.watchers.remove(user)
