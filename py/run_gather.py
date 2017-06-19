import GLOBALS

from gather import Gather

auth = GLOBALS.POSTGRES_DEV

get = Gather(auth)

get.gather_new_kino_movies()