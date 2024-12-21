INSERT INTO `Users` (username, password, email, date_of_birth, profile_image) VALUES
('john_doe', 'password123', 'john@example.com', '1990-01-01', NULL),
('jane_smith', 'password456', 'jane@example.com', '1985-05-15', NULL),
('alice_jones', 'password789', 'alice@example.com', '1992-07-20', NULL);

-- Seed data for Artists
INSERT INTO `Artists` (name, genre, profile_image) VALUES
('The Beatles', 'Rock', NULL),
('Taylor Swift', 'Pop', NULL),
('Miles Davis', 'Jazz', NULL);

-- Seed data for Albums
INSERT INTO `Albums` (artist_id, name, release_date, album_image) VALUES
(1, 'Abbey Road', '1969-09-26', NULL),
(2, '1989', '2014-10-27', NULL),
(3, 'Kind of Blue', '1959-08-17', NULL);

-- Seed data for Songs
INSERT INTO `Songs` (album_id, artist_id, name, release_date, song_image) VALUES
(1, 1, 'Come Together', '1969-09-26', NULL),
(1, 1, 'Something', '1969-09-26', NULL),
(2, 2, 'Shake It Off', '2014-10-27', NULL),
(2, 2, 'Blank Space', '2014-10-27', NULL),
(3, 3, 'So What', '1959-08-17', NULL),
(3, 3, 'Freddie Freeloader', '1959-08-17', NULL);

INSERT INTO `Playlists` (user_id, name, playlist_image) VALUES
(1, 'Johns favorites', NULL),
(2, 'Janes chill mix', NULL),
(3, 'Alices workout playlist', NULL);

INSERT INTO `Playlist_tracks` (playlists_id, song_id, `order`) VALUES
(1, 1, 1),
(1, 3, 2),
(2, 5, 1),
(2, 6, 2),
(3, 2, 1),
(3, 4, 2);

-- Seed data for Artists_followers
INSERT INTO `Artists_followers` (user_id, artist_id) VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 1),
(3, 3);

-- Seed data for Followers_users
INSERT INTO `Followers_users` (user_id1, user_id2) VALUES
(1, 2),
(1, 3),
(2, 3);

-- Seed data for Likes
INSERT INTO `Likes` (user_id, song_id, `order`) VALUES
(1, 1, 1),
(1, 2, 2),
(2, 3, 1),
(2, 4, 2),
(3, 5, 1),
(3, 6, 2);