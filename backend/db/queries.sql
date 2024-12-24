-- Important notes:
--      Some tables when explain is used show ALL as their table search. 
--      Its not because queries are not optimized but because you are not using where and selecting someone specific.
--      Use where to see how well is the table optimized.

-- Ideas:
-- Retrieve the name of an artist and the name of all tracks in an album:
-- EXPLAIN
SELECT ar.name AS Artist_name, al.name AS Album_name, s.name AS Song_name
FROM non_deleted_artists AS ar
JOIN non_deleted_albums AS al ON ar.id = al.artist_id
JOIN non_deleted_songs AS s ON al.id = s.album_id

-- EXPLAIN
SELECT s.name AS Songs FROM non_deleted_songs AS s
JOIN Playlist_tracks AS plt ON s.id = plt.song_id
JOIN non_deleted_playlists AS pl ON pl.id = plt.playlists_id;

-- Retrieve the name of a user, the name of a playlist, and all tracks in the playlist:
-- EXPLAIN
SELECT u.username AS Username, pl.name AS Playlist_name, s.name AS Song_name
FROM non_deleted_users AS u
JOIN non_deleted_playlists AS pl ON u.id = pl.creator_id
JOIN Playlist_tracks AS pl_t ON pl.id = pl_t.playlists_id
JOIN non_deleted_songs AS s ON pl_t.song_id = s.id;

-- Retrieve the name of a user and all artists they are following:
-- EXPLAIN
SELECT u.username AS Username, a.name AS Artists 
FROM non_deleted_users AS u
JOIN Artists_followers AS af ON u.id = af.user_id
JOIN non_deleted_artists AS a ON af.artist_id = a.id;

-- Retrieve the name of a user and all tracks they have liked:
-- EXPLAIN
SELECT u.username AS Username, s.name AS Song_name
FROM non_deleted_users AS u
JOIN Likes AS l ON u.id = l.user_id
JOIN non_deleted_songs AS s ON l.song_id = s.id;

-- Retrieve the name of an artist and the name of all tracks in an album, but only for albums released in the last 5 years:
EXPLAIN
SELECT ar.name AS Artist, s.name AS Song_name, DATE_FORMAT(al.release_date, '%Y') AS Date_released
FROM non_deleted_artists AS ar
JOIN non_deleted_albums AS al ON ar.id = al.artist_id
JOIN non_deleted_songs AS s ON al.id = s.album_id
WHERE YEAR(CURDATE()) - DATE_FORMAT(al.release_date, '%Y') <= 5; 

-- Retrieve the name of a user and all tracks in a playlist, but only for playlists that contain more than 10 tracks:
-- EXPLAIN
SELECT u.username AS Username, pl.name AS Playlist, COUNT(s.name) AS Song_count
FROM non_deleted_users AS u
JOIN non_deleted_playlists AS pl ON u.id = pl.creator_id
JOIN Playlist_tracks AS plt ON pl.id = plt.playlists_id
JOIN non_deleted_songs AS s ON s.id = plt.song_id
GROUP BY u.username, pl.name
HAVING COUNT(plt.song_id) > 10;

-- Retrieve the name of a user, the name of a playlist, and all tracks in the playlist, but only for playlists that were created in the last 2 years:
-- EXPLAIN
SELECT u.username AS Username, pl.name AS Playlist, s.name AS Songs
FROM non_deleted_users AS u
JOIN non_deleted_playlists AS pl ON u.id = pl.creator_id
JOIN Playlist_tracks AS plt ON pl.id = plt.playlists_id
JOIN Songs AS s ON s.id = plt.song_id
WHERE YEAR(CURDATE()) - DATE_FORMAT(pl.date_creation, '%Y')  <= 2;

-- Retrieve the name of a user and all artists they are following, but only for users who are following more than 5 artists:
-- EXPLAIN
SELECT u.username AS Username, COUNT(a.name) AS Number_of_artists_following
FROM non_deleted_users AS u
JOIN Artists_followers AS af ON u.id = af.user_id
JOIN non_deleted_artists AS a ON a.id = af.artist_id
GROUP BY u.username
HAVING COUNT(a.name) >= 2;