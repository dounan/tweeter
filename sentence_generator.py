from ngram_kneser_ney import NgramKneserNey
import random

class SentenceGenerator:

  def __init__(self, model):
    """
    model needs to have the following methods:
        get_unigrams()
        get_word_probability(ngram_prefix, word)
    """
    self._model = model

  def generate_sentence(self, n, word_limit=50):
    sentence = []
    ngram_prefix = (NgramKneserNey.START,) * (n - 1)
    word = self._generate_word(ngram_prefix)
    while len(sentence) < word_limit and not word == NgramKneserNey.STOP:
      sentence.append(word)
      if len(ngram_prefix) > 0: ngram_prefix = ngram_prefix[1:] + (word,)
      word = self._generate_word(ngram_prefix)
    return sentence

  def _generate_word(self, ngram_prefix):
    sample = random.random()
    aggregate = 0
    for word, in self._model.get_unigrams():
      aggregate += self._model.get_word_probability(ngram_prefix, word)
      if aggregate >= sample: return word
    raise "Error generating a word for prefix " + str(ngram_prefix)


# Test the class a little
if __name__ == '__main__':
  sentences = [
    "this is a test sentence".split(),
    "this is another test sentence that is different".split(),
    "this one is a different sentence".split()
  ]
  max_n = 4
  kn = NgramKneserNey(max_n)
  kn.train(sentences)

  sg = SentenceGenerator(kn)
  n = 3
  print sg.generate_sentence(n)
