from collections import Counter
from collections import defaultdict
import pprint

DEBUG = False
pp = pprint.PrettyPrinter()

class NgramKneserNey:

  START = "<START>"
  STOP = "<STOP>"

  def __init__(self, max_n):
    """
    max_n must be greater than or equal to 2.
    """
    self._max_n = max_n

    # Maps {n: {ngram_prefix: word_counts}}
    #    ngram_prefix is a tuple of words.
    #    word_counts is a Counter of word to count.
    self._ngram_word_counts_map = {}

    # Used to calculate the continuation counts.
    # For each n, maps a word to a set of ngram_prefix that preceed it.
    # Maps {n: {word: set(ngram_prefix)}}
    self._continuations_map = {}

    # Used to normalize continuation counts into a probability.
    # Maps {n: set(ngram)}
    self._ngrams_map = {}

    # Maps {order: discount}
    # TODO(dounanshi): calculate discount http://www.riacs.edu/research/technical_reports/TR_pdf/TR_00.07.pdf
    self._discount_map = {1: .75, 2: .75, 3: .75}

    # Initialize maps.
    for i in range(max_n):
      n = i + 1
      self._ngram_word_counts_map[n] = defaultdict(Counter)
      self._continuations_map[n] = defaultdict(set)
      self._ngrams_map[n] = set()

    # Maps {ngram_prefix: count}
    self._prefix_count_cache = {}
    # Maps {ngram_prefix: (n1, n2, n3)}
    self._nvals_cache = {}

  def train(self, sentences):
    """
    sentence is a list of strings.
    """
    # Clear caches
    self._prefix_count_cache = {}
    self._nvals_cache = {}

    for sentence in sentences:
      sentence = sentence + [self.STOP]

      for i in range(self._max_n):
        n = i + 1
        ngram_word_counts = self._ngram_word_counts_map[n]
        continuations = self._continuations_map[n]
        ngrams = self._ngrams_map[n]
        ngram_prefix = (self.START,) * (n - 1)

        for word in sentence:
          ngram_word_counts[ngram_prefix][word] += 1
          continuations[word].add(ngram_prefix)
          ngrams.add(ngram_prefix + (word,))

          # Advance the ngram_prefix.
          if len(ngram_prefix) > 0: ngram_prefix = ngram_prefix[1:] + (word,)

  def get_unigrams(self):
    return self._ngrams_map[1]

  def get_word_probability(self, ngram_prefix, word):
    n = len(ngram_prefix) + 1

    if n == 1:
      return self._get_continuation_probability(word)   

    c_total = self._get_prefix_count(n, ngram_prefix)
    prev_p = self.get_word_probability(ngram_prefix[1:], word)

    if c_total == 0:
      # TODO(dounanshi): not quite sure what to do in this case
      return prev_p

    c = self._get_ngram_count(n, ngram_prefix, word)
    discount = self._get_discount(c)
    c_star = max(c - discount, 0)
    gamma = self._get_gamma(n, ngram_prefix)
    return float(c_star) / c_total + gamma * prev_p

  def _get_prefix_count(self, n, ngram_prefix):
    # Simple cache.
    if ngram_prefix not in self._prefix_count_cache:
      c = sum(self._ngram_word_counts_map[n][ngram_prefix].values())
      self._prefix_count_cache[ngram_prefix] = c
    # Return cached value.
    return  self._prefix_count_cache[ngram_prefix]

  def _get_ngram_count(self, n, ngram_prefix, word):
    return self._ngram_word_counts_map[n][ngram_prefix][word]

  def _get_discount(self, count):
    if count == 0:
      return 0
    elif count == 1:
      return self._discount_map[1]
    elif count == 2:
      return self._discount_map[2]
    else:
      return self._discount_map[3]

  def _get_gamma(self, n, ngram_prefix):
    # Simple cache.
    if ngram_prefix not in self._nvals_cache:
      word_counts = self._ngram_word_counts_map[n][ngram_prefix]
      n1 = len([v for v in word_counts.values() if v == 1])
      n2 = len([v for v in word_counts.values() if v == 2])
      n3 = len([v for v in word_counts.values() if v > 2])
      self._nvals_cache[ngram_prefix] = (n1, n2, n3)
    else:
      n1, n2, n3 = self._nvals_cache[ngram_prefix]
    d1 = self._discount_map[1]
    d2 = self._discount_map[2]
    d3 = self._discount_map[3]
    return (d1 * n1 + d2 * n2 + d3 * n3) / self._get_prefix_count(n, ngram_prefix)

  # Unigram probability
  def _get_continuation_probability(self, word):
    return float(len(self._continuations_map[2][word])) / len(self._ngrams_map[2])


# Test the class a little
if __name__ == '__main__':
  sentences = [
    "this is a test sentence".split(),
    "this is another test sentence that is different".split(),
    "this one is a different sentence".split()
  ]
  kn = NgramKneserNey(4)
  kn.train(sentences)
  print kn.get_word_probability(("this",), "is")
