import dbsettings

    
class SiteSettings(dbsettings.Group):
    enabled = dbsettings.BooleanValue('Send email after purchase', default=False)
    sender = dbsettings.StringValue('address to send emails from')
    subject = dbsettings.StringValue()  
    products_per_page = dbsettings.PositiveIntegerValue(
                        'Number of products to be displayed on a page',
                        default=20) 
    remove_cart = dbsettings.PositiveIntegerValue(
                        'Remove cart after how many days of inactivity',
                        default=1)
    
    