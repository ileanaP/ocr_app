var mimeTypes = ['jpg', 'bmp', 'png', 'tif'];
var siteMessages;
var filename;

Noty.overrideDefaults({
    layout   : 'topCenter',
    theme    : 'nest',
	timeout: '4000',
	progressBar: true,
    closeWith: ['click', 'button'],
    killer: true
});

$(document).ready(function(){

	$.getJSON('static/data/sitemessages.json')
	.done(function(data){
    	siteMessages = JSON.parse(JSON.stringify(data));
	});

    $('.js-upload-template').show();
    $('.js-postupload-template').hide();
    $('.js-scan-template').hide();
    
    $('.postupload input[type="checkbox"]').click(function(e){
        if($(this).prop("checked"))
        {
            $(this).parent().parent().prevAll().each(function(e){
                $(this).children().children().first().prop('checked', true);
            });
        }
        else
        {
            $(this).parent().parent().nextAll().each(function(e){
                $(this).children().children().first().prop('checked', false);
            });
        }
    });

    $(".js-file-form").submit(function(e){
        e.preventDefault();
        
        var form = this;
        var formData = new FormData(form);
    
        const promiseUploadFile = new Promise(function(resolve, reject){
            
            let success = (data) => {
                if(isNaN(data))  //file was uploaded successfully, filename was returned
                {
                    resolve(data);
                }
                else
                {
                    reject(data) //file was not uploaded, a code corresponding to the reason was returned
                }
            }
            
            let error = (data) => {
                reject(data);
            }
            
            callAjax("POST", "/upload", formData, success, error);
        });
        
        const execPromiseUploadFile = () => 
        {
            promiseUploadFile.then(data => {
                filename = data;
                showNotif('1003');
                $(".postupload .js-image").attr("src", "/static/img/uploads/" + filename);
                
                setTimeout(() => {                   
                    $('.js-upload-template').hide();
                    $('.js-postupload-template').show();
                }, 2000);
                
            }).catch(error => { 
                if(isNaN(error))
                    showNotif('1006');
                else
                    showNotif(error);
            });
        }
        
        execPromiseUploadFile();        
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
			showNotif('1004'); //file extension not allowed
			$('.js-file').val("");
			$('.js-file-label').html("Choose file");
		}
	});
	
	$('.js-return-to-upload').on('click',function(){
    	
    	if(filename == '')
        {
        	showNotif('1006');
        	return;
        }
        
        const promiseDeleteFile = new Promise(function(resolve, reject){
            data = 'operation=delete&filename=' + filename;
           
            let success = (data) => {
                if(data == 1007)
                {
                    console.log('ajax success with resolve; data: ' + data);
                    resolve(data);
                }
                else
                {
                    console.log('ajax success with reject; data: ' + data);
                    consolelog(data);
                    reject(data);
                }    
            }
            
            let error = (data) => {
                console.log('ajax error; data: ' + data);
                reject(data);
            }
            
            callAjax("GET", "/upload", data, success, error);
        });
        
        const execPromiseDeleteFile = () => {
            promiseDeleteFile.then(data => {
                showNotif(data);
                setTimeout(() => {
                    filename = '';
                    
                    $('.js-file').val("");
        			$('.js-file-label').html("Choose file");
                    $('.js-upload-template').show();
                    $('.js-postupload-template').hide();
                    $(".js-postupload-template .js-image").attr("src", "");
                    
                }, 3000);
            }).catch(error => {
                showNotif(error);
            });
        }
        
        execPromiseDeleteFile();
    	
	});
	
});

function showNotif(code)
{

    details = siteMessages[code];

    if(details === undefined || details["type"] === undefined || details["message"] === undefined)
        details = siteMessages['1006'];
    
    new Noty({
	   type: details["type"],
	   text: details["message"],
	}).show();
}

function callAjax(type, url, data, success = '', error = '')
{
    if(success == '')
        success = (msg) => {console.log(msg)}
    if(error == '')
        error = (msg) => {console.log(msg)}

    $.ajax({
        type: type,
        url: url,
        data: data,
        async: true,
        contentType: false,
        processData: false,
        success: success,
        error: error
        }); 
}