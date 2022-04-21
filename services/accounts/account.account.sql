-- MySQL dump 10.13  Distrib 8.0.18, for macos10.14 (x86_64)
--
-- Database: account
-- ------------------------------------------------------
-- Server version	8.0.23

--
-- Table structure for table `account`
--
CREATE DATABASE IF NOT EXISTS `account` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `account`;

DROP TABLE IF EXISTS `account`;

CREATE TABLE `account` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `user_email` varchar(64) NOT NULL,
  `password` varchar(100) NOT NULL,
  `user_phone` varchar(10) NOT NULL,
  PRIMARY KEY (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `account`
--
-- Dump completed on 2021-08-15  1:38:38
