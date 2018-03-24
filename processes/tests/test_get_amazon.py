import unittest
import os
import sys
import re
from bs4 import BeautifulSoup

current_dir = (os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(current_dir, '..', '..'))

from processes.get_amazon import Main, RequestAPI, StandardiseResponse, ChooseBest


class TestMain(unittest.TestCase):
    """Testing RequestAPI"""
    @classmethod
    def setUpClass(cls):
        cls.main = Main()

    def test_get_info(self):
        request = {'imdb_id': 'tt0083658',
                   'tmdb_main': [{'title': 'Lion', 'runtime': 118, 'release_date': '2017-05-15'}]}
        result = self.main.run(request)
        expected = {
            'amazon_main': [{
                'imdb_id': 'tt0083658',
                'binding': 'Amazon Video',
                'title': 'Lion',
                'currency': 'GBP',
                'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF',
                'runtime': 118,
                'price': 9.99,
                'released': '2017-05-15',
                'productType': 'DOWNLOADABLE_MOVIE'
            }]
        }
        self.assertEqual(result, expected)

    def test_get_info_bad(self):
        request = {'imdb_id': 'tt0083658',
                   'tmdb_main': [{'title': 'Blah blah blha I do not exist', 'runtime': 500, 'release_date': '1990-05-15'}]}
        result = self.main.run(request)
        expected = {
            'amazon_main': []
        }
        self.assertEqual(result, expected)


class TestRequestAPI(unittest.TestCase):
    """Testing class RequestAPI"""

    @classmethod
    def setUpClass(cls):
        cls.request = RequestAPI()

    def test_get_signature(self):
        url_params = 'AWSAccessKeyId=AKIAJCZNP6FPLXEFGTRA&AssociateTag=kinoproject-21&Keywords=Lion&Operation=ItemSearch&ResponseGroup=Images%2CItemAttributes%2COffers&SearchIndex=All&Service=AWSECommerceService&Timestamp=2018-03-23T23%3A06%3A19.000Z'
        secret_key = 'Dq81jlr+Q/oEb2micJUEwq4kFvXn2EKkJJDrY7cc'
        result = self.request.get_signature(url_params, secret_key)
        expected = b'fHqjFMbHLH0LihuJpfE3qTG1D0ORmeaIF8eRqrW6Jpg='
        self.assertEqual(result, expected)

    def test_get_timestamp(self):
        result = self.request.get_timestamp()
        self.assertTrue(re.match('\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{5}', result))

    def test_rfc_3986_encode(self):
        result = self.request.rfc_3986_encode('2018-03-23T19:12:49.000Z')
        expected = '2018-03-23T19%3A12%3A49.000Z'
        self.assertEqual(result, expected)

    def test_get_amazon(self):
        # Very lazy test, checking that we do not error
        self.request.get_amazon('Lion')


