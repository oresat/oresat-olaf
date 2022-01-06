'''OreSat Linux node app'''


class App:

    def __init__(self, name: str, delay: float = 1.0):
        '''OreSat Linux app'''

        self.name = name
        '''str: unique name for the app'''
        self.delay = delay
        '''float: delay between loop calls in seconds. set to a negative number if loop is not
        needed'''

    def setup(self):
        '''Setup the app. Should be used to setup hardware.'''

        pass

    def on_loop(self):
        '''This is called all in loop every `delay` seconds.'''

        pass

    def end(self):
        '''Called when the program ends or the apps fails. Should be used to
        stop hardware amd can be used to zero/clear app's data in od.'''

        pass
