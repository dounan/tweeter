from mysql_tweets import MysqlTweets
from ngram_kneser_ney import NgramKneserNey
from sentence_generator import SentenceGenerator

N = 4

t = MysqlTweets()
kn = NgramKneserNey(N)
print "Getting sentences"
sentences = t.get_more_sentences(100000)
print "Training model"
kn.train(sentences)
generator = SentenceGenerator(kn)
for i in range(20):
  print "======="
  print " ".join(generator.generate_sentence(N))
