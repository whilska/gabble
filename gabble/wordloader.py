import sys
from hilskapy.commons.logger import Logger
from hilskapy.commons.configparsing import AppConfig
from hilskapy.integrations.integration import Integration


class WordLoader:

	WORDS_URL = 'https://www.wordgamedictionary.com/word-lists/5-letter-words/5-letter-words.json'
	_words: [str] = []

	@classmethod
	def _get_words_url_data(cls):
		endpoint = Integration(cls.WORDS_URL, '', '')
		return endpoint.get()

	@classmethod
	def load_words(cls):
		log = Logger.get_logger(cls.__name__)
		data = cls._get_words_url_data()
		for i in data:
			cls._words.append(i['word'])
			log.trace('Adding word: ' + i['word'])
		log.debug('Finished adding {0} word(s)'.format(len(cls._words)))

	@classmethod
	def get_words(cls):
		return cls._words

	@classmethod
	def is_word_valid(cls, word: str):
		if len(cls._words) == 0:
			raise WordLoaderError('No words have been loaded')
		w = word.lower().strip()
		return any(w == i for i in cls._words)


class WordLoaderError(Exception):

	pass


if __name__ == '__main__':
	config_path = sys.argv[1]
	AppConfig.instance(config_path)
	Logger.set_logger_level_from_config(AppConfig.get_attr('Logging.logger_level'))
	# print(WordLoader.is_word_valid('Aside'))
	WordLoader.load_words()
	print(WordLoader.is_word_valid('Aside'))
