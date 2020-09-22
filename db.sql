-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Sep 22, 2020 at 11:42 AM
-- Server version: 5.7.31-0ubuntu0.18.04.1
-- PHP Version: 7.1.17-0ubuntu0.17.10.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `cvdnou`
--

-- --------------------------------------------------------

--
-- Table structure for table `hashImage`
--

CREATE TABLE `hashImage` (
  `id` int(11) NOT NULL,
  `file_id` text NOT NULL,
  `filename` text CHARACTER SET utf8 COLLATE utf8_spanish_ci NOT NULL,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `subs`
--

CREATE TABLE `subs` (
  `user_id` bigint(20) NOT NULL,
  `region` text CHARACTER SET utf8mb4 NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `tg_id` bigint(20) NOT NULL,
  `lang` text NOT NULL,
  `n_world` tinyint(1) NOT NULL DEFAULT '0',
  `n_spain` tinyint(1) NOT NULL DEFAULT '0',
  `n_italy` tinyint(1) NOT NULL DEFAULT '0',
  `n_france` tinyint(1) NOT NULL DEFAULT '0',
  `n_austria` int(11) NOT NULL DEFAULT '0',
  `botons` set('gl','es','it','fr','at') NOT NULL DEFAULT 'gl,es,it'
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `hashImage`
--
ALTER TABLE `hashImage`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `subs`
--
ALTER TABLE `subs`
  ADD KEY `s_key` (`user_id`,`region`(255));

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD UNIQUE KEY `id` (`tg_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `hashImage`
--
ALTER TABLE `hashImage`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1766;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
