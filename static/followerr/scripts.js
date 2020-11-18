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

// sidebar icons
const currentLocation = location.href;
const menuItems = document.querySelectorAll('.sidebar-ul a');
const menuLength = menuItems.length;
const menuArrows = document.querySelectorAll('.arrow')

for (let i=0; i< menuLength; i++) {
    if (menuItems[i].href === currentLocation){
        menuItems.forEach(menuItem => menuItem.classList.remove('active'))
        menuItems[i].className = 'active'
    }
};