$(document).ready(function(){
  $(".modulename").click(function(){
    $.ajax({
      url: '',
      type: 'get',
      data:{
        module_name:$(this).attr('id')
      },
      success: function(response){
        $(".modinfo").text(response.info)
      }
    });
  });

});
