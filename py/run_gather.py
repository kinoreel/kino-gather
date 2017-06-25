import sys

from gather import Gather

server = sys.argv[1]
port = sys.argv[2]
database = sys.argv[3]
username = sys.argv[4]
password = sys.argv[5]
omdb_key = sys.argv[6]
tmdb_key = sys.argv[7]
guidebox_key = sys.argv[8]
youtube_films_key = sys.argv[9]

get = Gather(server, port, database, username, password, omdb_key, tmdb_key, guidebox_key, youtube_films_key)

get.gather_new_kino_movies()