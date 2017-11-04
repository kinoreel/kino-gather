

class GatherException(Exception):

    def __init__(self, imdb_id, message):
        self.message = message
        self.imdb_id = imdb_id
        super(GatherException, self).__init__(imdb_id, message)
