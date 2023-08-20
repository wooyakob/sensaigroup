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

    $.get('/api/objections_data', function(data) {
        let ctx = document.getElementById('objectionsChart').getContext('2d');
        let myChart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Sales Team Objections Data'
                    }
                }
            }
        });
    });
});


$(document).ready(function() {
    $.get('/api/total_users', function(data) {
        $("#totalUsers").text( data.total + '/25');
    });
});





