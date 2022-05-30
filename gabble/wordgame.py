from hilskapy.commons.logger import Logger
from hilskapy.commons.configparsing import AppConfig
from gabble.wordloader import WordLoader
from enum import Enum
import sys


class WordGameAnswer(Enum):

	RIGHT_ANSWER = 1
	INVALID_ANSWER = 0
	WRONG_ANSWER = -1
	GAME_OVER = -2


class WordGame:

	MAX_TURNS = 6
	previous_guesses: [str]

	def __init__(self, answer: str):
		self.log = Logger.get_logger(self.__class__.__name__)
		self._answer = self._format_answer(answer)
		self.log.debug('Answer set to {0}'.format(self._answer))
		self.turns_left = self.MAX_TURNS
		self.previous_guesses = []

	def take_turn(self, answer: str):
		is_valid = WordLoader.is_word_valid(answer)
		if len(answer.strip()) != 5:
			return WordGameAnswer.INVALID_ANSWER
		if is_valid:
			self.turns_left -= 1
			if self._format_answer(answer) == self._answer:
				return WordGameAnswer.RIGHT_ANSWER
			if self.turns_left == 0:
				return WordGameAnswer.GAME_OVER
			self.previous_guesses.append(self._format_answer(answer))
			return WordGameAnswer.WRONG_ANSWER
		return WordGameAnswer.INVALID_ANSWER

	def get_game_board(self):
		rows = []
		for x in self.previous_guesses:
			row = x + ': '
			for i in range(len(x)):
				if x[i] == self._answer[i]:
					row += 'X'
				elif x[i] in self._answer:
					row += '?'
				else:
					row += '_'
			rows.append(row)
		return rows


	def get_correct_answer(self):
		return self._answer

	def _format_answer(self, answer: str):
		return answer.lower().strip()


class WordGameError(Exception):

	pass


def play_word_game(answer: str):
	WordLoader.load_words()
	if not WordLoader.is_word_valid(answer):
		raise WordGameError('Answer: {0} is not a valid word'.format(answer))
	word_game = WordGame(answer)
	answer = None
	print('**********')
	print('Welcome to Gabble!')
	while not (answer == WordGameAnswer.RIGHT_ANSWER or answer == WordGameAnswer.GAME_OVER):
		if len(word_game.previous_guesses) > 0:
			print('Your previous tries ({0}):'.format(str(len(word_game.previous_guesses))))
			print('**********')
			for i in word_game.get_game_board():
				print(i)
			print('**********')
		response = input('Enter your next guess: ')
		answer = word_game.take_turn(response)
		if answer == WordGameAnswer.INVALID_ANSWER:
			print('Sorry, {0} is not a valid word'.format(response))
	if answer == WordGameAnswer.RIGHT_ANSWER:
		print('Congratulation you won! {0} was the correct answer'.format(word_game.get_correct_answer()))
	else:
		print('Sorry, you lost. {0} was the correct answer'.format(word_game.get_correct_answer()))

if __name__ == '__main__':
	config_path = sys.argv[1]
	AppConfig.instance(config_path)
	Logger.set_logger_level_from_config(AppConfig.get_attr('Logging.logger_level'))
	play_word_game(AppConfig.get_attr('WordGame.answer'))
