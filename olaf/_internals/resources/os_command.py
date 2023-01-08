import subprocess
from enum import IntEnum

from loguru import logger

from ...common.resource import Resource
from ...common.timer_loop import TimerLoop


class OSCommandState(IntEnum):
    NO_ERROR_NO_REPLY = 0x00
    NO_ERROR_REPLY = 0x01
    ERROR_NO_REPLY = 0x02
    ERROR_REPLY = 0x03
    EXECUTING = 0xFF


class OSCommandResource(Resource):
    '''Resource for running OS (bash) commands over CAN bus as defined by CiA 301 specs'''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.index = 0x1023
        self.sub_command = 0x01
        self.sub_state = 0x02
        self.sub_reply = 0x03

        self.command = ''
        self.state = OSCommandState.NO_ERROR_NO_REPLY
        self.reply = ''
        self.reply_max_len = 10000

        self.timer_loop = TimerLoop('os command resource', self._loop, 0.5,
                                    exc_func=self._loop_error)
        self.failed = False

    def _loop(self):

        if self.state == OSCommandState.EXECUTING:
            logger.info('Running OS command: ' + self.command)

            out = subprocess.run(self.command, capture_output=True, shell=True)
            if out.returncode != 0:  # error
                self.reply = out.stderr[:self.reply_max_len].decode()
                if self.reply:
                    self.state = OSCommandState.ERROR_REPLY
                else:
                    self.state = OSCommandState.ERROR_NO_REPLY
            else:  # no error
                self.reply = out.stdout[:self.reply_max_len].decode()
                if self.reply:
                    self.state = OSCommandState.NO_ERROR_REPLY
                else:
                    self.state = OSCommandState.NO_ERROR_NO_REPLY

            logger.info('OS command has completed')

        return True

    def _loop_error(self, exc: Exception):

        self.failed = True
        self.command = ''
        self.state = OSCommandState.ERROR_NO_REPLY
        self.reply = ''

    def on_start(self):

        self.timer_loop.start()

    def on_end(self):

        self.timer_loop.stop()

    def on_read(self, index, subindex, od):

        ret = None

        if index == self.index and not self.failed:
            if subindex == self.sub_command:
                ret = self.command.encode()
            elif subindex == self.sub_state:
                ret = self.state.value
            elif subindex == self.sub_reply:
                ret = self.reply.encode()

        return ret

    def on_write(self, index, subindex, od, data):

        if index == self.index and subindex == self.sub_command:
            if self.state == OSCommandState.EXECUTING or self.failed:
                logger.eror('cannot start another os command when one is running')
                return

            self.reply = ''
            self.command = data.decode()
            self.state = OSCommandState.EXECUTING  # run os command
