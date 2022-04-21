package com.payment.service;

import org.springframework.stereotype.Service;

import org.apache.http.client.HttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.HttpComponentsClientHttpRequestFactory;
import org.springframework.web.client.RestTemplate;

@Service
public class RequestService {

    @Value("${api_key}")
    private String xAPIKey;

    private RestTemplate restTemplate;

    public ResponseEntity<?> createAuthHttpPatchRequest(
        String data, String url) {

        restTemplate = new RestTemplate();
        HttpClient httpClient = HttpClientBuilder.create().build();
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-API-Key", xAPIKey);
        restTemplate.setRequestFactory(
            new HttpComponentsClientHttpRequestFactory(httpClient)
        );
        HttpEntity<String> reqEntity = new HttpEntity<String>(data, headers);
        ResponseEntity<String> responseEntity = restTemplate.exchange(
            url, HttpMethod.PATCH, reqEntity, String.class
        );

        return responseEntity;
    }

    public ResponseEntity<String> createHttpRequest(
        String data, String url, HttpMethod method) {

        restTemplate = new RestTemplate();
        HttpEntity<String> request = new HttpEntity<>(data);
        ResponseEntity<String> response = null;

        try {
            response = restTemplate.exchange(
                url, method, request, String.class
            );
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

        return response;
    }

    public ResponseEntity<?> createHttpPatchRequest(String data, String url) {

        restTemplate = new RestTemplate();
        HttpClient httpClient = HttpClientBuilder.create().build();
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        restTemplate.setRequestFactory(
            new HttpComponentsClientHttpRequestFactory(httpClient)
        );
        HttpEntity<String> reqEntity = new HttpEntity<String>(data, headers);
        ResponseEntity<String> responseEntity = restTemplate.exchange(
            url, HttpMethod.PATCH, reqEntity, String.class
        );

        return responseEntity;
    }
}
