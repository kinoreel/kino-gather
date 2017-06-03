import json

from gather import Gather


with open('db_auth.json') as auth_file:
    auth = json.load(auth_file)['postgres_dev']

get = Gather(auth)

get.gather_new_kino_movies()