$(document).ready(function(){

$('.wishlist').on('click', '.wishlist_button', function(event){
	event.preventDefault();
	href = $(this).data('href')
	$this=this
	$.ajax({
        type: "POST",
        url: href,
        cache: false,
        dataType: "json",
        success: function(data) {
        	$($this).data('href', data['href']);
        	$($this).text(data['text']);
        	$("body").find(".error").first().text(data['message']).show().delay(3000).fadeOut();
        }
	  });
  })


});