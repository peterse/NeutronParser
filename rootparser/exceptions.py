"""Exceptions for modules in this specific library"""

class ParallelError(Exception):
    """Thrown when the multithreading Pool or ThreadPool reaches unexpected behavior"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class RootFileError(Exception):
    """Root file does not exist"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MissingBranchError(Exception):
    """The branch you're trying to access doesn't exist"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)    

if __name__ == "__main__":


    #raise ParallelError("parallel error")
    raise RootFileError("RootFileError")
