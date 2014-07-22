$(document).ready(function(){

	function getCookie(name){
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
					var cookie = jQuery.trim(cookies[i]);
					// Does this cookie string begin with the name we want?
		 
					if (cookie.substring(0, name.length + 1) == (name + '=')) {
						cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
						break;
					}
			}
		}
		return cookieValue;
	}
	 
	$.ajaxSetup({
		beforeSend: function(xhr, settings) {
			if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
				// Only send the token to relative URLs i.e. locally.
				xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
			}
		}
	});
	
	
	$(".cart").on("click", function(){
		var prod_id = $(this).data("prod");
		var stock = $(this).data("qty");
		var parent = $(this).parents(".product_details").first();
		var qty = $(parent).find("input").val();
		data = validate_data(qty, stock);
		console.log(data);
		if (data){
			add_to_cart(qty, prod_id);
		}
		
	})

	
	$(".cart_container").on("click", ".edit", function(){
		var prod_id = $(this).data("prod");
		var stock = parseInt($("body").find("#stock"+ prod_id).text()); //data("qty");
		var parent = $(this).parents(".quant").first();
		var input_field = $(parent).find("input")
		if (input_field.length == 0){
			var input_qty = $(parent).find(".input_qty")		
			var elem = $('<p><label for="p_scnts"><input type="text" id="p_scnt" size="5" name="quant" value="" placeholder="Quantity" /></label> <button id="remScnt">OK</button></p>');
			$(elem).appendTo($(input_qty));
		}
		$(".cart_container").on("click", "button", function(){
		var qty = $(parent).find("input").val();
		console.log(qty);
		data = validate_data(qty, stock);
		if (data){
			add_to_cart(qty, prod_id)
		}
		
		});
		

		
	})
	
	function add_to_cart(qty, prod_id){
		console.log("bine ma");
		$.ajax({
	        type: "POST",
	        url: "/store/addtocart/",
	        data: { qty: qty, prod_id: prod_id} ,
	        cache: false,
	        success: function(data) {
	        	$(".cart_container").html(data);
	        	}
	        });
		
	}
	
	function validate_data(qty, stock){
		if (qty ==""){
			var div = $("body").find(".error").first().text("Enter a valid quantity").show().delay(3000).fadeOut();
			return false;
		}
		if (qty < 0){
			var div = $("body").find(".error").first().text("Enter a positive quantity").show().delay(3000).fadeOut();
			return false;
		}
		if (qty > stock){
			var div = $("body").find(".error").first().text("We don't have the required amount").show().delay(3000).fadeOut();
			return false;
		}
		return true
	}
});
