// Helper function to display status / error messages
const addMessage = (message) => {
    const messagesDiv = document.querySelector("#messages");
    messagesDiv.style.display = "block";
    messagesDiv.innerHTML = "";
    messagesDiv.innerHTML += "> " + message + "<br />";
    console.log("Debug: ", message);
};

let returnURL = "http://localhost:8080/success"; // payment service local url
let redirectURL = "https://ifreelance.site/api/v1/stripe/redirect";

// Only run code when DOM is fully loaded
document.addEventListener("DOMContentLoaded", async() => {
    
    // initialize Stripe
    const {publishableKey} = await fetch("https://ifreelance.site/api/v1/stripe/config").then(res => res.json());
    const stripe = Stripe(publishableKey);

    // create card input box
    var elements = stripe.elements();
    var cardElement = elements.create("card");
    cardElement.mount("#card-element");

    // when form is submitted, create PaymentIntent on server then confirm on frontend
    const form = document.querySelector("#payment-form");

    form.addEventListener("submit", async(e) => {

        const nameInput = document.querySelector("#name");
        const emailInput = document.querySelector("#email");
        const amountInput = document.querySelector("#amount");
        const orderID = document.querySelector("#order");

        addMessage("Sending details to server");

        e.preventDefault(); // prevents browser from reloading

        // make Ajax call to server to create PaymentIntent
        // use browser's native fetch API to avoid dependencies
        const {error: backendError, clientSecret} = await fetch("https://ifreelance.site/api/v1/stripe/create-payment-intent", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: parseInt(amountInput.value),
                email: emailInput.value,
                order: orderID.value
            }),
        })
        .then((result) => result.json());

        if (backendError) {
            addMessage(backendError.message);
            return;
        }

        addMessage("PaymentIntent created");

        // After obtaining clientSecret for PaymentIntent, can confirm it
        // const {error: stripeError, paymentIntent} = await stripe.confirmCardPayment(
        //     clientSecret, {
        //         // option block
        //         payment_method: {
        //             card: cardElement,
        //             billing_details: {
        //                 // amount?
        //                 name: nameInput.value,
        //                 email: emailInput.value
        //             },
        //         }
        //     }
        // )
        // .then((res) => {
        //     fetch(returnURL, {
        //         method: 'POST',
        //         headers: {
        //             'Content-Type': 'application/json',
        //             'mode': 'no-cors'
        //         },
        //         body: JSON.stringify(res.paymentIntent)
        //     })
        // });

        const {error: stripeError, paymentIntent} = await stripe.confirmCardPayment(
            clientSecret, {
                // option block
                payment_method: {
                    card: cardElement,
                    billing_details: {
                        // amount?
                        name: nameInput.value,
                        email: emailInput.value
                    },
                }
            }
        )

        if (stripeError) {
            addMessage(stripeError.message);
            return;
        }

        // If PaymentIntent couldn't confirm due to eg. secure customer auth
        // Open modal / redirect
        addMessage(`PaymentIntent (${paymentIntent.id}): ${paymentIntent.status}`);

        // let redirectURL = window.location.protocol + "//" + window.location.host + "/redirect";
        location.href=redirectURL;
    });

   
});