$(document).ready(function(){
  var content,marked_content
  $(".markdown-content").each(function(){
  content=$(this).text();
  console.log(content)
  marked_content=marked(content);
  $(this).html(marked_content);
});
});
