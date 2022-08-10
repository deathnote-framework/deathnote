def array_integer(shellcode):
	listToStr = ', '.join([str(elem) for elem in shellcode])
	return '[{}]'.format(listToStr)	
