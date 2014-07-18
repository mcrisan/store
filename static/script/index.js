/* set equal height thumbnail images*/
$(document).ready(function(){
	$('.thumbnail .product_image').css({
	    'height': $('.thumbnail .product_image').height()
	});
	
function load_wish_button(){
	$.ajax({
        type: "POST",
        url: "/store/check_wishlist/",
        cache: false,
        success: function(data) {
        	$(".cart_container").html(data);
        	}
        });
}	
});
