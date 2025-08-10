from processes.config import Config
from processes.gather import get_film

from processes.postgres import Postgres

config = Config.from_env(".env")
pg = Postgres(config.DB_SERVER, config.DB_PORT, config.DB_DATABASE, config.DB_USER, config.DB_PASSWORD)


def get_imdb_ids_to_fetch():
    sql = """select distinct f.imdb_id
               from movies2festivals f
               left join movies m
                 on f.imdb_id = m.imdb_id
               left join errored e
                 on f.imdb_id = e.imdb_id
              where e.imdb_id is null 
                and m.imdb_id is null"""
    pg.pg_cur.execute(sql)
    return [e[0] for e in pg.pg_cur.fetchall()]

def get_films():
    new_films_count = 0
    all_films_count = 0
    error_films_count = 0
    imdb_ids = get_imdb_ids_to_fetch()
    for i in imdb_ids:
        all_films_count += 1
        response = get_film(i)
        if "error_message" in response:
            if "The request cannot be completed because you have exceeded your" in response['error_message']:
                print("QUOTA REACHED")
                return
            else:
                error_films_count += 1
                print(f"{i} - ERROR: {response['error_message']}")
        else:
            new_films_count += 1
            print(f"{i} - SUCCESS")


if __name__ == '__main__':
    get_films()
    # print(get_film('tt23143494'))