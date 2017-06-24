from gather import Gather

from py import GLOBALS

auth = GLOBALS.POSTGRES_DEV

get = Gather(auth)

get.gather_new_kino_movies()