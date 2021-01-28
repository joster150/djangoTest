$(document).ready(function(){
  $(".modulename").click(function(){
    $.ajax({
      url: '',
      type: 'get',
      data:{
        ajax_type:"list_funcs",
        module_name:$(this).attr('id')
      },
      success: function(response){
        $(".modinfo").html("<b>Name: </b>"+response.modname+"</br><b>Description: </b>"+response.description);
        var temp_str="";
        for (i=0;i<response.functions.length;i++){
          temp_str+="<li id='"+response.functions[i]+"!"+response.modname+"'>"+response.functions[i]+"</li>"
        }
        $(".funcinfo").html(temp_str);
        $(".funcinfo li").addClass("list-inline-item");
      }
    });
  });

  $(document).on('click','.funcinfo li',function(){
    $(this).siblings().css('font-weight','normal');
    $(this).css("font-weight","Bold");
    $.ajax({
      url: '',
      type: 'get',
      data:{
        ajax_type:"func_info",
        module_name:"func_name:"+ $(this).attr('id')
      },
      success: function(response){
        $(".functionDoc."+response.mod_name).html(response.funcdoc);
      }
    });
  });

});
