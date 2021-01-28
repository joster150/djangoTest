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
// $(document).on('click',".submit_ajax_steps",function(){
//   var inputs = $('form').map(function(){
//   return this.className
//   }).get();
//   var inputs_3={};
//   var inputs_2;
//   for (const form in inputs){
//     inputs_2 = $('.'+inputs[form]).find('input').map(function(){
//     return $(this).val()
//     }).get();
//     inputs_3[form]=inputs_2;
//   }
//   console.log(inputs_3)
//     $.ajax({
//       url: '',
//       type: 'post',
//       data:{
//         ajax_type:"perform_pipe",
//         'inputs':JSON.stringify(inputs_3, null, 2),
//       },
//       success: function(response){
//         if(response.status == 'success'){
//           alert('Saved')
//          }
//           }
//     });
//   });
$(document).on('change',".table_select",function(){
  $.ajax({
    url: '',
    type: 'post',
    data:{
      ajax_type:"table_select",
      ajax_table:$('.table_select option:selected').text()
    },
    success: function(response){
      $('#myTable thead tr').html(response.table_head)
        $('#myTable tbody').html(response.table_body)
        $('.search_column').parent().html(response.search_cols)
        }
  });
});
$(document).on('change',".table_group",function(){
        $.ajax({
          url: '',
          type: 'post',
          data:{
            ajax_type:"table_group_choice",
            ajax_table_group:$('.table_group option:selected').text()
          },
          success: function(response){
            $('.table_select').parent().parent().html(response.tables_in_group);
            $('.search_column').parent().parent().html(response.search_cols);
            $('#myTable thead tr').html(response.table_head);
            $('#myTable tbody').html(response.table_body)
              }
        });
      });

$(document).on('click',"#add_to_output",function(){
var to_add = $("#table_field_to_add").text();
if(to_add!=""){
  var option_num;
  for(select in $(".table_param")){
    if(typeof($(".table_param")[select].options) != 'undefined'){
      var opt = document.createElement('option');
      var table_name=$('.table_select option:selected').text()
      opt.value=$(".table_param")[select].options.length + '--'+table_name+'//'+to_add;
      opt.text=table_name+'//'+to_add;
      $(".table_param")[select].appendChild(opt);
    };
  };
}
});
$(document).on('click',"td",function(){
var field_value= $(this).text();
$("#table_field_to_add").text(field_value)
});
$(document).on('click',".toggle",function(){
$(this).siblings().toggle()
});
});
function mySearchFunction() {
  var input, filter, table, tr, td, i, txtValue, column_number;
  column_number=$('.search_column').val()
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[column_number];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
};
