package com.payment.service.stripe;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.Map;

import com.google.gson.Gson;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.RequestBuilder;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

@ExtendWith(SpringExtension.class)
@WebMvcTest(StripeServiceController.class)
@ContextConfiguration(classes={StripeApplication.class, ViewController.class, StripeServiceController.class})
class StripeServiceTests {
    @Autowired
    private MockMvc mvc;

    @Value("${STRIPE_PUBLISHABLE_KEY}")
    private String stripePK;

    @Test
    void stripeHealthCheck_ReturnsString() throws Exception {
        RequestBuilder request = MockMvcRequestBuilders.get("/health");
        MvcResult result = mvc.perform(request).andReturn();
        assertEquals("{'message': 'Stripe service is healthy.'}", result.getResponse().getContentAsString());
    }

    @Test
    void checkConfig_ReturnsKeyString() throws Exception {
        RequestBuilder request = MockMvcRequestBuilders.get("/config");
        MvcResult result = mvc.perform(request).andReturn();
        Gson gson = new Gson();
        Map<String, String> expectedResponse = new HashMap<>();
        expectedResponse.put("publishableKey", stripePK);
        assertEquals(gson.toJson(expectedResponse), result.getResponse().getContentAsString());
    }
}
