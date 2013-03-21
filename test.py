from mysql_tweets import MysqlTweets
from ngram_kneser_ney import NgramKneserNey
from sentence_generator import SentenceGenerator
from happyfuntokenizing import Tokenizer
import twokenize

N = 3

# tokenize = Tokenizer(preserve_case=False).tokenize
tokenize = twokenize.tokenize


t = MysqlTweets(tokenize)
kn = NgramKneserNey(N)
print "Getting sentences"
sentences = t.get_more_sentences(1000)
print "Training model"
kn.train(sentences)
generator = SentenceGenerator(kn)
for i in range(20):
  print "======="
  print " ".join(generator.generate_sentence(N))
