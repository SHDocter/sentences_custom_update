from pyncm import apis

apis.login.LoginViaAnonymousAccount() # 匿名登录ncm

playlist_id = ""
song_id = ""
song_list = []

playlist = apis.playlist.GetPlaylistAllTracks(playlist_id)["songs"]

for song in playlist:
    song_name = song["name"]
    song_id = song["id"]
    song = {song_name: f"https://music.163.com/#/song?id={song_id}"}
    song_list.append(song)

print(song_list)