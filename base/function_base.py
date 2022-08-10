from base.exceptions import MaxLengthException
from core.utils.printer import *
import string
import random

def pattern_create(length: int):
	try:
		if int(length) >= 20280:
				raise MaxLengthException('ERROR: Pattern length exceeds ' 'maximum of 20280')

		pattern = ''
		for upper in string.ascii_uppercase:
			for lower in string.ascii_lowercase:
				for digit in string.digits:
					if len(pattern) < int(length):
						pattern += upper+lower+digit
					else:
						out = pattern[:int(length)]
						return out
	except (ValueError, TypeError) as e:
		print_error("Must be integer")
		return

def pattern_research(pattern):
	try:
		if pattern.startswith('0x'):
			pattern = pattern[2:]
			pattern = bytearray.fromhex(pattern).decode('ascii')
			pattern = pattern[::-1]
	except (ValueError, TypeError) as e:
		raise
	haystack = ''
	for upper in string.ascii_uppercase:
		for lower in string.ascii_lowercase:
			for digit in string.digits:
				haystack += upper+lower+digit
				found_at = haystack.find(pattern)
				if found_at > -1:
					return found_at							
	return

def random_text(length: int, alph: str = string.ascii_letters):

	return "".join(random.choice(alph) for _ in range(length))