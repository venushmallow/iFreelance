package com.payment.service;

import org.json.simple.parser.JSONParser;
import org.json.simple.parser.ParseException;

import java.util.HashMap;
import java.util.Map;

import org.json.simple.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

@CrossOrigin(maxAge = 3600)
@RestController
public class PaymentServiceController {

    @Autowired
    private RequestService requestService;

    @Autowired
    private JSONService jsonService;

    private PaymentDetails paymentDetails;

    public PaymentDetails getDetails() {
        return paymentDetails;
    }

    @Value("${stripe_service_url}")
    private String stripeServiceURL;

    @Value("${stripe_service_url_internal}")
    private String stripeServiceURLInternal;

    @Value("${orders_service_url}")
    private String ordersServiceURL;

    @Value("${orders_service_url_internal}")
    private String ordersServiceURLInternal;

    @Value("${place_order_service_url}")
    private String placeOrdersURL;

    @Value("${place_order_service_url_internal}")
    private String placeOrdersURLInternal;

    @Value("${spring.profiles.active:Unknown}")
    private String activeProfile;

    @RequestMapping("/get-active-profile")
    public String getActiveProfile() {
        return activeProfile;
    }

    // Get user details associated with payment (not inclusive of card)
    @PostMapping("/")
    public JSONObject receivePaymentDetails(@RequestBody String details) {

        JSONParser parser = new JSONParser();
        JSONObject receivedPaymentDetails = new JSONObject();

        try {
            receivedPaymentDetails = (JSONObject) parser.parse(details);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
        }

        RestTemplate restTemplate = new RestTemplate();
        HttpEntity<JSONObject> request = new HttpEntity<>(
            receivedPaymentDetails
        );

        // Set url to internal / external (dev / prod)
        String stripeService = null;
        if (activeProfile.equals("dev")) {
            stripeService = stripeServiceURLInternal;
        } else {
            stripeService = stripeServiceURL;
        }

        try {
            restTemplate.postForEntity(stripeService, request, String.class);
            System.out.println("Request from payment sent to stripe");
        } catch (Exception e) {
            Map<String, String> errorMap = new HashMap<>();
            errorMap.put(
                "message", "An error occurred receiving payment details."
            );
            errorMap.put("error", e.getMessage());
            return new JSONObject(errorMap);
        }

        return receivedPaymentDetails;
    }

    @RequestMapping("/webhook")
    public ResponseEntity<?> webhook(@RequestBody String request) {
        Map<String, Object> map = jsonService.convertStringToMap(request);

        if (map == null) {
            return new ResponseEntity<>(
                "Something went wrong.", HttpStatus.INTERNAL_SERVER_ERROR
            );
        }

        if (map.get("type").equals("payment_intent.succeeded")) {
            System.out.println(map.toString());
            String orderID = jsonService.searchForValue("description", map);
            System.out.println("ORDER TO UPDATE: " + orderID);
            ResponseEntity<?> update = updateOrder(orderID);
            if (update != null) {
                System.out.println(update.getBody().toString());
                System.out.println(update.getStatusCodeValue());
            } else {
                System.out.println("Something went wrong.");
            }

            return update;
        }

        return new ResponseEntity<>(
                "Something went wrong.", HttpStatus.INTERNAL_SERVER_ERROR
        );
    }

    public ResponseEntity<?> placeOrderUpdateStatusPAID(String orderID) {

        Map<String, String> newOrderStatus = new HashMap<>();
        newOrderStatus.put("order_id", orderID);
        newOrderStatus.put("status", "PAID");
        JSONObject requestJson = new JSONObject(newOrderStatus);

        System.out.println("Contacting place-order to update order...");

        // Set url to internal / external (dev / prod)
        String placeOrdersService = null;
        if (activeProfile.equals("dev")) {
            placeOrdersService = placeOrdersURLInternal;
        } else {
            placeOrdersService = placeOrdersURL;
        }

        String placeOrder = placeOrdersService + "/place-order/update-status";
        System.out.println(placeOrder);

        try {
            ResponseEntity<?> response = requestService
            .createAuthHttpPatchRequest(
                requestJson.toJSONString(), placeOrder
            );
            return response;
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        return new ResponseEntity<String>(
            "Something went wrong when updating orders.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
    }

    public ResponseEntity<?> updateOrder(String orderID) {

        Map<String, String> newOrderStatus = new HashMap<>();
        newOrderStatus.put("status", "PAID");
        JSONObject requestJson = new JSONObject(newOrderStatus);

        // Set url to internal / external (dev / prod)
        String ordersService = null;
        if (activeProfile.equals("dev")) {
            ordersService = ordersServiceURLInternal;
        } else {
            ordersService = ordersServiceURL;
        }

        String ordersUpdateURL = ordersService + "/orders/" + orderID;

        System.out.println(ordersUpdateURL);

        System.out.println("Updating order...");

        try {
            ResponseEntity<?> response = requestService
            .createAuthHttpPatchRequest(
                requestJson.toJSONString(), ordersUpdateURL
            );
            return response;
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        return new ResponseEntity<String>(
            "Something went wrong when updating orders.",
            HttpStatus.INTERNAL_SERVER_ERROR
        );
    }

    @RequestMapping("/health")
    public String healthCheck() {
        return "{'message': 'Service is healthy'}";
    }

    @RequestMapping("/check-stripe")
    public String checkStripeConn() {

        // Set url to internal / external (dev / prod)
        String stripeService = null;
        if (activeProfile.equals("dev")) {
            stripeService = stripeServiceURLInternal;
        } else {
            stripeService = stripeServiceURL;
        }

        ResponseEntity<String> response = requestService.createHttpRequest(
            null, stripeService + "/health", HttpMethod.GET
        );
        if (response != null) {
            return response.getBody();
        }
        return null;
    }
}
