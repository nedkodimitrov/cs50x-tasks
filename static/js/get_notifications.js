// Populate the notifications drop-down menu
$(function() {
    $('#notification-toggle').on('click', function() {       
        $.ajax({
            url: '/get_notifications',
            success: function(notifications) {
                const notificationList = $('#notification-container');
                notificationList.empty(); // Clear previous notifications
                
                // Populate the notification list with fetched notifications
                notifications.forEach(notification => {
                    const link = $('<a>')
                        .addClass('dropdown-item')
                        .attr('href', `/show_task?id=${notification.task_id}`)
                        .html(`<div class="notification">
                                    ${notification.timestamp}
                                    <h6>${notification.text}</h6>
                                </div>`
                        );

                    notificationList.append(link);
                });
            }
        });
    });
});
