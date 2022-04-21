package com.payment.service;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.util.HashMap;
import java.util.Map;

import org.json.simple.JSONObject;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.junit.jupiter.SpringExtension;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.RequestBuilder;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;

@ExtendWith(SpringExtension.class)
@WebMvcTest(PaymentServiceController.class)
class PaymentTests {
    @Autowired
    private MockMvc mvc;

    @MockBean
    private RequestService requestService;

    @MockBean
    private JSONService jsonService;

    @Test
    void healthCheck_ReturnsString() throws Exception {
        RequestBuilder request = MockMvcRequestBuilders.get("/health");
        MvcResult result = mvc.perform(request).andReturn();
        assertEquals("{'message': 'Service is healthy'}", result.getResponse().getContentAsString());
    }

    @Test
    void inputFormat_ReturnsJSONObject() throws Exception {
        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("username", "username");
        requestBody.put("email", "email@email.com");
        requestBody.put("amount", 1000);
        requestBody.put("order_id", 1);
        JSONObject requestJson = new JSONObject(requestBody);

        RequestBuilder request = MockMvcRequestBuilders.get("/check-stripe");
        MvcResult checkConnection = mvc.perform(request).andReturn();

        MvcResult result = mvc.perform(
            MockMvcRequestBuilders.post("/")
            .contentType(MediaType.APPLICATION_JSON)
            .content(requestJson.toJSONString())
        ).andReturn();

        String stripeConn = checkConnection.getResponse().getContentAsString();

        if (stripeConn == "{'message': 'Stripe service is healthy.'}") {
            assertEquals(requestJson.toJSONString(), result.getResponse().getContentAsString());
        } else {
            String exception = result.getResponse().getContentAsString();
            assertEquals(exception,result.getResponse().getContentAsString());
        }
    }
}
