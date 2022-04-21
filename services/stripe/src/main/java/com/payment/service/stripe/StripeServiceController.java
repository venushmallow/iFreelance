package com.payment.service.stripe;

import java.util.HashMap;
import java.util.Map;

import com.google.gson.Gson;
import com.stripe.Stripe;
import com.stripe.exception.StripeException;
import com.stripe.model.PaymentIntent;
import com.stripe.param.PaymentIntentCreateParams;

import org.json.simple.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@RestController
public class StripeServiceController {

    private static Gson gson = new Gson();

    private ViewController view;

    @Autowired
    public StripeServiceController(ViewController view) {
        this.view = view;
    }

    @Value("${payment_service_url}")
    private String paymentServiceURL;

    @Value("${payment_service_url_internal}")
    private String paymentServiceURLInternal;

    @Value("${STRIPE_PUBLISHABLE_KEY}")
    private String stripePK;

    @Value("${STRIPE_SECRET_KEY}")
    private String stripeSK;

    @Value("${spring.profiles.active:Unknown}")
    private String activeProfile;

    @GetMapping("/get-active-profile")
    public String getActiveProfile() {
        return activeProfile;
    }

    @PostMapping(
        value = "/create-payment-intent",
        produces = "application/json"
    )
    public String createPaymentIntent(@RequestBody String paymentRequest) {

        Stripe.apiKey = stripeSK;

        try {
            // create PaymentIntent to make API request to Stripe
            CreatePaymentIntentRequest data = gson.fromJson(
                paymentRequest,
                CreatePaymentIntentRequest.class
            );

            // API call to create payment intent
            PaymentIntentCreateParams params = PaymentIntentCreateParams
            .builder()
            .setAmount(data.getAmount())
            .setCurrency("sgd")
            .setReceiptEmail(data.getEmail())
            .setDescription(data.getOrder())
            .build();

            PaymentIntent paymentIntent = PaymentIntent.create(params);

            // return JSON with only client secret
            Map<String, Object> responseData = new HashMap<>();
            responseData.put("clientSecret", paymentIntent.getClientSecret());

            return gson.toJson(responseData);

        } catch (StripeException e) {

            // more client-friendly way of displaying errors

            Map<String, Object> errorData = new HashMap<>();
            errorData.put("message", e.getUserMessage());

            Map<String, Object> responseData = new HashMap<>();
            responseData.put("error", errorData);
            responseData.put("status", 400);

            return gson.toJson(responseData);

        } catch (Exception e) {
            Map<String, Object> errorData = new HashMap<>();
            errorData.put("message", e.toString());

            Map<String, Object> responseData = new HashMap<>();
            responseData.put("error", errorData);
            responseData.put("status", 500);

            return gson.toJson(responseData);
        }
    }

    @PostMapping("/")
    public void getPaymentDetails(@RequestBody JSONObject paymentDetails) {
        String logMsg = String.format(
            "Payment details received: %s",
            paymentDetails.toString()
        );
        System.out.println(logMsg);
        this.view.setData(paymentDetails);
    }

    @GetMapping("/check-payment")
    public String checkPaymentConn() {
        RestTemplate restTemplate = new RestTemplate();
        HttpEntity<String> request = new HttpEntity<>(null);
        ResponseEntity<String> response = null;

        // Set url to internal / external (dev / prod)
        String paymentService = null;
        if (activeProfile.equals("dev")) {
            paymentService = paymentServiceURLInternal;
        } else {
            paymentService = paymentServiceURL;
        }

        String url = paymentService + "/health";

        try {
            response = restTemplate.exchange(
                url, HttpMethod.GET, request, String.class
            );
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        if (response != null) {
            return response.getBody();
        }

        return null;
    }

    @GetMapping("/config")
    public String getKeys() {
        Map<String, Object> responseData = new HashMap<>();
        responseData.put("publishableKey", stripePK);
        return gson.toJson(responseData);
    }

    @GetMapping("/health")
    public String healthCheck() {
        return "{'message': 'Stripe service is healthy.'}";
    }
}
