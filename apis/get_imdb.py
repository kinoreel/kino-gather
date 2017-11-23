import json

from kafka import KafkaProducer

from GLOBALS import KAFKA_BROKER

class PostIMDB(object):

    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)

    def push_imdb_id(self, imdb_id):
        data = {'imdb_id': imdb_id}
        self.producer.send('imdb_ids', json.dumps(data).encode())

if __name__=='__main__':
    imdb_ids = ['tt1065073', 'tt2321549', 'tt1490017', 'tt2582802', 'tt2872718', 'tt2382298', 'tt2473794', 'tt2802154', 'tt1706620', 'tt2425486', 'tt2737050', 'tt2015381', 'tt1877832', 'tt2278388', 'tt2576852', 'tt2567712', 'tt1935156', 'tt1865505', 'tt2852470', 'tt2103281', 'tt2364975', 'tt2718492', 'tt4044364', 'tt2084970', 'tt2901736', 'tt2359024', 'tt2326554', 'tt2305051', 'tt3263996', 'tt2405792', 'tt2267998', 'tt1843866', 'tt2350496', 'tt2639344', 'tt2692904', 'tt1646971', 'tt2121382', 'tt2714900', 'tt3169706', 'tt1605717', 'tt2920540', 'tt1385956', 'tt3103326', 'tt2340784', 'tt2245084', 'tt3279124', 'tt2301592', 'tt1600196', 'tt1100089', 'tt2852458', 'tt2910274', 'tt2234003', 'tt2235108', 'tt2013293', 'tt1684226', 'tt3129564', 'tt2741806', 'tt3268458', 'tt2187115', 'tt2392326', 'tt1972571', 'tt3089388', 'tt1441395', 'tt2911666', 'tt2406252', 'tt2883512', 'tt1714915', 'tt2852406', 'tt2784678', 'tt2737310', 'tt2980592', 'tt3091304', 'tt3654964', 'tt2420006', 'tt2174896', 'tt2294449', 'tt2382396', 'tt1571249', 'tt2524674', 'tt2043933', 'tt2389182', 'tt2732932', 'tt2932606', 'tt2652092', 'tt0469021', 'tt2967006', 'tt2331143', 'tt2375574', 'tt1951181', 'tt2866360', 'tt2758880', 'tt2562232', 'tt1816518', 'tt0115940', 'tt2178256', 'tt3230082', 'tt2400275']
    #imdb_ids = ['tt1441395']
    post = PostIMDB()
    for i in imdb_ids:
        post.push_imdb_id(i)
