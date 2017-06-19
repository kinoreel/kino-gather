create or replace function update_gather_tables() returns void as
$$

  import plpy
  from gather import Gather

  plan = plpy.prepare('select * from pg_settings where name = $1', ["text"])
  port = plpy.execute(plan, ['port'])[0]['setting']
  host = plpy.execute('select inet_server_addr()')[0]['inet_erver_addr']
  password = SOME ENVIRONEMNTAL VARIABLE PASSED IN BY JENKINS

  get = Gather(db=l_db,host=l_host)
  get.gather_new_kino_movies()

  return kino_db, host, port

$$ LANGUAGE plpython3u ;