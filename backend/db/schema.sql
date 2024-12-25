DROP TABLE IF EXISTS `Payments`;
DROP TABLE IF EXISTS `User_subscriptions`;
DROP TABLE IF EXISTS `Playlists_users`;
DROP TABLE IF EXISTS `Likes`;
DROP TABLE IF EXISTS `Followers_users`;
DROP TABLE IF EXISTS `Artists_followers`;
DROP TABLE IF EXISTS `Playlist_tracks`;
DROP TABLE IF EXISTS `Playlists`;
DROP TABLE IF EXISTS `Songs`;
DROP TABLE IF EXISTS `Albums`;
DROP TABLE IF EXISTS `Artists`;
DROP TABLE IF EXISTS `Users`;
DROP TABLE IF EXISTS `Subscription_plan_info`;
DROP VIEW IF EXISTS `non_deleted_users`;
DROP VIEW IF EXISTS `non_deleted_artists`;
DROP VIEW IF EXISTS `non_deleted_albums`;
DROP VIEW IF EXISTS `non_deleted_songs`;
DROP VIEW IF EXISTS `non_deleted_playlists`;
-- USERS
-- table mapping users.
CREATE TABLE `Users`(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    deleted TINYINT DEFAULT 0,
    type VARCHAR(20) NOT NULL DEFAULT 'regular',
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
    creator_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    playlist_image BLOB,
    deleted TINYINT DEFAULT 0,
    FOREIGN KEY (creator_id) REFERENCES Users(id)
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

CREATE TABLE `Playlists_users` (
    playlists_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (playlists_id, user_id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (playlists_id) REFERENCES Playlists(id)
);

CREATE TABLE `Subscription_plan_info` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(200) NOT NULL,
    price MEDIUMINT UNSIGNED NOT NULL,
    duration SMALLINT NOT NULL,
    deleted TINYINT(1) NOT NULL DEFAULT 0
);

CREATE TABLE `Payments` (
    id INT NOT NULL PRIMARY KEY,
    user_id INT NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    money_value MEDIUMINT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE `User_subscriptions` (
    user_id INT NOT NULL,
    subscription_plan_id INT NOT NULL,
    start_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiration_date DATETIME DEFAULT NULL,
    PRIMARY KEY(user_id, subscription_plan_id),
    FOREIGN KEY(user_id) REFERENCES Users(id),
    FOREIGN KEY(subscription_plan_id) REFERENCES Subscription_plan_info(id)
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

CREATE TRIGGER expritaion_date_calc
BEFORE INSERT ON `User_subscriptions`
FOR EACH ROW
BEGIN
    DECLARE plan_duration INT;

    SELECT duration INTO plan_duration
    FROM Subscription_plan_info
    WHERE id = NEW.subscription_plan_id;

    SET NEW.expiration_date = DATE_ADD(NEW.start_date, INTERVAL plan_duration DAY);
END;
//

DELIMITER ;

-- Attempt to add the column
ALTER TABLE Playlists
ADD date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE Users
ADD user_type VARCHAR(20) NOT NULL DEFAULT 'regular';

-- Index creation
CREATE INDEX artist_name ON Artists(name);
CREATE INDEX album_name ON Albums(name);
CREATE INDEX song_name ON Songs(name);
CREATE INDEX playlist_name ON Playlists(name);
CREATE INDEX user_username ON Users(username);
CREATE INDEX artist_genre ON Artists(genre);

-- Create views
CREATE VIEW `non_deleted_users` AS
SELECT * FROM `Users`
WHERE deleted = 0
WITH CHECK OPTION;

CREATE VIEW `non_deleted_artists` AS 
SELECT * FROM `Artists`
WHERE deleted = 0
WITH CHECK OPTION;

CREATE VIEW `non_deleted_albums` AS 
SELECT * FROM `Albums`
WHERE deleted = 0
WITH CHECK OPTION;

CREATE VIEW `non_deleted_songs` AS
SELECT * FROM `Songs`
WHERE deleted = 0
WITH CHECK OPTION;

CREATE VIEW `non_deleted_playlists` AS
SELECT * FROM `Playlists`
WHERE deleted = 0
WITH CHECK OPTION;

CREATE VIEW `non_deleted_subscriptions` AS
SELECT * FROM `Subscription_plan_info`
WHERE deleted = 0
WITH CHECK OPTION;