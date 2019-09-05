var mimeTypes = ['jpg', 'bmp', 'png', 'tif'];
var siteMessages;

Noty.overrideDefaults({
    layout   : 'topCenter',
    theme    : 'nest',
	timeout: '4000',
	progressBar: true,
    closeWith: ['click', 'button'],
    killer: true
});

function showNotif(details)
{
    new Noty({
	   type: details["type"],
	   text: details["message"],
	}).show();
}

$(document).ready(function(){

    $(".js-file-form").submit(function(e){
        e.preventDefault();
        
        var form = this;
        var formData = new FormData(form);
    
        $.ajax({
        type: "POST",
        url: "/upload",
        data: formData,
        async: false,
        contentType: false,
        processData: false,
        success: function(code){
            showNotif(siteMessages[code]);
        },
        error: function(code){
            showNotif(siteMessages['1006']); //something went wrong
        }
        });
    });

	$('.js-file').change(function()
	{
		var fileName = $('.js-file').val().split("\\")[2];
		var ext = fileName.split(".")[1];
		
		if(!$.inArray(ext, mimeTypes)) // de ce merge asa? ^_^'
		{
			$('.js-file-label').html(fileName);		
		}
		else
		{
			showNotif(siteMessages['1004']); //file extension not allowed
			$('.js-file').val("");
			$('.js-file-label').html("Choose file");
		}
	});
	
	$.getJSON('static/data/sitemessages.json')
	.done(function(data){
    	siteMessages = JSON.parse(JSON.stringify(data));
	});
	
});