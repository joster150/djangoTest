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
$(document).on('click',".add-data-row",function(){
  var row = $('.ajax-row-input').map(function(){
           return $.trim($(this).val());
        }).get();
    $.ajax({
      url: '',
      type: 'post',
      data:{
        ajax_type:"add_row",
        "row_data[]":row
      },
      success: function(response){
        if(response.status == 'success'){
          $('.ajax-row-input').val("");
          var new_html='<tr>'
          for(c in response.columns){
              new_html=new_html+'<td>'+response.row[c]+'</td>';
          }
          new_html=new_html+'</tr>'
          $('.table_html').html($('.table_html').html()+new_html);
          alert('Saved')
         }
         else{
           alert('Not Saved')
         }
          }
    });
  });
$(document).on('click',".adjax-data-tpye",function(){
  console.log("fefefef")
  if(this.val()!=0){
    this.prop('readonly', true);
  }
  else{
    this.prop('readonly', false);
  }
});
});
