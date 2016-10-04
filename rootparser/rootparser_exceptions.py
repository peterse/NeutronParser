"""Exceptions for modules in this specific library"""
import os #_exit()

#Setting general logging preferences
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

import sys
from rootpy import log
log = log["rootparser_exceptions.py"]
log.debug("Debug test statement")

class ParallelError(Exception):
    """Thrown when the multithreading Pool or ThreadPool reaches unexpected behavior"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

#FIXME: better way of handling these kinds of exceptions
class ChildThreadError(Exception):
    """Kill the entire process via a child thread"""
    def __init__(self, *args, **kwargs):
        #Raise the typical exception
        #super(ChildThreadError).__init__(*args, **kwargs)
        #os._exit(1)
        print "ERROR: A child thread encountered fatal error"
        raise OSError

class RootFileError(Exception):
    """Root file does not exist"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#Logging and Error Message Suppression

#Set suppression to < INFO
log.setLevel(log.INFO)

#Filter GetBasket warnings for access collisions
import logging
class SuppressBasketFilter(logging.Filter):
    #Catch basket filter errors and essentially downgrade them to info statements
    def filter(self, record):
        logging.info("Access colission detected:\n %s" % record.msg)
        return False
        #return "Root.TBranch.GetBasket"
log["/ROOT.TBranch.GetBasket"].addFilter(SuppressBasketFilter())

logging.info("Logging configured")

if __name__ == "__main__":
    #raise ParallelError("parallel error")
    raise RootFileError("RootFileError")
