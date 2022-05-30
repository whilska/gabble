from hilskapy.commons.logger import Logger
from hilskapy.commons.configparsing import AppConfig
from gabble.wordloader import WordLoader
from enum import Enum
import sys


class WordGameLetterType(Enum):

	GREEN = 'G'
	YELLOW = 'Y'
	BLACK = 'B'


class WordGameLetter:

	def __init__(self, letter_type: WordGameLetterType, letter: str):
		self.letter_type = letter_type
		self.letter = letter

	@classmethod
	def get_letter(cls, answer, correct_answer, i):
		letter = answer[i]
		correct_letter = correct_answer[i]
		if letter == correct_letter:
			return WordGameLetter(WordGameLetterType.GREEN, letter)
		elif letter in correct_answer:
			return WordGameLetter(WordGameLetterType.YELLOW, letter)
		else:
			return WordGameLetter(WordGameLetterType.BLACK, letter)

	def get_letter_for_board_txt(self):
		if self.letter_type == WordGameLetterType.GREEN:
			return '[' + self.letter + ']'
		elif self.letter_type == WordGameLetterType.YELLOW:
			return '(' + self.letter + ')'
		return self.letter


class WordGameRow:

	def __init__(self, answer: str, letters: [WordGameLetter]):
		self.answer = answer
		self.letters = letters

	@classmethod
	def get_row(cls, answer, correct_answer):
		return WordGameRow(answer, [WordGameLetter.get_letter(answer, correct_answer, i) for i in range(len(answer))])


class WordGameBoard:

	rows: [WordGameRow]

	def __init__(self, correct_answer):
		self._correct_answer = correct_answer
		self.rows = []

	def add_row(self, answer):
		self.rows.append(WordGameRow.get_row(answer, self._correct_answer))


class WordGameAnswer(Enum):

	RIGHT_ANSWER = 1
	INVALID_ANSWER = 0
	WRONG_ANSWER = -1
	GAME_OVER = -2


class WordGame:

	MAX_TURNS = 6
	previous_guesses: [str]
	game_board: WordGameBoard

	def __init__(self, answer: str):
		self.log = Logger.get_logger(self.__class__.__name__)
		self._answer = self._format_answer(answer)
		self.log.debug('Answer set to {0}'.format(self._answer))
		self.turns_left = self.MAX_TURNS
		self.previous_guesses = []
		self.game_board = WordGameBoard(self._answer)

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
			self.game_board.add_row(answer)
			return WordGameAnswer.WRONG_ANSWER
		return WordGameAnswer.INVALID_ANSWER

	def get_game_board(self):
		return self.game_board

	def get_game_board_txt(self):
		rows = []
		for i in self.game_board.rows:
			rows.append(','.join(n.get_letter_for_board_txt() for n in i.letters))
		return '\n'.join(rows)

	def get_correct_answer(self):
		return self._answer

	def get_no_of_turns(self):
		return self.MAX_TURNS - self.turns_left

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
	print('Correct letters will be wrapped in square brackets: [A]')
	print('Letters in incorrect positions will be wrapped in parentheses: (B)')
	print('Incorrect letters will appear normally')
	print('**********')
	while not (answer == WordGameAnswer.RIGHT_ANSWER or answer == WordGameAnswer.GAME_OVER):
		if len(word_game.previous_guesses) > 0:
			print('Your previous tries ({0}):'.format(str(len(word_game.previous_guesses))))
			print('**********')
			print(word_game.get_game_board_txt())
			print('**********')
		response = input('Enter your next guess: ')
		answer = word_game.take_turn(response)
		if answer == WordGameAnswer.INVALID_ANSWER:
			print('Sorry, {0} is not a valid word'.format(response))
	if answer == WordGameAnswer.RIGHT_ANSWER:
		print('Congratulations you won! {0} was the correct answer'.format(word_game.get_correct_answer().upper()))
		print('You reached the correct answer in {0} tries'.format(word_game.get_no_of_turns()))
	else:
		print('Sorry, you lost. {0} was the correct answer'.format(word_game.get_correct_answer()))


if __name__ == '__main__':
	config_path = sys.argv[1]
	AppConfig.instance(config_path)
	Logger.set_logger_level_from_config(AppConfig.get_attr('Logging.logger_level'))
	play_word_game(AppConfig.get_attr('WordGame.answer'))
