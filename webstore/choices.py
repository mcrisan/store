import collections




class Choices(object):
     
    def get_field_choices(self):
        """
        Namedtuple expected, return Django field choices
        """
        dictionary = self._asdict()
        return [(v, k) for (k, v) in dictionary.items()]
    
    


#class Status(Choices, collections.namedtuple("Status", ["Active" , "Pending", 'Finished'])):
#    __slots__ = ()
    
#    def __new__(cls):
#        return super(cls, Status).__new__(cls, 0, 1, 2) 
    
class Status(Choices, collections.namedtuple("Status", ["Active" , "Pending", 'Finished'])):
    __slots__ = ()
    
    def __new__(cls, *args, **kwargs):
        return super(cls, Status).__new__(cls, 0, 1, 2) 
            
class Choice(object):

    def __init__(self, *args, **kwargs):
        self.choices = tuple()
        for k, v in kwargs.iteritems():
            setattr(self, k, v[0])
            self.choices += (v,)            


DISCOUNT_STATUS_CHOICES = Choice(ACTIVE=('0', 'Active'),
                                 PENDING=('1', 'Pending'),
                                 FINISHED=('2', 'Finished'),                                
                                 )

CART_STATUS_CHOICES = Choice(ACTIVE=('0', 'Active'),
                             ORDERED=('1', 'Ordered'),                               
                             )
     
  

   
    
         