class TestAmazonItem(unittest.TestCase):
    """Testing the class AmazonItem"""

    @classmethod
    def setUpClass(cls):
        cls.api_response = '''<?xml version="1.0"?>
            <ItemSearchResponse xmlns="http://webservices.amazon.com/AWSECommerceService/2011-08-01">
              <Items>
                <Item>
                  <ASIN>B06XPMT8FF</ASIN>
                  <DetailPageURL>https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&amp;tag=kinoproject-21&amp;linkCode=xm2&amp;camp=2025&amp;creative=165953&amp;creativeASIN=B06XPMT8FF</DetailPageURL>
                  <ItemAttributes>
                    <Actor>Dev Patel</Actor>
                    <Actor>Rooney Mara</Actor>
                    <Actor>Nicole Kidman</Actor>
                    <Actor>David Wenham</Actor>
                    <Actor>Sunny Pawar</Actor>
                    <AudienceRating>Parental Guidance</AudienceRating>
                    <Binding>Amazon Video</Binding>
                    <Creator Role="Writer">Luke Davies</Creator>
                    <Director>Garth Davis</Director>
                    <Genre>drama &gt; based-on-a-true-story</Genre>
                    <ListPrice>
                      <Amount>999</Amount>
                      <CurrencyCode>GBP</CurrencyCode>
                      <FormattedPrice>&#xA3;9.99</FormattedPrice>
                    </ListPrice>
                    <ProductGroup>Movie</ProductGroup>
                    <ProductTypeName>DOWNLOADABLE_MOVIE</ProductTypeName>
                    <ReleaseDate>2017-05-15</ReleaseDate>
                    <RunningTime Units="minutes">118</RunningTime>
                    <Studio>Entertainment Film Distributors</Studio>
                    <Title>Lion</Title>
                  </ItemAttributes>
                </Item>
                <Item>
                  <ASIN>B01N38EP0Z</ASIN>
                  <DetailPageURL>https://www.amazon.co.uk/Lion-DVD-Garth-Davis/dp/B01N38EP0Z?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&amp;tag=kinoproject-21&amp;linkCode=xm2&amp;camp=2025&amp;creative=165953&amp;creativeASIN=B01N38EP0Z</DetailPageURL>
                  <ItemAttributes>
                    <AudienceRating>To Be Announced</AudienceRating>
                    <Binding>DVD</Binding>
                    <Director>Garth Davis</Director>
                    <Label>Entertainment in Video</Label>
                    <ProductGroup>DVD</ProductGroup>
                    <ProductTypeName>ABIS_DVD</ProductTypeName>
                    <ReleaseDate>2017-05-22</ReleaseDate>
                    <RunningTime Units="minutes">114</RunningTime>
                    <Studio>Entertainment in Video</Studio>
                    <Title>Lion [DVD]</Title>
                  </ItemAttributes>
                </Item>
              </Items>
            </ItemSearchResponse>'''
        cls.standardise = StandardiseResponse(cls.api_response)

    def test_standardise(self):
        result = self.standardise.standardise()
        expected = [{
            'currency': 'GBP',
            'binding': 'Amazon Video',
            'price': 9.99,
            'title': 'Lion',
            'runtime': 118,
            'released': '2017-05-15',
            'productType': 'DOWNLOADABLE_MOVIE',
            'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF'
        }, {
            'currency': None,
            'binding': 'DVD',
            'price': None,
            'title': 'Lion [DVD]',
            'runtime': 114,
            'released': '2017-05-22',
            'productType': 'ABIS_DVD',
            'url': 'https://www.amazon.co.uk/Lion-DVD-Garth-Davis/dp/B01N38EP0Z?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B01N38EP0Z'
        }]
        self.assertEqual(result, expected)

    def test_get_main_data(self):
        item  = """
            <item>
              <asin>B00EU76BSE</asin>
              <detailpageurl>https://www.amazon.co.uk/Due-Date-Zach-Galifianakis/dp/B00EU76BSE?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&amp;tag=kinoproject-21&amp;linkCode=xm2&amp;camp=2025&amp;creative=165953&amp;creativeASIN=B00EU76BSE</detailpageurl>
              <itemattributes>
                <actor>Zach Galifianakis</actor>
                <actor>Robert Downey Jr.</actor>
                <actor>Juliette Lewis</actor>
                <actor>Michelle Monaghan</actor>
                <actor>Jamie Foxx</actor>
                <audiencerating>Suitable for 15 years and over</audiencerating>
                <binding>Amazon Video</binding>
                <director>Todd Phillips</director>
                <genre>Comedy</genre>
                <isadultproduct>0</isadultproduct>
                <listprice>
                  <amount>599</amount>
                  <currencycode>GBP</currencycode>
                  <formattedprice>&#xA3;5.99</formattedprice>
                </listprice>
                <productgroup>Movie</productgroup>
                <producttypename>DOWNLOADABLE_MOVIE</producttypename>
                <releasedate>2014-02-26</releasedate>
                <runningtime units="minutes">95</runningtime>
                <title>Due Date</title>
              </itemattributes>
            </item>"""
        item = BeautifulSoup(item, "html.parser")
        result = self.standardise.get_main_data(item)
        expected = {
            'released': '2014-02-26',
            'url': 'https://www.amazon.co.uk/Due-Date-Zach-Galifianakis/dp/B00EU76BSE'
                   '?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025'
                   '&creative=165953&creativeASIN=B00EU76BSE',
            'price': 5.99,
            'runtime': 95,
            'title': 'Due Date',
            'productType': 'DOWNLOADABLE_MOVIE',
            'currency': 'GBP',
            'binding': 'Amazon Video'
        }
        self.assertEqual(result, expected)


