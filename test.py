import sys
import root_numpy
import rootpy
# try:
#     import rootpy
# except:
#     print "rootpy"
#     print sys.exc_info()[0]
#
# try:
#     import root_numpy
# except:
#     "print root_numpy"
#     print sys.exc_info()[0]
#
# try:
#     import ROOT
# except:
#     print "ROOT"
#     print sys.exc_info()[0]

def summ(x, y):
    return x + y

def collapse(*args):
    print args
    return summ(*args)


if __name__ == "__main__":

    #print collapse(1)
    print collapse(1,2)
