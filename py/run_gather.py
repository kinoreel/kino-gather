import sys

from gather import Gather

server = sys.argv[0]
port = sys.argv[1]
database = sys.argv[2]
username = sys.argv[3]
password = sys.argv[4]
omdb_key = sys.argv[5]
tmdb_key = sys.argv[6]
guidebox_key = sys.argv[7]
youtube_films_key = sys.argv[8]

get = Gather(server, port, database, username, password, omdb_key, tmdb_key, guidebox_key, youtube_films_key)

get.gather_new_kino_movies()