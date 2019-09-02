var mimeTypes = ['jpg', 'bmp', 'png', 'tif'];

Noty.overrideDefaults({
    layout   : 'topCenter',
    theme    : 'nest',
	timeout: '4000',
	progressBar: true,
    closeWith: ['click', 'button'],
    killer: true
});

$(document).ready(function(){
	$('.js-file').change(function()
	{
		var fileName = $('.js-file').val().split("\\")[2];
		var ext = fileName.split(".")[1];
		
		console.log('ext: ' + ext);
		if(!$.inArray(ext, mimeTypes)) // de ce merge asa? ^_^'
		{
			$('.js-file-label').html(fileName);		
		}
		else
		{
			new Noty({
			   type: 'error',
			   text: 'This file type is not supported.',
			}).show();
			$('.js-file').val("");
			$('.js-file-label').html("Choose file");
		}
	});
});