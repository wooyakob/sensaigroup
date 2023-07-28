$(document).ready(function(){
  $('#show-objections').click(function(){
    $('#objections-section').show();
    $('#product-objections-section').hide();
    $('#product-questions-section').hide();
  });

  $('#show-product-objections').click(function(){
    $('#objections-section').hide();
    $('#product-objections-section').show();
    $('#product-questions-section').hide();
  });

  $('#show-product-questions').click(function(){
    $('#objections-section').hide();
    $('#product-objections-section').hide();
    $('#product-questions-section').show();
  });
});