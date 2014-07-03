import collections
   
            
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

HAS_DISCOUNT_CHOICES = Choice(NO=('0', 'No'),
                              YES=('1', 'Yes'),                               
                             )
     
  

   
    
         
