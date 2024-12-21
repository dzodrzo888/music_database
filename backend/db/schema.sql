DROP TABLE IF EXISTS `Users`;
DROP TABLE IF EXISTS `Artists`;
DROP TABLE IF EXISTS `Songs`;
DROP TABLE IF EXISTS `Albums`;
DROP TABLE IF EXISTS `Playlists`;
DROP TABLE IF EXISTS `Playlist_tracks`;
DROP TABLE IF EXISTS `Artists_users`;
--USERS
--table mapping users.
CREATE TABLE `Users`(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(30) NOT NULL,
    email VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    profile_image BLOB
);

--ARTIST
--table mapping artists.
CREATE TABLE `Artists` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    profile_image BLOB
);

--SONGS
CREATE TABLE `Songs` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    album_id INT NOT NULL,
    artist_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    release_date DATE NOT NULL DEFAULT CURDATE(),
    song_image BLOB,
    FOREIGN KEY(album_id) REFERENCES Albums(id),
    FOREIGN KEY(artist_id) REFERENCES Artists(id)
);

--ALBUMS
CREATE TABLE `Albums`(
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    release_date DATE NOT NULL DEFAULT CURDATE(),
    album_image BLOB,
    FOREIGN KEY (artist_id) REFERENCES Artists(id)
);

--PLAYLISTS
CREATE TABLE `Playlists` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    playlist_image BLOB,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

--Playllist_track
--table connecting playlists and tracks
CREATE TABLE `Playlist_tracks`(
    playlists_id INT NOT NULL,
    song_id INT NOT NULL,
    ORDER SMALLINT,
    PRIMARY KEY (playlists_id, song_id)
    FOREIGN KEY (playlists_id) REFERENCES Playlists(id),
    FOREIGN KEY (song_id) REFERENCES Songs(id)
);

--Folowers_artists
--table connecting users and artists
CREATE TABLE `Artists_followers`(
    user_id INT NOT NULL,
    artist_id INT NOT NULL,
    PRIMARY KEY (user_id, artist_id)
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (artist_id) REFERENCES Artists(id)
);

--Followers_users
--table connecting users together
CREATE TABLE `Followers_users`(
    user_id1 INT NOT NULL,
    user_id2 INT NOT NULL,
    PRIMARY KEY (user_id1, user_id2)
    FOREIGN KEY (user_id1) REFERENCES Users(id),
    FOREIGN KEY (user_id2) REFERENCES Users(id)
)