import os
import sys
from time import sleep
import shutil

def pprint_dict_in_order(dictionary, order=None):
	""" Print dictionary in order. """
	order = order or ()

	def prettyprint(title, body):
		print_info("\n{}:".format(title.capitalize()))
		if not isinstance(body, str):
			for value_element in body:
				print_info("\t- ", value_element)
		else:
			print_info("- ",body)

	keys = list(dictionary.keys())
	for element in order:
		try:
			key = keys.pop(keys.index(element))
			value = dictionary[key]
		except (KeyError, ValueError):
			pass
		else:
			prettyprint(element, value)

	for rest_keys in keys:
		prettyprint(rest_keys, dictionary[rest_keys])

def color_blue(string):
	""" Returns string colored with blue """
	if os.name != 'nt':
		return "\033[94m{}\033[0m".format(string)
	return string

def color_green(string):
	""" Returns string colored with green """ 
	if os.name != 'nt':
		return "\033[92m{}\033[0m".format(string)
	return string

def color_red(string):
	""" Returns string colored with red """
	if os.name != 'nt':
		return "\033[91m{}\033[0m".format(string)
	return string

def color_orange(string):
	""" Returns string colored with orange """
	if os.name != 'nt':
		return "\033[93m{}\033[0m".format(string)
	return string

def print_error(*args, **kwargs):
	""" Print error message. """
	if os.name != 'nt':
		print(f"{color_red('[-]')}", *args, **kwargs)
	else:
		print('[-]',*args, **kwargs)

def print_warning(*args, **kwargs):
	""" Print warning message. """
	if os.name != 'nt':
		print(f"{color_orange('[!]')}", *args, **kwargs)
	else:
		print('[!]',*args, **kwargs)

def print_status(*args, **kwargs):
	""" Print status message. """
	if os.name != 'nt':
		print(f"{color_blue('[*]')}", *args, **kwargs)
	else:
		print('[*]', *args, **kwargs)

def print_success(*args, **kwargs):
	""" Print success message. """
	if os.name != 'nt':
		print(f"{color_green('[+]')}", *args, **kwargs)
	else:
		print('[+]',*args, **kwargs)

def print_info(*args, **kwargs):
	""" Print info message. """
	print(*args, **kwargs)


def print_no_chariot(*args, **kwargs):
	""" Print message without chariot. """
	print(*args, **kwargs, end='\r')

def print_slow(*args, **kwargs):
	for letter in args[0]:
		sys.stdout.write(letter)
		sys.stdout.flush()
		sleep(.007)

def print_table(headers, *args, **kwargs):
	""" Print table. """
	try:
		terminal_size = shutil.get_terminal_size()
		terminal_columns = terminal_size.columns
	except:
		terminal_columns = 80
	extra_fill = kwargs.get("extra_fill", 5)
	header_separator = kwargs.get("header_separator", "-")

	if not all(map(lambda x: len(x) == len(headers), args)):
		print_error(args)
		print_error("Headers and table rows tuples should be the same length.")
		return

	def custom_len(x):
		try:
			return len(x)
		except TypeError:
			return 0

	fill = []
	headers_line = '   '
	headers_separator_line = '   '
	for idx, header in enumerate(headers):
		column = [custom_len(arg[idx]) for arg in args]
		column.append(len(header))

		current_line_fill = max(column) + extra_fill
		fill.append(current_line_fill)
		headers_line = "".join((headers_line, "{header:<{fill}}".format(header=header, fill=current_line_fill)))
		headers_separator_line = "".join((
			headers_separator_line,
			"{:<{}}".format(header_separator * len(header), current_line_fill)
		))

	print_info()
	print_info(headers_line)
	print_info(headers_separator_line)
	for arg in args:
		content_line = "   "
		for idx, element in enumerate(arg):
			content_line = "".join((
				content_line,
				"{:<{}}".format(element, fill[idx])
			))
		print_info(content_line[:terminal_columns])

	print_info()
