import logging
import time

import requests
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import \
    ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import \
    RenderResultListAction
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction
from ulauncher.api.shared.event import (ItemEnterEvent, KeywordQueryEvent,
                                        PreferencesEvent,
                                        PreferencesUpdateEvent)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

logger = logging.getLogger(__name__)

class TodoistCaptureExtension(Extension):

    url = "https://api.todoist.com/rest/v2/tasks"

    def __init__(self):
        super(TodoistCaptureExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent,
                       PreferencesUpdateEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        text = event.get_argument() or ""

        if text == "":
            return RenderResultListAction([ExtensionResultItem(
                icon='images/icon.png',
                name='Type something to capture',
                on_enter=HideWindowAction()
            )])

        return RenderResultListAction([
            ExtensionResultItem(
                icon='images/icon.png',
                name='Capture "%s"' % text,
                description='Hit enter to capture this note in your inbox!',
                on_enter=ExtensionCustomAction(text, keep_app_open=True)
            )
        ])



class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        logger.info("Capturing note: %s" % event.get_data())
        response = requests.post(
            extension.url,
            json={
                "content": event.get_data(),
            },
            headers={
                "Authorization": "Bearer %s" % extension.token,
                "X-Request-Id": str(time.time()),
                "Content-Type": "application/json",
            }
        )

        if response.status_code != 200:
            notify_message = "Error capturing note: %s" % response.status_code
            logger.error(notify_message)
            return RenderResultListAction([ExtensionResultItem(
                icon='images/icon.png',
                name=notify_message,
                description='Press enter to dismiss',
                on_enter=HideWindowAction()
            )])

        notify_message = "Note captured: %s" % event.get_data()
        logger.info(notify_message)
        return RenderResultListAction([ExtensionResultItem(
            icon='images/icon.png',
            name=notify_message,
            description='Press enter to dismiss',
            on_enter=HideWindowAction()
        )])





class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.token = event.preferences["api_token"]
        extension.keyword = event.preferences["keyword"]


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == "api_token":
            extension.token = event.new_value
            extension.keyword = event.preferences["keyword"]


if __name__ == "__main__":
    TodoistCaptureExtension().run()
