package com.payment.service.stripe;

import java.text.DecimalFormat;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.json.simple.JSONObject;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ViewController {

    private static final Logger LOG = LogManager.getLogger();

    private JSONObject data;

    public void setData(JSONObject data) {
        String logMsg = String.format(
            "Data transferred to view: %s",
            data.toString()
        );
        LOG.debug(logMsg);
        this.data = data;
    }

    private static final DecimalFormat DF = new DecimalFormat("0.00");

    @GetMapping("/checkout")
    public String getView(Model model) {

        if (data == null) {
            return "failure";
        }

        // send a message to something to load the url?
        model.addAttribute("username", (String) data.get("username"));
        model.addAttribute("email", (String) data.get("email"));
        model.addAttribute("order", (String) data.get("order_id"));

        String amountStr = String.valueOf(data.get("amount"));

        long amount = Long.parseLong(amountStr);
        model.addAttribute("amount", amount);

        double displayAmount = ((double) amount) / 100;
        model.addAttribute("displayAmount", DF.format(displayAmount));

        return "index";
    }

    @GetMapping("/redirect")
    public String getRedirect() {
        LOG.debug("Redirecting page...");
        return "thanks";
    }
}
