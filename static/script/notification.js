$(".notification").on("click", function(e){
	$this = this
	$.ajax({
        type: "POST",
        url: "/store/notification/",
        cache: false,
        success: function(data) {
        	console.log($this);
        	console.log($($this).parent().find('#dropdown'));
        	$($this).parent().find('#dropdown').html(data);
        	$($this).find('span').remove();
        	}
        });
})