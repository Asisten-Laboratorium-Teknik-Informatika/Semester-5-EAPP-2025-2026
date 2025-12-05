-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Waktu pembuatan: 02 Des 2025 pada 06.32
-- Versi server: 10.4.28-MariaDB
-- Versi PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smartpay`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `transactions`
--

CREATE TABLE `transactions` (
  `id` int(11) NOT NULL,
  `user_email` varchar(100) DEFAULT NULL,
  `product` varchar(50) DEFAULT NULL,
  `account_number` varchar(30) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `admin_fee` int(11) DEFAULT 1500,
  `total` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'pending',
  `reference` varchar(225) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `pay_code` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `transactions`
--

INSERT INTO `transactions` (`id`, `user_email`, `product`, `account_number`, `amount`, `admin_fee`, `total`, `status`, `reference`, `created_at`, `pay_code`) VALUES
(21, 'andre@gmail.com', 'DANA50', '082369396188', 50000, 4250, 54250, 'pending', 'DEV-T14876311566EOKSG', '2025-11-25 04:27:46', '360824690424413'),
(22, 'andre@gmail.com', 'DANA50', '082369396188', 50000, 4250, 54250, 'success', 'DEV-T14876313642QJNOT', '2025-12-02 03:03:24', '552166104479117'),
(23, 'yazid@gmail.com', 'DANA50', '082369396188', 50000, 4250, 54250, 'success', 'DEV-T14876313688T0NXM', '2025-12-02 04:59:02', '488817917961753');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `fullname`, `email`, `phone`, `password`) VALUES
(7, 'Andre Tri Ramadana', 'andre@gmail.com', '082369396188', 'bd01b0b648c2c64eb1bddd9361d9972ea684b344fedc4d166654a85e8919e7ad'),
(8, 'Yai]]]]zid', 'yazid@gmail.com', '08236939618822', 'c42452727400c956e39cb8fbcd95fa803b0953832ed27e02a85c5ca3d5dca2a5');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `transactions`
--
ALTER TABLE `transactions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=24;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
