$(document).ready(function() {

    $('#user-reports').click(function(e) {
        e.preventDefault();

        $.get('/admin/reports/user_activity', function(data) {
            console.log(data);
        });
    });

    $('#login-reports').click(function(e) {
        e.preventDefault();

        $.get('/admin/reports/logins', function(data) {
            console.log(data);
        });
    });
});