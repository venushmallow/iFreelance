var form = document.getElementById("payment-form");
var stripe_service_url = "http://stripe:4242/";
form.addEventListener('submit', (e) => {
    e.preventDefault();

    var comments = document.getElementById("comments");

    var paymentDetails = {
        "username": username,
        "email": email,
        "amount": amount,
        "comments": comments.value
    }

    console.log(paymentDetails);
});

