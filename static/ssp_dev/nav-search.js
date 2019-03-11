$(function(){
    $('#nav-search').keyup(function() {
    	if($('#nav-search').val()) {

        $.ajax({
            type: "POST",
            url: "/nav-search/",
            data: { 
                'search_text' : $('#nav-search').val(),
                'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
            },
            success: searchSuccess,
            dataType: 'html'
        });
    } else { $('#nav-search-results').empty();  } 
    });
});

$("#nav-search-results").focusout(function(){
    $('#nav-search-results').html();
    
});

function searchSuccess(data, textStatus, jqXHR)
{
    $('#nav-search-results').html(data);

}




