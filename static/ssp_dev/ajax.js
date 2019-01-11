$(function(){
	setFocusToTextBox();
    $('#search').keyup(function() {
    	if($('#search').val()) {

        $.ajax({
            type: "POST",
            url: "/search/",
            data: { 
                'search_text' : $('#search').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });
    } else { $('#search-results').empty();  } 
    });


    $(".list-group-item").on('click', function(){
      $("#guidance-0").removeClass("hidden");
    });


});

function addClickHandlers(){

    $(".list-group-item").on('click', function(){
      	if($(this).hasClass("unhidden")){
			$(this).find("div").addClass("hidden");
			$(this).removeClass("unhidden");		
		}		
		 else {
			$(this).find("div").removeClass("hidden");
    		$(this).addClass("unhidden");
			}

});}

$.fn.hasAttr = function(name) {
	return this.attr(name) !== undefined;
}

function searchSuccess(data, textStatus, jqXHR)
{
    $('#search-results').html(data);
	addClickHandlers()
}

function setFocusToTextBox(){
    document.getElementById("search").focus();
}


