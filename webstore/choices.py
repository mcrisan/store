import collections

from collections import namedtuple

Status = namedtuple("Status" ,["Active", "Pending", 'Finished'])
s = Status(Active='0', Pending='1', Finished='2')

def get_field_choices(named):
    """
    Namedtuple expected, return Django field choices
    """
    dictionary = named._asdict()
    return [(v, k) for (k, v) in dictionary.items()]

class Choices():
     
    def get_field_choices(self):
        """
        Namedtuple expected, return Django field choices
        """
        dictionary = self._asdict()
        return [(v, k) for (k, v) in dictionary.items()]


class Status(Choices, collections.namedtuple("Status", ["Active" , "Pending", 'Finished'])):
    __slots__ = ()
    
    def __new__(cls):
        return super(cls, Status).__new__(cls, 0, 1, 2) 
     
  

   
    
         
