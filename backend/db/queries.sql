-- Ideas:
-- Retrieve the name of an artist and the name of all tracks in an album:
SELECT ar.name AS Artist_name, al.name AS Album_name, s.name AS Song_name
FROM Artists AS ar
JOIN Albums AS al ON ar.id = al.artist_id
JOIN Songs AS s ON al.id = s.album_id

-- Retrieve the name of a user, the name of a playlist, and all tracks in the playlist:
SELECT u.name AS Username, pl.name AS Playlist_name, s.name AS Song_name
FROM Users AS u
JOIN Playlists AS pl ON u.id = p.user_id
JOIN Playlist_tracks AS pl_t ON p.id = pl_t.playlists_id
JOIN Songs AS s ON pl_t.song_id = s.id

-- Retrieve the name of a user and all artists they are following:

-- Retrieve the name of a user and all tracks they have liked:

-- Retrieve the name of an artist and the name of all tracks in an album, but only for albums released in the last 5 years:

-- Retrieve the name of a user and all tracks in a playlist, but only for playlists that contain more than 10 tracks:

-- Retrieve the name of a user, the name of a playlist, and all tracks in the playlist, but only for playlists that were created in the last 2 years:

-- Retrieve the name of a user and all artists they are following, but only for users who are following more than 5 artists:
