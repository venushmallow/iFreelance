# FROM openjdk:11
FROM maven:3.8.3-jdk-11-slim AS build
EXPOSE 4242
# WORKDIR /home/dockerdemo
# COPY ./ ./
# RUN mvn -f ./pom.xml clean package
# ADD ./target/stripe-service-spring-boot.jar ./stripe-service-spring-boot.jar
# ENTRYPOINT ["java", "-jar", "./stripe-service-spring-boot.jar"]
ADD target/stripe-service-spring-boot.jar stripe-service-spring-boot.jar
ENTRYPOINT ["java", "-jar", "-Dspring.profiles.active=dev", "/stripe-service-spring-boot.jar"]

