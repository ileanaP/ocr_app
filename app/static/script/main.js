var mimeTypes = ['jpg', 'bmp', 'png', 'tif'];
var siteMessages;
var filename;
var processedFilename;
var segmentedFilenames;
var uploadsFolder = "/static/img/uploads/";
var resultsFolder = "/static/results/"
var defaultTimeout = 0;
var cHeight, cWidth;
var v;
var x1, y1, x2, y2, symbol, strokeStyles;

var ppC = ['preprocessing', 'segmentation', 'recognition'] // preprocess checkboxes
var sgC = ['lines', 'words', 'regions', 'boundaries', 'frame', 'cropped', 'showall'] // segmentation checkboxes
var cNames = ["img", "lines", "words", "regions", "boundaries", "frame"]; // canvas names

Noty.overrideDefaults({
    layout   : 'topCenter',
    theme    : 'nest',
	timeout: '4000',
	progressBar: true,
    closeWith: ['click', 'button'],
    killer: true
});

$(document).ready(function(){
    v = Date.now();

	$.getJSON('static/data/sitemessages.json').done(function(data){ 
    	siteMessages = JSON.parse(JSON.stringify(data));
	});

    $('.js-upload').show();
    $('.js-postupload').hide();
    $('.js-scan').hide();
    
    $("body").on("click", ".js-postupload .js-cb-main", function(e){
        if($(this).prop("checked"))
        {
            $(this).parent().parent().prevAll().each(function(e){
                $(this).children().children().first().prop('checked', true);
                $(this).children().children().first().trigger('change');
            });
        }
        else
        {
            $(this).parent().parent().nextAll().each(function(e){
                $(this).children().children().first().prop('checked', false);
                $(this).children().children().first().trigger('change');
            });
        }
    });
    
    $(".js-image").on("load", function(){
        $(".outsideWrapper").width($(this).width());
        $(".outsideWrapper").height($(this).height());
    });

    $("body").on("submit", ".js-file-form", function(e){
        e.preventDefault();
        
        var form = this;
        var formData = new FormData(form);
        
        promiseUploadFileCall(formData).then(data => {
                filename = data;
                showNotif('1003');
                $(".js-image").attr("src", uploadsFolder + filename);
                
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

	$("body").on("change", ".js-file", function()
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
	
	$("body").on("click", ".js-return-to-upload", function(){
    	
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
                    
                    $(".js-file").val("")
                    $(".js-file-label").text("Choose file");
                    
                    $(".js-postupload .js-image").attr("src", "");
                    $(".js-cb-main").prop("checked", true);
                    $(".js-results-cropped").html("");
                    $(".js-btn-results").css("visibility", "hidden");
                    restoreDefaultSegmentationTags();
                    showSegmentationTags();
                    
                    $(".js-upload").show();
                    $(".js-postupload").hide();
                    
                }, defaultTimeout);
            }).catch(error => {
                showNotif(error);
            });
        
        });
        
    $("body").on("click", ".js-btn-original", function(e){
        $(".js-image").attr("src", uploadsFolder + filename);
    });
    $("body").on("click", ".js-btn-preprocessed", function(e){
        $(".js-image").attr("src", resultsFolder + processedFilename);
    });
    $("body").on("click", ".js-btn-segmented", function(e){
        $(".js-image").attr("src", resultsFolder + segmentedFilenames[0]);
    });
    
    $("body").on("change", ".js-cb-segmentation", function(){
        if($(".js-cb-segmentation").prop("checked"))
            $(".js-badges-list").css("visibility", "visible");
        else
            $(".js-badges-list").css("visibility", "hidden")
    });

    $("body").on('click', '.js-postupload .js-apply', function(e){        
        var operations = getCheckboxesValues(ppC) // ppC - preprocess checkboxes
        
        $(".js-postupload .js-options").css("pointer-events", "none");
        console.log("consoolee");
        
        promiseApplyToImageCall("preprocessing").then(data => {
            
            //TO DO - image preprocessing happened, manipulate the DOM
            $(".js-spinner-preprocessing").hide();
            processedFilename = data;
            $(".js-image").attr("src", resultsFolder + data + "?v=" + v);
            $('.js-btn-original').css("visibility", "visible");
            $('.js-btn-preprocessed').css("visibility", "visible");

            return promiseApplyToImageCall("segmentation");
        })
        .then(data => {

            //TO DO - image segmentation happened, manipulate the DOM
            
            if($(".js-cb-cropped").prop("checked"))
                showCropped();
            
            segmentedFilenames = JSON.parse(data);
                  
            //$(".js-image").attr("src", resultsFolder + segmentedFilenames[0] + "?v=" + v);
            $('.js-btn-segmented').css("visibility", "visible");
            
            $('#postupload').imagesLoaded(function(){
                
                cWidth = parseInt($(".js-image").width());
                cHeight = parseInt($(".js-image").height());
                
                var canvas;
                
                for(var i = 0; i < cNames.length; i++)
                {
                    canvas = newCanvas(cNames[i], cWidth, cHeight);
                    $(".insideWrapper").append(canvas);
                }
                
                /* ******** */                
                /*
                c = document.getElementById("js-canvas-lines");
                ctx = c.getContext("2d");
                
                ctx.strokeStyle = "#FF0000";
                ctx.lineWidth = 1;
                ctx.strokeRect(30, 60, 100, 200);*/
                
                
                /* ******** */
                
                
                $.getJSON('static/results/' + segmentedFilenames[1] + "?v=" + v).done(function(data){
                    var data = JSON.parse(JSON.stringify(data));
                    
                    fillCanvases(data);               
                    displayCanvases();
                });
                
            });
            
            $(".js-spinner-segmentation").hide();
            
            return promiseApplyToImageCall("recognition");
        })
        .then(data => {
           $(".js-spinner-recognition").hide();
            //TO DO - text recognition happened, manipulate the DOM

        })
        .catch(data => {
            if(data != 'stop')
                showNotif(data);
            
            $(".js-spinner-preprocessing").hide();
            $(".js-spinner-segmentation").hide();
            $(".js-spinner-recognition").hide();
        })
        .finally(data => {
            console.log("finalllyyy");
            $(".js-postupload .js-options").css("pointer-events", "auto");
        });
    });

    // sgC - segmentation checkboxes
    $('body').on('click', '.js-cb-segmentation-modal', function(){
        
        // "Show All" Checkbox Functionality
        if($(this).attr("class").includes("showall"))
        {
            if($('.js-cb-showall').prop("checked"))
            {
                for(i = 0; i < sgC.length-2; i++)
                    $('.js-cb-' + sgC[i]).prop("checked", true);
            }
            else
            {
                for(i = 0; i < sgC.length-2; i++)
                    $('.js-cb-' + sgC[i]).prop("checked", false);
            }
        }
        else
        {
            ok = 1;
            for(i = 0; i < sgC.length; i++)
            {
                if(!$('.js-cb-' + sgC[i]).prop("checked") && !(sgC[i] == "showall" || sgC[i] == "cropped"))
                    ok = 0;
            }
            if(!ok)
                $('.js-cb-showall').prop("checked", false);
            else
                $('.js-cb-showall').prop("checked", true);
        }
        
        console.log("before def values");
        if(areDefaultValues())
            console.log("values are default");
        else
            console.log("values are NOT default");
        console.log("AFTER def values");
        
        if(areDefaultValues())
            $('.js-modal-segmentation .js-save').prop("disabled", true);
        else
            $('.js-modal-segmentation .js-save').prop("disabled", false);
    });
    
    $('.js-modal-segmentation .js-close').on('click', function(){
        restoreDefaultSegmentationTags()
    });

    $('.js-modal-segmentation .js-save').on('click', function(){
        $('.js-modal-segmentation').modal('hide');
        // TO DO - add "stack overflow" tags with selected items
    });
    
    $('.js-modal-segmentation').on('hidden.bs.modal', function (e) {
        showSegmentationTags();
        $(".js-badges-list").prop("onclick", null).off("click");
    });
    
    $(".js-badges-list").on("click", function(){
        $('.js-modal-segmentation').modal("show");

        $(".js-badge").on("click", function(){            
            if($(this).hasClass("badge-secondary"))
            {
                $(this).removeClass("badge-secondary").addClass("badge-light");
                $(".js-cb-" + $(this).text()).prop("checked", false);
                
                if($("#js-canvas-" + $(this).text()).length)
                    $("#js-canvas-" + $(this).text()).css("visibility", "hidden");
            }
            else
            {
                $(this).removeClass("badge-light").addClass("badge-secondary");
                $(".js-cb-"+ $(this).text()).prop("checked", true);
                
                if($("#js-canvas-" + $(this).text()).length)
                    $("#js-canvas-" + $(this).text()).css("visibility", "visible");
            }
        });
    });    
	
});

function newCanvas(name, width, height)
{
    var canvas = $("<canvas />")
                    .addClass("defaultCanvas")
                    .attr("id", "js-canvas-" + name)
                    .attr("width", width)
                    .attr("height", height);
                    /*.width(width)
                    .height(height);*/
                    
    return canvas;
}

function fillCanvases(data)
{

    c = document.getElementById("js-canvas-img");
    var img = document.getElementById("js-image");
    ctx = c.getContext("2d");
    ctx.drawImage(img, 0, 0, $(".js-image").width(), $(".js-image").height());
    
    $(".js-image").css("visibility", "hidden");

    var hRatio = cHeight / data["shape"][0];
    var wRatio = cWidth / data["shape"][1];
    
    $.ajax({
        url: 'static/data/strokestyles.json',
        data: "v=" + v,
        dataType: 'json',
        async: false,
        success: function(data){
            strokeStyles = JSON.parse(JSON.stringify(data));
        },
        error: function(err){ console.log(err); }
    });

    for(var j = 1; j < cNames.length; j++)
    {
        fillCanvas(data[cNames[j]], cNames[j], hRatio, wRatio);
    }
}

function fillCanvas(data, name, hRatio, wRatio)
{
    c = document.getElementById("js-canvas-" + name);
    ctx = c.getContext("2d");
    ctx.lineWidth = 1;
    ctx.strokeStyle = strokeStyles[name] + strokeStyles["opacity"];

    for(var i = 0; i < data.length; i++)
    {
        x1 = parseInt(data[i][0]*wRatio);
        y1 = parseInt(data[i][1]*hRatio);
        x2 = parseInt(data[i][2]*wRatio);
        y2 = parseInt(data[i][3]*hRatio);
        
        ctx.strokeRect(x1, y1, x2-x1, y2-y1);
    }
}

function displayCanvases()
{    
    for(var i = 1; i < cNames.length; i++)
    {
        if($(".js-cb-" + cNames[i]).prop("checked"))
        {
            $("#js-canvas-" + cNames[i]).css("visibility", "visible");
        }
        else
        {
            $("#js-canvas-" + cNames[i]).css("visibility", "hidden");
        }
    }
}

function showCropped()
{
    $.getJSON('static/results/cropped_filenames.json?v=' + v).done(function(data){ // I prevent cache-ing by adding the timestamp 
    // TO DO - sa iau static/results din app.config (daca se poate)
            filenames = JSON.parse(JSON.stringify(data));
            
            var img;
            for(var i = 0; i < filenames.length; i++)
            {
                fileInfo = filenames[i].split("_");
                
                img = $("<img />")
                        .attr('src', 'static/results/cropped/'+filenames[i] + "?v=" + v)
                        .attr("title", "Line " + fileInfo[0] + ", Char " + fileInfo[1]);
                $(".js-results-cropped").append(img);
            }
        });
}

function restoreDefaultSegmentationTags()
{
    for(i =0; i< sgC.length; i++)
        $(".js-cb-" + sgC[i]).prop("checked", false);

    $(".js-cb-lines").prop("checked", true);
    $(".js-cb-regions").prop("checked", true);
}

function areDefaultValues()
{
    return $('.js-cb-lines').prop("checked") && $('.js-cb-words').prop("checked") &&  
           !($('.js-cb-regions').prop("checked") || $('.js-cb-boundaries').prop("checked") || 
             $('.js-cb-frame').prop("checked") || $('.js-cb-showall').prop("checked") ||  $('.js-cb-cropped').prop("checked"));
}


function showSegmentationTags()
{
    for(i =0; i< sgC.length - 1; i++)
    {
        if($(".js-cb-"+sgC[i]).prop("checked"))
        {
            $(".js-badge-" + sgC[i]).removeClass("badge-light").addClass("badge-secondary");
        }
        else
        {
            $(".js-badge-" + sgC[i]).removeClass("badge-secondary").addClass("badge-light");
        }
    }
}

function promiseApplyToImageCall(operation)
{
    var data = getCallArgs(filename, operation);
    
    const promise = new Promise(function(resolve, reject) {
    
        if($(".js-cb-"+operation).prop("checked"))
        {
            let success = (data) => { // TO DO - reject daca nu se intoarce expected result 
                resolve(data);
            }
    
            let error = (data) => {
                reject(data);
            }
    
            $(".js-spinner-"+operation).css("display", "inline-block");
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
        ops[cArr[i]] = $('.js-cb-' + cArr[i]).prop("checked")
        
    return ops;
}

function getCallArgs(file, operation)
{

    var kargs;

    switch(operation)
    {
        case "segmentation": ops = getCheckboxesValues(sgC);
                             kargs = JSON.stringify(ops);
                             break;
        default: kargs=0;
    }
    
    callArgs = "filename=" + file + "&operation=" + operation + "&kargs=" + kargs;
    
    return callArgs;
}