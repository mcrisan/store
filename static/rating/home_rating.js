$(document).ready(function(){
	
$.fn.raty.defaults.path = '/static/images';

var a=[]
$.each( $('.rating'), function( key, value ) {
	  a[key] = $(value).attr('id')
	});

$.ajax({
    type: "POST",
    url: "/store/product_rating/",
    data: { prod_id: a} ,
    cache: false,
    traditional: true,
    success: function(data) {
    	$.each( data, function( key, data ) {
    		  $('#'+data['prod_id']).data( "rate", data['readonly'] );
    		  rating(data['rate'], data['readonly'], data['prod_id']);
    		  if (data['wish']==true){
	    		  elem = $('<a/>', {
	    			    href: "#",
	    			    'data-href': 'http://localhost:8000/store/remove_wishlist/' + data['prod_id'] + '/',
	    			    'data-wishlist': data['prod_id'],
	    			    text: 'Remove from wishlist!',
	    			   'class': "wishlist_button btn-info"
	    			})
    		  }else{
        		 elem = $('<a/>', {
      			      //href: 'store/add_wishlist/' + data['prod_id'],
        			  href: "#",
      			     'data-href': 'store/add_wishlist/' + data['prod_id'] + '/',
    			     'data-wishlist': data['prod_id'],
      			      text: 'Add to wishlist!',
      			     'class': "wishlist_button btn-info"
      			  }) 
    		  }
        	  $(elem).appendTo($("[data-wishlist='" + data['prod_id'] + "']"));
    		});
    	rating(data['rate'], data['readonly']);
    }
});

$('.rating').on('click', function(){
	    if ($(this).data( "rate") == false){
		    value= $(this).find("input").val();
			$.ajax({
		        type: "POST",
		        url: "/store/rate/",
		        data: { prod_id: this.id, rating: value} ,
		        cache: false,
		        success: function(data) {
		        	rating(data['rate']);
		        }
		  });
	    }
	  })

function rating(rate, enable, prod_id){
$('#'+prod_id).raty({
	  score:rate,
	  readOnly   : enable,
	});
}



});