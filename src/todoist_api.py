import requests
import time

class TodoistApi:
    url = "https://api.todoist.com/rest/v2/tasks"
    token = None

    def set_token(self, token):
        self.token = token

    def add_task(self, task):
        response = requests.post(
            self.url,
            json={
                "content": task,
            },
            headers={
                "Authorization": "Bearer %s" % self.token,
                "X-Request-Id": str(time.time()),
                "Content-Type": "application/json",
            }
        )

        return None if response.status_code == 200 else "Error communicating with Todoist. Repsonse code is %s. " % response.status_code
