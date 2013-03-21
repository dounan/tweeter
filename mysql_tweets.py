import MySQLdb as mdb
from happyfuntokenizing import Tokenizer

class MysqlTweets:

  def __init__(self):
    self._mysql = mdb.connect('localhost', 'root', '', 'tweeter_development')
    self._tokenizer = Tokenizer(preserve_case=False)
    self._offset = 0

  def get_more_sentences(self, limit=100000):
    """
    Returns:
      A generator for sentences (list of strings) that will generate at most
      limit number of sentences.
    """
    # Grab the db cursor to the tweets.
    try:
      cursor = self._mysql.cursor()
      cursor.execute("SELECT text FROM crawl_tweet LIMIT %d OFFSET %d;" % (limit, self._offset))
      row = cursor.fetchone()
      while row:
        self._offset += 1
        yield self._tokenizer.tokenize(row[0])
        row = cursor.fetchone()
    except mdb.Error, e:
      print "Error %d: %s" % (e.args[0], e.args[1])
