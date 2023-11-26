// Get autocomplete suggestions for assignee input field
$(function() {
    $('#assignee').on('input', function() {
        let inputValue = $(this).val().trim();
        
        if (inputValue) {
            $.ajax({
                url: '/get_users',
                data: { name: inputValue },
                dataType: 'json',
                success: function(userNames) {
                    $('#assignee').autocomplete({
                        source: userNames
                    });
                }
            });
        }
    });
});