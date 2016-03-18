$('img').click(function(){
	$.post("signIn", function(data, status) {
		console.log("success!");
	})
})