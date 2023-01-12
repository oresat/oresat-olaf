from pathlib import Path
from enum import IntEnum, auto

from loguru import logger

from ...common.resource import Resource
from ...common.timer_loop import TimerLoop
from ..updater import Updater, UpdaterError


class Subindex(IntEnum):
    STATUS = auto()
    UPDATES_CACHED = auto()
    LIST_AVAILABLE = auto()
    UPDATE = auto()
    MAKE_STATUS_FILE = auto()


class UpdaterResource(Resource):
    '''Resource for interacting with the updater'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._updater = Updater('/tmp/updater', f'{Path.home()}/.cache/oresat/updates')

        self.index = 0x3100

        self.timer_loop = TimerLoop('updater resource', self._loop, 0.5)

    def _loop(self):

        for i in self.fwrite_cache.files('update'):
            self._updater.add_update(self.fwrite_cache.dir + '/' + i)

        if self.update_obj.value:
            try:
                self._updater.update()
            except UpdaterError as exc:
                logger.critical(exc)
            self.update_obj.value = False

        if self.make_status_obj.value:
            status_archive_file_path = self._updater.make_status_archive()
            self.fread_cache.add(status_archive_file_path, consume=True)
            self.make_status_obj.value = False

        return True

    def on_start(self):

        record = self.od[self.index]
        self.update_obj = record[Subindex.UPDATE.value]
        self.make_status_obj = record[Subindex.MAKE_STATUS_FILE.value]
        self.timer_loop.start()

        # make sure defaults are set correctly (override the values from eds/dcf)
        self.update_obj.value = False
        self.make_status_obj.value = False

    def on_end(self):

        self.timer_loop.stop()

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.index:
            if subindex == Subindex.STATUS:
                ret = self._updater.status.value
            elif subindex == Subindex.UPDATES_CACHED:
                ret = self._updater.updates_cached
            elif subindex == Subindex.LIST_AVAILABLE:
                ret = ' '.join(self._cache.files())

        return ret
