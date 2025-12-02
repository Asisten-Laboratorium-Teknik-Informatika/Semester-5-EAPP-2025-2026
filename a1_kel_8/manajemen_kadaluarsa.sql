-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 02 Des 2025 pada 04.49
-- Versi server: 10.4.32-MariaDB
-- Versi PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `manajemen_kadaluarsa`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `foods`
--

CREATE TABLE `foods` (
  `id` int(11) NOT NULL,
  `user_email` varchar(255) NOT NULL,
  `nama_makanan` varchar(255) NOT NULL,
  `jumlah` int(11) NOT NULL,
  `tanggal_dibuat` varchar(50) NOT NULL,
  `tanggal_edit` varchar(50) DEFAULT NULL,
  `tanggal_expired` date NOT NULL,
  `created_at` varchar(50) NOT NULL,
  `updated_at` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `foods`
--

INSERT INTO `foods` (`id`, `user_email`, `nama_makanan`, `jumlah`, `tanggal_dibuat`, `tanggal_edit`, `tanggal_expired`, `created_at`, `updated_at`) VALUES
(1, 'admin@example.com', 'Chicken Tender', 2, '2025-11-12 11:11:00', NULL, '2025-11-28', '2025-11-12 11:11:00', '2025-11-12 11:11:00'),
(2, 'admin@example.com', 'Chicken Tender', 5, '2025-11-12 11:15:22', NULL, '2025-11-22', '2025-11-12 11:15:22', '2025-11-12 11:15:22'),
(3, 'admin@example.com', 'Chicken Tender', 6, '2025-11-12 11:18:13', NULL, '2025-12-05', '2025-11-12 11:18:13', '2025-11-12 11:18:13'),
(4, 'admin@example.com', '12345', 12, '2025-11-12 11:19:08', NULL, '2025-11-15', '2025-11-12 11:19:08', '2025-11-12 11:19:08'),
(5, 'admin@example.com', '12345', 32, '2025-11-12 11:20:46', NULL, '2025-11-07', '2025-11-12 11:20:46', '2025-11-12 11:20:46'),
(6, 'admin@example.com', 'Bila Bujang', 2, '2025-11-14 17:32:21', NULL, '2025-11-26', '2025-11-14 17:32:21', '2025-11-14 17:32:21'),
(7, 'ppp@example.com', 'Chicken Tender', 3, '2025-11-16 11:02:56', NULL, '2025-11-20', '2025-11-16 11:02:56', '2025-11-16 11:02:56'),
(8, 'admin@example.com', 'Chicken Tender', 3, '2025-11-18 11:16:26', NULL, '2025-11-20', '2025-11-18 11:16:26', '2025-11-18 11:16:26'),
(10, 'ppp@example.com', 'Chicken Tender', 1, '2025-11-18 11:24:42', NULL, '2025-11-21', '2025-11-18 11:24:42', '2025-11-18 11:24:42'),
(12, 'JefGantenk@example.com', 'BPK', 67, '2025-11-18 11:56:05', '2025-11-18 11:56:40', '2025-12-06', '2025-11-18 11:56:05', '2025-11-18 11:56:40'),
(13, 'JefGantenk@example.com', 'Chicken Tender', 2, '2025-11-18 11:59:49', '2025-11-18 12:00:11', '2025-11-09', '2025-11-18 11:59:49', '2025-11-18 12:00:11'),
(14, 'ppp@example.com', 'BPK', 4, '2025-11-18 20:40:07', NULL, '2025-11-19', '2025-11-18 20:40:07', '2025-11-18 20:40:07'),
(16, 'ppp@example.com', 'Tenderloin Steak', 2, '2025-11-24 11:10:35', NULL, '2025-11-28', '2025-11-24 11:10:35', '2025-11-24 11:10:35'),
(17, 'ppp@example.com', 'Makanan', 1, '2025-11-24 11:11:01', NULL, '2025-11-24', '2025-11-24 11:11:01', '2025-11-24 11:11:01'),
(18, 'ppp@example.com', 'Jefanya Goreng', 2, '2025-11-24 20:09:28', NULL, '2025-12-25', '2025-11-24 20:09:28', '2025-11-24 20:09:28'),
(19, 'ppp@example.com', 'Andre Goreng', 2, '2025-12-02 09:58:27', NULL, '2025-12-03', '2025-12-02 09:58:27', '2025-12-02 09:58:27');

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `password`, `created_at`) VALUES
(1, 'Nasution Yazid', 'admin@example.com', '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', '2025-11-12 02:27:35'),
(2, 'Michael McMannus', 'ppp@example.com', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', '2025-11-12 02:29:41'),
(3, 'rio gay', 'riogay@gmail.com', '7cbccda65959a4fe629dbdf546ae3ddea9328ae5a53498785f4a27394fe26515', '2025-11-12 02:30:08'),
(4, 'Jef si Bandar', 'JefGantenk@example.com', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', '2025-11-18 04:55:21');

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `foods`
--
ALTER TABLE `foods`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_email` (`user_email`);

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
-- AUTO_INCREMENT untuk tabel `foods`
--
ALTER TABLE `foods`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Ketidakleluasaan untuk tabel pelimpahan (Dumped Tables)
--

--
-- Ketidakleluasaan untuk tabel `foods`
--
ALTER TABLE `foods`
  ADD CONSTRAINT `foods_ibfk_1` FOREIGN KEY (`user_email`) REFERENCES `users` (`email`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
