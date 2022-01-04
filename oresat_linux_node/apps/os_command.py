'''App for running OS (bash) commands over CAN bus'''

import subprocess
from enum import IntEnum

import canopen

from ..common.app import App


class OSCommandState(IntEnum):
    NO_ERROR_NO_REPLY = 0x00
    NO_ERROR_REPLY = 0x01
    ERROR_NO_REPLY = 0x02
    ERROR_REPLY = 0x03
    EXECUTING = 0xFF


class OSCommandApp(App):

    def __init__(self, node: canopen.LocalNode):

        super().__init__('OS Command', 0.5)

        self.failed = False

        self.index = 0x1023
        self.subindex_command = 0x01
        self.subindex_state = 0x02
        self.subindex_reply = 0x03

        self.command = ''
        self.state = OSCommandState.NO_ERROR_NO_REPLY
        self.reply = ''
        self.reply_max_len = 10000

        node.add_read_callback(self.on_read)
        node.add_write_callback(self.on_write)

    def end(self):
        self.failed = True
        self.command = ''
        self.state = OSCommandState.ERROR_NO_REPLY
        self.reply = ''

    def on_read(self, index, subindex, od):
        '''Callback for a SDO read the command and/or reply domain values'''

        ret = None

        if index == self.index and not self.failed:
            if subindex == self.subindex_command:
                ret = self.command.encode()
            elif subindex == self.subindex_state:
                ret = self.state.value
            elif subindex == self.subindex_reply:
                ret = self.reply.encode()

        return ret

    def on_write(self, index: int, subindex: int, od: canopen.ObjectDictionary, data: bytes):
        '''Callback for a SDO write for an OS command'''

        if index == self.index and \
                subindex == self.subindex_command and \
                self.state != OSCommandState.EXECUTING and \
                not self.failed:

            self.reply = ''
            self.command = data.decode()
            self.state = OSCommandState.EXECUTING  # run os command

    def loop(self):
        '''Run the command and get the reply'''

        if self.state == OSCommandState.EXECUTING:
            print('Running OS command: ' + self.command)

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
