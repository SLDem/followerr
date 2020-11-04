$(document).ready(function(){
    // change the selector to use a class
    $(".reply-button").click(function(){
        // this will query for the clicked toggle
        var $toggle = $(this);

        // build the target form id
        var id = "#replycomment-" + $toggle.data('id');

        $( id ).toggle();
        $( button_id ).toggle();
    });
    $(".image-reply-button").click(function(){
        // this will query for the clicked toggle
        var $toggle = $(this);

        // build the target form id
        var id = "#image-replycomment-" + $toggle.data('id');

        $( id ).toggle();
        $( button_id ).toggle();
    });
});