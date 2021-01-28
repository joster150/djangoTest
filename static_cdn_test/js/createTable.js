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
$(document).on('click',".addCard",function(){
    $.ajax({
      url: '',
      type: 'post',
      data:{
        ajax_type:"add_field"
      },
      success: function(response){
            var tablecontainer='<div class="col-12 col-sm-6 col-md-4 col-lg-3 col-xlg-2 table_field"><div class="my-2 card px-3 mx-auto" style="width: 18rem;"><div class="card-body"><h5 class="card-title  mb-0 text-success">Create Field '+
            response.field_num+'</h5><div class="form-group table-field-container-'+response.field_num+'">'+response.field_form+'</div></div></div></div></div>';
            $(tablecontainer).insertAfter("div.table_field:last");
          }
    });
  });
  $(document).on('click',".submit_ajax_fields",function(){
    var names = $('.ajax-name').map(function(){
             return $.trim($(this).val());
          }).get();
    var data_types = $('.ajax-data_type').map(function(){
             return $.trim($(this).val());
          }).get();
    var max_lengths = $('.ajax-max_length').map(function(){
             return $.trim($(this).val());
          }).get();
    var requireds = $('.ajax-required').map(function(){
             return $.trim($(this).prop("checked"));
          }).get();
      $.ajax({
        url: '',
        type: 'post',
        data:{
          ajax_type:"post_table",
          ajax_name:$('.table-form-container-name').val(),
          ajax_group:$('.table-form-group').val(),
          'names[]':names,
          'data_types[]':data_types,
          'max_lengths[]':max_lengths,
          'requireds[]':requireds
        },
        success: function(response){
          var i;
          for (i = 0; i < response.field_nums.length; i++) {
              console.log(i)
              $('.table-field-container-'+response.field_nums[i]).html(response.forms[i])
          }
          $('.table-form-container').html(response.table_form+'<button type="button" class="submit_ajax_fields btn btn-primary">Submit</button><button type="button" class="addCard btn btn-primary">Add Field</button>')
          if(response.status == 'success'){
            alert('Saved')
           }
            }
      });
    });
    $(document).on('change',".ajax-data_type",function(){
      console.log("fefefef");
      if($(this).val()!=0){
        $(this).parentsUntil('.card-body').find('.ajax-max_length').prop('style', "display:none");
        $(this).parentsUntil('.card-body').find('.ajax-max_length').siblings().prop('style', "display:none");
      }
      else{
        $(this).parentsUntil('.card-body').find('.ajax-max_length').prop('style', "");
        $(this).parentsUntil('.card-body').find('.ajax-max_length').siblings().prop('style', "");
      }
    });
  });
