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
		if (qty ==""){
			var div = $("body").find(".error").first().text("Enter a valid quantity").show().delay(3000).fadeOut();
			return;
		}
		if (qty < 0){
			var div = $("body").find(".error").first().text("Enter a positive quantity").show().delay(3000).fadeOut();
			return;
		}
		if (qty > stock){
			var div = $("body").find(".error").first().text("We don't have the required amount").show().delay(3000).fadeOut();
			return;
		}
		
		console.log(div);
		$.ajax({
	        type: "POST",
	        url: "/store/addtocart/",
	        data: { qty: qty, prod_id: prod_id} ,
	        cache: false,
	        success: function(data) {
	        	set_data(data['prod_id'], data['quantity'], data['price'], data['total_price'], data['stock']);
	        	}
	        });
		
	})
	
	function set_data(prod_id, quant, price, total_price, stock){
		cart_div =$("body").find(".cart_details");
		$("body").find("#stock"+ prod_id).text(stock);
		row = $(cart_div).find('[data-id="'+prod_id+'"]');
		if (row.length > 0){
		$(row).find(".quantity").text(quant);
		$(row).find(".price").text(price);
		$(cart_div).find('.total').text("Total: " + total_price)
		}else{
			window.location.reload(false);
			
		}
	}
	
	$(".edit").on("click", function(){
		var prod_id = $(this).data("prod");
		var stock = parseInt($("body").find("#stock"+ prod_id).text()); //data("qty");
		var parent = $(this).parents(".quant").first();
		var input_field = $(parent).find("input")
		if (input_field.length == 0){
			var input_qty = $(parent).find(".input_qty")		
			console.log("input is" + input_qty)
			var elem = $('<p><label for="p_scnts"><input type="text" id="p_scnt" size="5" name="quant" value="" placeholder="Quantity" /></label> <button id="remScnt">OK</button></p>');
			$(elem).appendTo($(input_qty));
		}
		$("button").on("click", function(){
		var qty = $(parent).find("input").val();
		if (qty ==""){
			var div = $("body").find(".error").first().text("Enter a valid quantity").show().delay(3000).fadeOut();
			return;
		}
		if (qty < 0){
			var div = $("body").find(".error").first().text("Enter a positive quantity").show().delay(3000).fadeOut();
			return;
		}
		if (qty > stock){
			var div = $("body").find(".error").first().text("We don't have the required amount").show().delay(3000).fadeOut();
			return;
		}
		
		$.ajax({
	        type: "POST",
	        url: "/store/addtocart/",
	        data: { qty: qty, prod_id: prod_id} ,
	        cache: false,
	        success: function(data) {
	        	console.log(data);
	        	$(elem).remove();
	        	set_data(data['prod_id'], data['quantity'], data['price'], data['total_price'], data['stock']);
	        	}
	        });
		
		});
		

		
	})
});
