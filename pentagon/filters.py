import re



def get_filters():
	"""Register a function with decorator"""
	registry = {}
	def registrar(func):
		registry[func.__name__] = func
		return func 
	registrar.all = registry
	return registrar


filter = get_filters()


@filter
def regex_trim(input, regex, replace=''):
	"""
	Trims or replaces the regex match in an input string.
	input (string): the input string to search for matches
	regex (string): regex to match
	replace (string - optional): a string to replace any matches with.  Defaults to trimming the match.
	"""
	return re.sub(regex, replace, input)





if __name__ == '__main__':
	for k,v in filter.all.items():
		print(v)
