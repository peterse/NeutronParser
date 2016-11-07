import time

class Timer():
    """Define a timer class to be instantiated once. Wrap routines to time with start() and end()"""

    def __init__(self, quiet=False):
        self.count = 0
        self.t0 = 0
        self.name = None
        self.quiet = quiet

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
        #Either print the timing results to the shell, or return the values
        if self.quiet:
            return dt
        else:
            if self.name:
                print "Routine '%s': Time elapsed: %f" % (self.name, dt)
            else:
                print "Index '%i': Time elapsed: %f" % (self.count, dt)
            self.count += 1
            return dt
