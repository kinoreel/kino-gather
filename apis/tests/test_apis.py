import unittest
import json

from apis.get_youtube import GetAPI as yt
from apis.get_omdb import GetAPI as omdb
from apis.get_tmdb import GetAPI as tmdb
from apis.get_itunes import GetAPI as itunes


class TestApis(unittest.TestCase):
    """Integration testing"""
    @classmethod
    def setUpClass(cls):
        cls.yt = yt()
        cls.omdb = omdb()
        cls.tmdb = tmdb()
        cls.itunes = itunes()
        cls.imdb_ids = ['tt5278596', 'tt5278596', 'tt5278460', 'tt5278462', 'tt4632316', 'tt5278464', 'tt5246328', 'tt5278466', 'tt5278592', 'tt5278592', 'tt5278598', 'tt5278598', 'tt3917210', 'tt5278578', 'tt5278578', 'tt5236900', 'tt5236900', 'tt4086024', 'tt4086024', 'tt5278458', 'tt5259692', 'tt2634548', 'tt5278928', 'tt5072370', 'tt5146068', 'tt4079902', 'tt5261818', 'tt5261818', 'tt5278930', 'tt2338774', 'tt2338774', 'tt5278868', 'tt5278868', 'tt5278914', 'tt5278914', 'tt5278506', 'tt4835086', 'tt5278932', 'tt5278932', 'tt4365518', 'tt4365518', 'tt3521306', 'tt3544218', 'tt5278836', 'tt5278836', 'tt5240748', 'tt5105218', 'tt5105218', 'tt3777860', 'tt3777860', 'tt3826628', 'tt3826628', 'tt4650738', 'tt5278850', 'tt5278850', 'tt5278832', 'tt4071086', 'tt4196450', 'tt4444438', 'tt4444438', 'tt4666726', 'tt3958780', 'tt4437216', 'tt4661798', 'tt4305148', 'tt3652862', 'tt4158876', 'tt4258698', 'tt5254640', 'tt4034354', 'tt1639084', 'tt3517044', 'tt4872078', 'tt4129870', 'tt5259692', 'tt5278458', 'tt5278932', 'tt5278932', 'tt5278836', 'tt5278832', 'tt4444438', 'tt4444438', 'tt5254640', 'tt3652862', 'tt4872078', 'tt3917210', 'tt5146068', 'tt3544218', 'tt4034354', 'tt2338774', 'tt2338774', 'tt3652862', 'tt5278466', 'tt5278928', 'tt5278836', 'tt5278836', 'tt4196450', 'tt4262174', 'tt4262174', 'tt5278214', 'tt5281134', 'tt5225338', 'tt4238858', 'tt4238858', 'tt5280984', 'tt4734132', 'tt5164412', 'tt5164412', 'tt3776826', 'tt4573516', 'tt5004252', 'tt4285496', 'tt4285496', 'tt5236900', 'tt5236900', 'tt4835086', 'tt5278592', 'tt5278592', 'tt3826628', 'tt3826628', 'tt5087064', 'tt4775726', 'tt4775726', 'tt4554344', 'tt4554344', 'tt4918278', 'tt4918278', 'tt4513008', 'tt5120094', 'tt5375434', 'tt5375434', 'tt5116560', 'tt5116560', 'tt5126872', 'tt5126872', 'tt5262444', 'tt5262444', 'tt5001224', 'tt4805832', 'tt5424742', 'tt4775726', 'tt4775726', 'tt5424802', 'tt5039924', 'tt5027506', 'tt5027506', 'tt4702552', 'tt4384832', 'tt4384832', 'tt4396330', 'tt4396330', 'tt5424964', 'tt5258442', 'tt5424972', 'tt4608516', 'tt4608516', 'tt5142310', 'tt5142310', 'tt5113262', 'tt5113262', 'tt5144102', 'tt5144102', 'tt5120094', 'tt4523534', 'tt4523534', 'tt4992136', 'tt5127444', 'tt5425050', 'tt5425066', 'tt5425066', 'tt4554344', 'tt4554344', 'tt5425086', 'tt5249484', 'tt4513008', 'tt5347340', 'tt4421754', 'tt4450308', 'tt4450308', 'tt4417314', 'tt4417314', 'tt4982454', 'tt4982454', 'tt5020232', 'tt5020232', 'tt4991570', 'tt4641652', 'tt4641652', 'tt4516050', 'tt4516050', 'tt5433902', 'tt5302670', 'tt5433940', 'tt5134912', 'tt5134912', 'tt5143976', 'tt5127958', 'tt4422282', 'tt4422282', 'tt4918278', 'tt4918278', 'tt5246722', 'tt5246722', 'tt5434050', 'tt5434050', 'tt4860694', 'tt4860694', 'tt5434060', 'tt5434060', 'tt4860346', 'tt5089600', 'tt5089600', 'tt5087064', 'tt4671082', 'tt4671082', 'tt5078874', 'tt4919714', 'tt4933584', 'tt4933584', 'tt4636194', 'tt4636194', 'tt5340864', 'tt5340864', 'tt4419744', 'tt5140514', 'tt5140514', 'tt5291650', 'tt4248458']

    def test_2(self):
        for i in self.imdb_ids:
            print ('\n   Getting '+i)
            try:
                request = {'imdb_id': i}
                data = self.omdb.get_info(request)
                print(data['omdb_main'][0]['title'])
                request.update(data)
                data = self.tmdb.get_info(request)
                request.update(data)
                data = self.itunes.get_info(request)
                if data is not None:
                    request.update(data)
                data = self.yt.get_info(request)
                request.update(data)
                # compare cast
                tmdb_cast = [e['name'] for e in request['tmdb_cast'] if e['cast_order'] < 5]
                print(request['tmdb_trailer'])
                sorted(tmdb_cast)
                print(tmdb_cast)
                # compare title
                omdb_title = request['omdb_main'][0]['title']
                print(omdb_title)
                tmdb_plot = request['tmdb_main'][0]['plot']
                print(tmdb_plot)
            except:
                continue





if __name__=='__main__':
    unittest.main()


