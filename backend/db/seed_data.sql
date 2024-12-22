INSERT INTO `Users` (username, password, email, date_of_birth, profile_image) VALUES
('john_doe', 'password123', 'john@example.com', '1990-01-01', NULL),
('jane_smith', 'password456', 'jane@example.com', '1985-05-15', NULL),
('alice_jones', 'password789', 'alice@example.com', '1992-07-20', NULL),
('bob_brown', 'password111', 'bob@example.com', '1988-03-22', NULL),
('charlie_black', 'password222', 'charlie@example.com', '1991-06-14', NULL),
('david_white', 'password333', 'david@example.com', '1983-09-10', NULL),
('eve_green', 'password444', 'eve@example.com', '1995-12-05', NULL),
('frank_blue', 'password555', 'frank@example.com', '1987-11-11', NULL),
('grace_red', 'password666', 'grace@example.com', '1994-04-18', NULL),
('hank_yellow', 'password777', 'hank@example.com', '1990-07-07', NULL),
('ivy_purple', 'password888', 'ivy@example.com', '1989-08-08', NULL),
('jack_orange', 'password999', 'jack@example.com', '1993-10-10', NULL),
('kate_pink', 'password000', 'kate@example.com', '1991-11-11', NULL),
('leo_gray', 'passwordaaa', 'leo@example.com', '1986-12-12', NULL),
('mia_brown', 'passwordbbb', 'mia@example.com', '1992-01-01', NULL);

-- Seed data for Artists
INSERT INTO `Artists` (name, genre, profile_image) VALUES
('The Beatles', 'Rock', NULL),
('Taylor Swift', 'Pop', NULL),
('Miles Davis', 'Jazz', NULL),
('Billie Eilish', 'Pop', NULL),
('Dua Lipa', 'Pop', NULL);

-- Seed data for Albums
INSERT INTO `Albums` (artist_id, name, release_date, album_image) VALUES
(1, 'Abbey Road', '1969-09-26', NULL),
(2, '1989', '2014-10-27', NULL),
(3, 'Kind of Blue', '1959-08-17', NULL),
(4, 'Happier Than Ever', '2021-07-30', NULL),
(5, 'Future Nostalgia', '2020-03-27', NULL);

-- Seed data for Songs
INSERT INTO `Songs` (album_id, artist_id, name, release_date, song_image) VALUES
(1, 1, 'Come Together', '1969-09-26', NULL),
(1, 1, 'Something', '1969-09-26', NULL),
(2, 2, 'Shake It Off', '2014-10-27', NULL),
(2, 2, 'Blank Space', '2014-10-27', NULL),
(3, 3, 'So What', '1959-08-17', NULL),
(3, 3, 'Freddie Freeloader', '1959-08-17', NULL),
(4, 4, 'Happier Than Ever', '2021-07-30', NULL),
(4, 4, 'Your Power', '2021-07-30', NULL),
(5, 5, 'Dont Start Now', '2020-03-27', NULL),
(5, 5, 'Levitating', '2020-03-27', NULL),
(1, 1, 'Maxwells Silver Hammer', '1969-09-26', NULL),
(1, 1, 'Oh! Darling', '1969-09-26', NULL),
(2, 2, 'Style', '2014-10-27', NULL),
(2, 2, 'Wildest Dreams', '2014-10-27', NULL),
(3, 3, 'Blue in Green', '1959-08-17', NULL),
(3, 3, 'All Blues', '1959-08-17', NULL),
(4, 4, 'Lost Cause', '2021-07-30', NULL),
(4, 4, 'Oxytocin', '2021-07-30', NULL),
(5, 5, 'Physical', '2020-03-27', NULL),
(5, 5, 'Hallucinate', '2020-03-27', NULL),
(5, 5, 'Love Again', '2020-03-27', NULL);

-- Seed data for Playlists
INSERT INTO `Playlists` (user_id, name, date_creation, playlist_image) VALUES
(1, 'Johns favorites', '2022-01-15', NULL),
(2, 'Janes chill mix', '2021-12-20', NULL),
(3, 'Alices workout playlist', '2022-03-10', NULL),
(4, 'Bobs rock collection', '2021-11-05', NULL),
(5, 'Charlies jazz vibes', '2022-02-25', NULL),
(6, 'Davids pop hits', '2021-10-30', NULL),
(7, 'Eves party mix', '2022-04-18', NULL),
(8, 'Franks workout tunes', '2021-09-12', NULL),
(9, 'Graces chill playlist', '2022-05-22', NULL),
(10, 'Hanks road trip', '2021-08-14', NULL),
(11, 'Ivys study playlist', '2022-06-01', NULL),
(12, 'Jacks workout mix', '2021-07-19', NULL),
(13, 'Kates favorites', '2022-07-10', NULL),
(14, 'Leos jazz collection', '2021-06-25', NULL),
(15, 'Mias pop hits', '2022-08-05', NULL);

-- Seed data for Playlist_tracks
INSERT INTO `Playlist_tracks` (playlists_id, song_id, `order`) VALUES
(1, 1, 1),
(1, 3, 2),
(1, 5, 3),
(1, 7, 4),
(1, 9, 5),
(1, 2, 6),
(1, 4, 7),
(1, 6, 8),
(1, 8, 9),
(1, 10, 10),
(1, 11, 11),
(2, 12, 1),
(2, 13, 2),
(2, 14, 3),
(2, 15, 4),
(2, 1, 5),
(2, 2, 6),
(2, 3, 7),
(2, 4, 8),
(2, 5, 9),
(2, 6, 10),
(2, 7, 11),
(3, 8, 1),
(3, 9, 2),
(3, 10, 3),
(3, 11, 4),
(3, 12, 5),
(3, 13, 6),
(3, 14, 7),
(3, 15, 8),
(3, 1, 9),
(3, 2, 10),
(3, 3, 11),
(4, 4, 1),
(4, 5, 2),
(4, 6, 3),
(4, 7, 4),
(4, 8, 5),
(4, 9, 6),
(4, 10, 7),
(4, 11, 8),
(4, 12, 9),
(4, 13, 10),
(4, 14, 11),
(5, 15, 1),
(5, 1, 2),
(5, 2, 3),
(5, 3, 4),
(5, 4, 5),
(5, 5, 6),
(5, 6, 7),
(5, 7, 8),
(5, 8, 9),
(5, 9, 10),
(5, 10, 11),
(6, 11, 1),
(6, 12, 2),
(6, 13, 3),
(6, 14, 4),
(6, 15, 5),
(6, 1, 6),
(6, 2, 7),
(6, 3, 8),
(6, 4, 9),
(6, 5, 10),
(6, 6, 11),
(7, 7, 1),
(7, 8, 2),
(7, 9, 3),
(7, 10, 4),
(7, 11, 5),
(7, 12, 6),
(7, 13, 7),
(7, 14, 8),
(7, 15, 9),
(7, 1, 10),
(7, 2, 11);

-- Seed data for Artists_followers
INSERT INTO `Artists_followers` (user_id, artist_id) VALUES
(1, 1),
(1, 2),
(2, 3),
(3, 1),
(3, 3),
(1, 4),
(2, 5);

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
(3, 6, 2),
(1, 7, 1),
(1, 8, 2),
(2, 9, 1),
(2, 10, 2);