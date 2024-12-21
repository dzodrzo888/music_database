DROP TABLE IF EXISTS `Likes`;
DROP TABLE IF EXISTS `Followers_users`;
DROP TABLE IF EXISTS `Artists_followers`;
DROP TABLE IF EXISTS `Playlist_tracks`;
DROP TABLE IF EXISTS `Playlists`;
DROP TABLE IF EXISTS `Songs`;
DROP TABLE IF EXISTS `Albums`;
DROP TABLE IF EXISTS `Artists`;
DROP TABLE IF EXISTS `Users`;
-- USERS
-- table mapping users.
CREATE TABLE `Users`(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(30) NOT NULL,
    email VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    deleted TINYINT DEFAULT 0,
    profile_image BLOB
);

-- ARTIST
-- table mapping artists.
CREATE TABLE `Artists` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    genre VARCHAR(50) NOT NULL,
    deleted TINYINT DEFAULT 0,
    profile_image BLOB
);

-- ALBUMS
CREATE TABLE `Albums`(
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    release_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    album_image BLOB,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (artist_id) REFERENCES Artists(id)
);

-- SONGS
CREATE TABLE `Songs` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    album_id INT NOT NULL,
    artist_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    release_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    song_image BLOB,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY(album_id) REFERENCES Albums(id),
    FOREIGN KEY(artist_id) REFERENCES Artists(id)
);

-- PLAYLISTS
CREATE TABLE `Playlists` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    playlist_image BLOB,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Playllist_track
-- table connecting playlists and tracks
CREATE TABLE `Playlist_tracks`(
    playlists_id INT NOT NULL,
    song_id INT NOT NULL,
    `order` INT,
    PRIMARY KEY (playlists_id, song_id),
    FOREIGN KEY (playlists_id) REFERENCES Playlists(id),
    FOREIGN KEY (song_id) REFERENCES Songs(id)
);

-- Folowers_artists
-- table connecting users and artists
CREATE TABLE `Artists_followers`(
    user_id INT NOT NULL,
    artist_id INT NOT NULL,
    PRIMARY KEY (user_id, artist_id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (artist_id) REFERENCES Artists(id)
);

-- Followers_users
-- table connecting users together
CREATE TABLE `Followers_users`(
    user_id1 INT NOT NULL,
    user_id2 INT NOT NULL,
    PRIMARY KEY (user_id1, user_id2),
    FOREIGN KEY (user_id1) REFERENCES Users(id),
    FOREIGN KEY (user_id2) REFERENCES Users(id)
);

-- Likes
-- table connecting liked songs and users
CREATE TABLE `Likes` (
    user_id INT NOT NULL,
    song_id INT NOT NULL,
    `order` INT,
    PRIMARY KEY (user_id, song_id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (song_id) REFERENCES Songs(id)
);

-- Trigger creation

DELIMITER //
-- This Trigger will delete all users from following tables if a user deletes their account
CREATE TRIGGER before_user_delete
BEFORE UPDATE ON `Users`
FOR EACH ROW
BEGIN
    IF NEW.deleted = 1 AND OLD.deleted = 0 THEN
        DELETE FROM `Followers_users` 
        WHERE user_id1 = OLD.id OR user_id2 = OLD.id;
        DELETE FROM `Artists_followers`
        WHERE user_id = OLD.id;
        DELETE FROM `Likes`
        WHERE user_id = OLD.id;
    END IF;
END;
//

CREATE TRIGGER before_artist_delete
BEFORE UPDATE ON `Artists`
FOR EACH ROW
BEGIN
    IF NEW.deleted = 1 AND OLD.deleted = 0 THEN
        UPDATE`Albums`
        SET deleted = 1
        WHERE artist_id = OLD.id;
        DELETE FROM `Artists_followers`
        WHERE artist_id = OLD.id;
    END IF;
END;
//

CREATE TRIGGER before_album_delete
BEFORE UPDATE ON `Albums`
FOR EACH ROW
BEGIN
    IF NEW.deleted = 1 AND OLD.deleted = 0 THEN
        UPDATE `Songs`
        SET deleted = 1
        WHERE album_id = OLD.id;
    END IF;
END;
//

CREATE TRIGGER before_song_delete
BEFORE UPDATE ON `Songs`
FOR EACH ROW
BEGIN 
    IF NEW.deleted = 1 AND OLD.deleted = 0 THEN
        DELETE FROM `Likes`
        WHERE song_id = OLD.id;
        DELETE FROM `Playlist_tracks`
        WHERE song_id = OLD.id;
    END IF;
END;
//

CREATE TRIGGER before_playlist_delete
BEFORE UPDATE ON `Playlists`
FOR EACH ROW
BEGIN
    IF NEW.deleted = 1 AND OLD.deleted = 0 THEN
        DELETE FROM `Playlists_tracks`
        WHERE playlists_id = OLD.id;
    END IF;
END;
//

DELIMITER ;