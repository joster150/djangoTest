$(document).ready(function(){
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$(".markdown-preview").html(marked($('#id_content').text()));

var content;
$('#id_content').on('change keyup paste', function() {
content=$(this).val();
$(".markdown-preview").html(marked(content));
MathJax.typeset()
});

// $(document).on('click',"#imageForm",function(){
//     $.ajax({
//       url: '/add_image',
//       method: 'POST',
//       data:new FormData(imageForm) ,
//       processData: false,
//       contentType: false,
//       success: function(response){
//           if(response.success){
//             var extra_image=response.item;
//             $(extra_image).insertAfter("li:last");
//           }
//
//           }
//     });
//   });

  });
