// Get autocomplete suggestions for assigner input field
$(function() {
    $('#assigner').on('input', function() {
        let inputValue = $(this).val().trim();
        
        if (inputValue) {
            $.ajax({
                url: '/get_users',
                data: { name: inputValue },
                dataType: 'json',
                success: function(userNames) {
                    $('#assigner').autocomplete({
                        source: userNames
                    });
                }
            });
        }
    });
});