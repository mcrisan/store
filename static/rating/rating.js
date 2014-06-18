$(document).ready(function(){
	
$.fn.raty.defaults.path = '/static/images';

$.ajax({
    type: "POST",
    url: "/store/product_rating/",
    data: { prod_id: $('.rating').attr('id')} ,
    cache: false,
    success: function(data) {
    	$('.rating').data( "rate", data['readonly'] );
    	rating(data['rate'], data['readonly']);
    }
});

$('.rating').on('click', function(){
	    if ($('.rating').data( "rate") == false){
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

function rating(rate, enable){
$('.rating').raty({
	  score:rate,
	  readOnly   : enable,
	});
}



});