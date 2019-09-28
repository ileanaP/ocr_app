var mimeTypes = ['jpg', 'bmp', 'png', 'tif'];
var siteMessages;
var filename;
var processedFilename;
var uploadsFolder = "/static/img/uploads/";
var defaultTimeout = 0;
var segmentationShow = {};
var modalShown = 0;

var ppC = ['preprocessing', 'segmentation', 'recognition'] // preprocess checkboxes
var sgC = ['lines', 'words', 'regions', 'boundaries', 'frame', 'showall'] // segmentation checkboxes

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

    $('.js-upload').show();
    $('.js-postupload').hide();
    $('.js-scan').hide();
    
    $('.js-postupload .js-checkbox-main').click(function(e){
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
        
        promiseUploadFileCall(formData).then(data => {
                filename = data;
                showNotif('1003');
                $(".postupload .js-image").attr("src", uploadsFolder + filename);
                
                setTimeout(() => {                   
                    $('.js-upload').hide();
                    $('.js-postupload').show();
                }, defaultTimeout);
                
            }).catch(error => { 
                if(isNaN(error))
                    showNotif('1006');
                else
                    showNotif(error);
            });     
    });

	$('.js-file').change(function()
	{
		var fileName = $('.js-file').val().split("\\")[2];
		var ext = fileName.split(".")[1];
		
		// TO DO - sa accepte si extensii cu upper case
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
        
        data = 'operation=delete&filename=' + filename;
        
        promiseDeleteFileCall(data).then(data => {
                showNotif(data);
                setTimeout(() => {
                    filename = '';
                    
                    $('.js-file').val("");
        			$('.js-file-label').html("Choose file");
                    $('.js-upload').show();
                    $('.js-postupload').hide();
                    $(".js-postupload .js-image").attr("src", "");
                    
                    segmentationShow = {};
                    
                }, defaultTimeout);
            }).catch(error => {
                showNotif(error);
            });
        
        });
        
    $('.js-toggle-original').on('click', function(e){ // TO DO - sa ascund butonul cand se incarca o noua imagine
        if($(this).text() == "See Original")
        {
            $(".postupload .js-image").attr("src", uploadsFolder + filename);
            $(this).text("See Preprocessed");
        }
        else
        {
            $(".postupload .js-image").attr("src", uploadsFolder + processedFilename);    
            $(this).text("See Original");  
        }
    });

    $('.js-postupload .js-apply').on('click', function(e){        
        var operations = getCheckboxesValues(ppC) // ppC - preprocess checkboxes
        
        if(operations.segmentation && !modalShown)
        {
            modalShown = 1;
            $('.js-modal-segmentation').modal("show");
            return;
        }
        
        promiseApplyToImageCall(operations.preprocessing,  getCallArgs(filename, "preprocessing")).then(data => {
            
            //TO DO - image preprocessing happened, manipulate the DOM
            console.log('image preprocess - ' + data);
            processedFilename = data;
            $(".postupload .js-image").attr("src", uploadsFolder + data);
            $('.js-toggle-original').show();

            return promiseApplyToImageCall(operations.segmentation, getCallArgs(filename, "segmentation"));
        })
        .then(data => {

            //TO DO - image segmentation happened, manipulate the DOM
            console.log('image segment - ' + data);

            return promiseApplyToImageCall(operations.recognition, callArgs + "recognition");
        })
        .then(data => {
           
            //TO DO - text recognition happened, manipulate the DOM
            console.log('image text rec - ' + data);

        })
        .catch(data => {
            if(data != 'stop')
                showNotif(data);
        });
    });
    
    
    // TO DO - la inchiderea modalului, sa apara tags cu optiunile selectate <3
    $('body').on('click', '.js-checkbox-segmentation-modal', function(){
        segmentationShow = getCheckboxesValues(sgC); // sgC - segmentation checkboxes
        
        // Show All Checkbox Functionality
        if($(this).attr("class").includes("showall"))
        {
            if(segmentationShow.showall)
            {
                for(i = 0; i < sgC.length; i++)
                    $('.js-checkbox-' + sgC[i]).prop("checked", true);
            }
            else
            {
                for(i = 0; i < sgC.length; i++)
                    $('.js-checkbox-' + sgC[i]).prop("checked", false);
            }
        }
        else
        {
            ok = 1;
            for(const prop of Object.keys(segmentationShow))
            {
                if(!segmentationShow[prop] && !(prop == "showall"))
                    ok = 0;
            }
            if(!ok)
                $('.js-checkbox-showall').prop("checked", false);
            else
                $('.js-checkbox-showall').prop("checked", true);
        }
        
        console.log(segmentationShow);
        
        if(segmentationShow.lines && segmentationShow.words &&  
                !(segmentationShow.regions || segmentationShow.boundaries || segmentationShow.frame || segmentationShow.showall))
            $('.js-modal-segmentation .js-save').prop("disabled", true);
        else
            $('.js-modal-segmentation .js-save').prop("disabled", false);
    });
    
    $('body').on('click', '.js-modal-segmentation .js-close', function(){
        
        for(c in sgC)
            segmentationShow[c] = false;
        segmentationShow["lines"] = true;
        segmentationShow["regions"] = true;
    });

    $('body').on('click', '.js-modal-segmentation .js-save', function(){
        $('.js-modal-segmentation').modal('hide');
        
        // TO DO - add "stack overflow" tags with selected items
    });
	
});

function promiseApplyToImageCall(willCall, data)
{
    const promise = new Promise(function(resolve, reject) {
    
        if(willCall)
        {
            let success = (data) => { // TO DO - reject daca nu se intoarce expected result 
                resolve(data);
            }
    
            let error = (data) => {
                reject(data);
            }
    
            callAjax("GET", "/image", data, success, error);
        }
        else
        {
            reject('stop');
        }
    });

    return promise;
}

function promiseDeleteFileCall(data)
{
    const promise = new Promise(function (resolve, reject) {
        let success = (data) => {
            if (data == 1007)
                resolve(data);
            else
                reject(data);
        }

        let error = (data) => {
            reject(data);
        }

        callAjax("GET", "/upload", data, success, error);
    });
    return promise;
}

function promiseUploadFileCall(data)
{
    const promise = new Promise(function (resolve, reject) {
        let success = (data) => {
            if (isNaN(data)) //file was uploaded successfully, filename was returned
                resolve(data);
            else
                reject(data); //file was not uploaded, a code corresponding to the reason was returned
        }

        let error = (data) => {
            reject(data);
        }

        callAjax("POST", "/upload", data, success, error);
    });
    return promise;
}

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

function getCheckboxesValues(cArr)
{
    var ops = {};
    
    for(i = 0; i < cArr.length; i++) 
        ops[cArr[i]] = $('.js-checkbox-' + cArr[i]).prop("checked")
        
    return ops;
}

function getCallArgs(file, operation)
{
    callArgs = "filename=" + file + "&operation=" + operation;

    switch(operation)
    {
        case "segmentation": ops = getCheckboxesValues(sgC);
                             for(const prop of Object.keys(segmentationShow))
                             {
                                 callArgs += "&" + prop + "=" + (ops["prop"] ? 1 : 0)
                             }
                             break;
        default: break;
    }
    
    return callArgs;
}