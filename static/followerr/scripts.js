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

//notifications
const notificationOpenButton = document.getElementById('nav-notifications')
const notificationsModal = document.getElementById('notifications')

notificationOpenButton.addEventListener('click', function () {
    if (notificationsModal.style.display == 'block') {
        notificationsModal.style.display = 'none';
    } else {
        notificationsModal.style.display = 'block';
    }
})

//getting cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');
console.log(csrftoken)