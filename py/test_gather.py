import unittest
import json

from gather import Gather
from postgres import Postgres

with open('db_auth.json') as auth_file:
    auth = json.load(auth_file)['postgres_dev']

pg = Postgres(auth)
#TODO: Move to test folder
#TODO: test_insert_data_omdb fails
class TestGather(unittest.TestCase):

    def setUp(self):
        self.get = Gather(auth)
        pg.pg_cur.execute("delete from gather.kino_movies")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt4285496')")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt2562232')")
        pg.pg_cur.execute("insert into gather.kino_movies values ('tt0245712')")
        pg.pg_conn.commit()

        self.omdb_tables = ['omdb_cast', 'omdb_crew', 'omdb_main', 'omdb_ratings']

    def tearDown(self):
        pg.pg_cur.execute("delete from gather.kino_movies where imdb_id = 'tt4285496'")
        pg.pg_cur.execute("delete from gather.kino_movies where imdb_id = 'tt2562232'")
        pg.pg_cur.execute("delete from gather.kino_movies where imdb_id = 'tt0245712'")
        pg.pg_conn.commit()


    def test_get_imdb_ids_omdb(self):
        omdb = self.get.apis[0]
        imdb_ids = self.get.get_imdb_ids(omdb)
        self.assertEqual(sorted(imdb_ids), ['tt0245712', 'tt2562232', 'tt4285496'])

    def test_get_movie_data_omdb(self):
        omdb = self.get.apis[0]
        data = self.get.get_movie_data(omdb, 'tt4285496')
        dict_keys = sorted(list(data.keys()))
        self.assertEqual(dict_keys, self.omdb_tables )
        for key in dict_keys:
            sql = "select column_name from information_schema.columns where table_name = %s and column_name <> 'tstamp'"
            pg.pg_cur.execute(sql, (key,))
            table_columns = [ e[0] for e in pg.pg_cur.fetchall() ]
            table_keys = [e.lower() for e in data[key][0].keys()]
            self.assertEqual(sorted(table_keys), sorted(table_columns))

    def test_insert_data_omdb(self):
        omdb = self.get.apis[0]
        data = self.get.get_movie_data(omdb, 'tt4285496')
        self.get.insert_data(data)
        dict_keys = sorted(list(data.keys()))
        for key in dict_keys:
            sql = 'select count(*) from {0}.{1}'.format('gather', key)
            pg.pg_cur.execute(sql)
            table_count = pg.pg_cur.fetchall()
            print(table_count)

    def test_update_gather_table_omdb(self):
        omdb = self.get.apis[0]
        self.get.update_gather_table(omdb)
        for table_name in self.omdb_tables:
            sql = 'select imdbid from {0} group by imdbid'.format(table_name)
            pg.pg_cur.execute(sql)
            imdb_ids = [ e[0] for e in pg.pg_cur.fetchall() ]
            self.assertEqual(imdb_ids,  ['tt0245712', 'tt2562232', 'tt4285496'])
            sql = 'delete from {0}'.format(table_name)
            pg.pg_cur.execute(sql)

            #def do the same with youtube_films
            #change api so that api takes a dictionary of what it needs
            # learn how to commit
            # then i can commit mine
            # joe - jenkins project to deploy everything stuff
            # rob - implement tmdb and guidebox into gather /test
            # talk about a scheduler.
            # how do we deal with bad imdb_ids, maybe a not found table?
            # talk over gather
            # compile jenkins project locally

            # talk about what is next?
























