'''OreSat Linux node app'''


class App:

    def __init__(self, name: str, delay: float = 1.0):
        '''OreSat Linux app

        Parameters
        ----------
        name: str
            Unique name for the app
        delay: float
            Delay between loop calls in seconds. Set to a negative number if loop is not needed
        '''

        self._name = name
        self._delay = delay

    def setup(self):
        '''Setup the app. Should be used to setup hardware.'''

        pass

    def on_loop(self):
        '''This is called all in loop every :py:data:`delay` seconds.'''

        pass

    def end(self):
        '''Called when the program ends or the apps fails. Should be used to stop hardware and
        can be used to zero/clear app's data in od as needed.'''

        pass

    @property
    def name(self):
        '''str: App's unique name. Read only.'''

        return self._name

    @property
    def delay(self):
        '''str: Delay between :py:func:`on_loop` calls. If it is a negative number on_loop will
        not be called. Read Only.'''

        return self._delay
