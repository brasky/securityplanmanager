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

$(function() {
    $(".nav-search-focus").blur(function(){
     setTimeout(function(){
        var $focused = document.activeElement.id;
        if($focused == "nav-search" || $focused == "nav-search-results"){
            jQuery.noop
        }else {
            $('#nav-search-results').empty();
        }
        },100);
    });
   });

//    $(function(){
//     $('#nav-search').keyup(function() {
//     	if($('#nav-search').val()) {

//         $.ajax({
//             type: "POST",
//             url: "/nav-search/",
//             data: { 
//                 'search_text' : $('#nav-search').val(),
//                 'csrfmiddlewaretoken' : $("input[name=csrfmiddlewaretoken]").val()
//             },
//             success: searchSuccess,
//             dataType: 'html'
//         });
//     } else { $('#nav-search-results').empty();  } 
//     });
// });

function searchSuccess(data, textStatus, jqXHR)
{
    $('#nav-search-results').html(data);

}




