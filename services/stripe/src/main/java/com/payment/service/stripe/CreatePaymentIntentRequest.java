package com.payment.service.stripe;

import com.google.gson.annotations.SerializedName;

public class CreatePaymentIntentRequest {
    @SerializedName("amount")
    long amount;

    public Long getAmount() {
      return amount;
    }

    @SerializedName("email")
    String email;

    public String getEmail() {
      return email;
    }

    @SerializedName("order")
    String order;

    public String getOrder() {
      return order;
    }
}
