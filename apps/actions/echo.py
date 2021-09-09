from actions import Action

class Echo(Action):
    key = "echo"

    def execute(*args, **kwargs):
        content = kwargs.get("content")
        return {"content": content}
