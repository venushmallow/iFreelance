package com.payment.service;

import java.util.HashMap;
import java.util.Map;

import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonProperty;

public class PaymentDetails {
    @JsonProperty
    private String username;

    @JsonProperty
    private String email;

    @JsonProperty
    private double amount;

    private Map<String, Object> optional = new HashMap<>();

    public PaymentDetails() {
        // Empty constructor
    }

    @JsonAnySetter
    public void addOptional(String name, Object value) {
        optional.put(name, value);
    }
    @JsonAnyGetter
    public Object getOptional(String name) {
        return optional.get(name);
    }

    public String getUsername() {
        return username;
    }

    public String getEmail() {
        return email;
    }

    public double getAmount() {
        return amount;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public void setAmount(double amount) {
        this.amount = amount;
    }
}
