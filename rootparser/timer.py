import time

class Timer():
    """Define a timer class to be instantiated once. Wrap routines to time with start() and end()"""

    def __init__(self):
        self.count = 0
        self.t0 = 0
        self.name = None

    def start(self, name=None):
        #Naming a timer sequence
        if name:
            self.name = name
        else:
            self.name = None

        self.t0 = time.clock()

    def end(self):
        self.t1 = time.clock()
        dt = self.t1 - self.t0
        if self.name:
            print "Routine '%s': Time elapsed: %f" % (self.name, dt)
        else:
            print "Index '%i': Time elapsed: %f" % (self.count, dt)

        self.count += 1
