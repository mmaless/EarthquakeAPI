CREATE DATABASE  IF NOT EXISTS `eqdashboard`;
USE `eqdashboard`;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
CREATE TABLE `events` (
  `id` varchar(20) NOT NULL,
  `latitude` decimal(20,14) NOT NULL,
  `longitude` decimal(20,14) NOT NULL,
  `mag` decimal(20,14) NOT NULL,
  `time` timestamp NOT NULL,
  `place` text NOT NULL,
  `updated` timestamp NULL DEFAULT NULL,
  `type` varchar(40) DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `depth` decimal(20,14) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

--
-- Table structure for table `locations`
--

DROP TABLE IF EXISTS `locations`;
CREATE TABLE `locations` (
  `name` varchar(45) NOT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `northeast_lat` float DEFAULT NULL,
  `northeast_lng` float DEFAULT NULL,
  `southwest_lat` float DEFAULT NULL,
  `southwest_lng` float DEFAULT NULL,
  PRIMARY KEY (`name`)
);
