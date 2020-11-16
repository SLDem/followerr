$(document).ready(function(){
    $(".reply-button").click(function(){
        var $toggle = $(this);
        var id = "#replycomment-" + $toggle.data('id');
        $( id ).toggle();
        $( button_id ).toggle();
    });
    $(".image-reply-button").click(function(){
        var $toggle = $(this);
        var id = "#image-replycomment-" + $toggle.data('id');
        $( id ).toggle();
        $( button_id ).toggle();
    });
});