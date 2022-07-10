from pathlib import Path

from pynicotine.pluginsystem import BasePlugin

from stats import UploadedItem, UploadedItems

PLUGIN_FOLDER = Path(__file__).resolve().parent
UPLOAD_STATS_FILE = PLUGIN_FOLDER / "stats" / "uploads.json"


class Plugin(BasePlugin):
    __unload_is_called__: bool = False

    def loaded_notification(self):
        self.log("My attributes are set!")
        self.log(f"I was loaded in {__file__}")
        self.log(f"{PLUGIN_FOLDER = }")
        try:
            self.uitems = UploadedItems.from_path(UPLOAD_STATS_FILE)
            self.log("Found existing stats file!")
        except FileNotFoundError:
            self.log("Stats file not found! Creating anew...")
            self.uitems = UploadedItems(UPLOAD_STATS_FILE)
        finally:
            self.log("Loaded stats file!")

    def unload(self, once: bool = True):
        """Dumps the file.
        If once is True, and the function has already been called previously,
        then the method simply exits.
        """
        # I'm not quite sure of the behavior of shutdown_notification (does .unloaded_notification
        # get called in the event of a shutdown? I couldn't tell you), so my hacky solution was to
        # add a cached property, ensuring that it only gets called once.
        if once and self.__unload_is_called__:
            return
        self.uitems.to_path()
        self.__unload_is_called__ = True
        self.log("Dumped stats file!")

    unloaded_notification = unload
    shutdown_notification = unload

    def upload_finished_notification(self, user: str, virtual_path: str, real_path: str):
        if virtual_path not in self.uitems:
            self.uitems[virtual_path] = UploadedItem()
        if user not in self.uitems[virtual_path]:
            self.uitems[virtual_path][user] = 0
        self.uitems[virtual_path][user] += 1
