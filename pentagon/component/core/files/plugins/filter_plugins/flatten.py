# This function will take an irregular list composed of lists 
# and flatten it

from compiler.ast import flatten

class FilterModule (object):
    def filters(self):
        return {
            "flatten": flatten
        }
