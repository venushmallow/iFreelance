-- MySQL dump 10.13  Distrib 8.0.18, for macos10.14 (x86_64)
--
-- Database: job
-- ------------------------------------------------------
-- Server version	8.0.23

--
-- Table structure for table `job`
--
CREATE DATABASE IF NOT EXISTS `job` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `job`;

DROP TABLE IF EXISTS `job`;

CREATE TABLE `job` (
  `job_id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(64) NOT NULL,
  `description` mediumtext NOT NULL,
  `price` float NOT NULL,
  `seller_id` int NOT NULL,
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;

--
-- Dumping data for table `job`
--

INSERT INTO `job` VALUES 
(1,'Design Portfolio Website', 'Design a professional website for your business.', 40, 2),
(2,'Logo Design', 'Design a Logo for your business.', 30, 2),
(3,'Party Wrecker','Hire my service to wreck any party you want to bail out from but forced to come.', 60.5, 1),
(4,'Babysit Children','Babysit your children at home.', 70, 1)
