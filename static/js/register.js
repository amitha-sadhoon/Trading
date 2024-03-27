$(document).ready(function(){
    $('#registration').children('.btn').on('click', register); // Pass the function reference, don't call it immediately
});

function register() {
    var form = document.getElementById("registration");
    var username = form.username.value;
    var password = form.password.value;
    var password_confirm = form.confirmation.value;
    var keyword = form.keyword.value;
    var email = form.email.value; // Get the email field

    // Regular expression for a valid email
    var emailRegEx = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$/;

    // Password regular expression
    var passwordRegEx = /^(?=.*\d)(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

    if (!username) {
        alert("Missing username!");
        return false;
    }
    else if (!email) {
        alert("Missing email!");
        return false;
    }
    else if (!emailRegEx.test(email)) { // Check if email is valid using the regular expression
        alert("Invalid email address!");
        return false;
    }
    else if (!password) {
        alert("Missing password!");
        return false;
    }
    else if (!passwordRegEx.test(password)) { // Check if password is valid using the regular expression
        alert("Password must be at least 8 characters long, and have at least one lowercase, uppercase, and special character!");
        return false;
    }
    else if (password !== password_confirm) {
        alert("Passwords don't match!");
        return false;
    }
    else if (!keyword) {
        alert("Missing keyword!");
        return false;
    }
    return true;
}