class TestChooseBest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.data = [{
            'currency': 'GBP',
            'binding': 'Amazon Video',
            'price': 9.99,
            'title': 'Lion',
            'runtime': 118,
            'released': '2017-05-15',
            'productType': 'DOWNLOADABLE_MOVIE',
            'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF'
        }, {
            'currency': 'GBP',
            'binding': 'Amazon Video',
            'price': 2.99,
            'title': 'Bad Choice',
            'runtime': 118,
            'released': '2017-05-15',
            'productType': 'DOWNLOADABLE_MOVIE',
            'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF'
        }, {
            'currency': None,
            'binding': 'DVD',
            'price': None,
            'title': 'Lion [DVD]',
            'runtime': 114,
            'released': '2017-05-22',
            'productType': 'ABIS_DVD',
            'url': 'https://www.amazon.co.uk/Lion-DVD-Garth-Davis/dp/B01N38EP0Z?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B01N38EP0Z'
        }]

    def test_get_best_match(self):
        result = ChooseBest.get_best_match(self.data, 'Lion', 118,'2017-05-15')
        expected = {
            'currency': 'GBP',
            'binding': 'Amazon Video',
            'price': 9.99,
            'title': 'Lion',
            'runtime': 118,
            'released': '2017-05-15',
            'productType': 'DOWNLOADABLE_MOVIE',
            'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF'
        }
        self.assertEqual(result, expected)

        # If we remove the good answer we expect to return None, as no item is acceptable
        result = ChooseBest.get_best_match(self.data[1:], 'Lion', 118, '2017-05-15')
        self.assertIsNone(result)

    def test_get_amazon_video_products(self):
        result = ChooseBest.get_amazon_video_products(self.data)
        expected = [{
            'currency': 'GBP',
            'binding': 'Amazon Video',
            'price': 9.99,
            'title': 'Lion',
            'runtime': 118,
            'released': '2017-05-15',
            'productType': 'DOWNLOADABLE_MOVIE',
            'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF'
        }, {
            'currency': 'GBP',
            'binding': 'Amazon Video',
            'price': 2.99,
            'title': 'Bad Choice',
            'runtime': 118,
            'released': '2017-05-15',
            'productType': 'DOWNLOADABLE_MOVIE',
            'url': 'https://www.amazon.co.uk/Lion-Dev-Patel/dp/B06XPMT8FF?SubscriptionId=AKIAJCZNP6FPLXEFGTRA&tag=kinoproject-21&linkCode=xm2&camp=2025&creative=165953&creativeASIN=B06XPMT8FF'
        }]
        self.assertEqual(result, expected)

    def test_get_match_score(self):
        score = ChooseBest.get_match_score('Blade Runner', 117, '2016-07-03', 'Blade Runner', 117, '2016-02-19')
        self.assertEqual(score, 100)
        score = ChooseBest.get_match_score('Blade Runner', 117, '2016-07-03', 'Blade Runner 2049', 164, '2016-02-19')
        self.assertEqual(score, 36)
        score = ChooseBest.get_match_score('Jaws', 124, '2016-07-03', 'Jaws 2', 116, '2016-02-19')
        self.assertEqual(score, 72)

    def test_get_title_score(self):
        score = ChooseBest.get_title_score('Blade Runner', 'Blade Runner')
        self.assertEqual(score, 100)
        score = ChooseBest.get_title_score('Blade Runner', 'BLADE RUNNER')
        self.assertEqual(score, 100)
        score = ChooseBest.get_title_score('Blade Runner', 'Blade Runner 2049')
        self.assertEqual(score, 83)
        score = ChooseBest.get_title_score('Jaws', 'Jaws 2')
        self.assertEqual(score, 80)
        score = ChooseBest.get_title_score("Bill and Ted's Excellent Adventure", "Bill and Ted's Bogus Journey")
        self.assertEqual(score, 61)

    def test_get_runtime_score(self):
        score = ChooseBest.get_runtime_score(100, 200)
        self.assertEqual(score, 100)
        score = ChooseBest.get_runtime_score(200, 100)
        self.assertEqual(score, 100)

    def test_get_release_date_score(self):
        """Testing get_release_date"""
        # Upload date sooner than release date is a good score
        # return 0
        score = ChooseBest.get_release_date_score('2016-07-03', '2016-02-19')
        self.assertEqual(score, 0)
        score = ChooseBest.get_release_date_score('2016-01-01', '2017-01-11')
        self.assertEqual(score, 13)
