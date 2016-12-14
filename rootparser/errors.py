#TODO: write this (called from PArallel.run() up as an official error:
# @versioncontrol
# def fetch_n_parts_mc(evt, nparts_leaf="MC_N_PART"):
#     while True:
#         try:
#             k = IO.tree.GetEvent(evt.index)
#             out = int(IO.tree.GetLeaf("event").GetValue())
#             #Odd out-of-synch...
#             if out != evt.index:
#                 print evt.index, out
#             return out
#
#         except:
#             #There was a clash for access, take a nap!:
#             time.sleep(.001)
#         else:
#             pass
#This resulted in failure to read the tree that was handled within the object
#Solution: Create a global tree located in IO module
