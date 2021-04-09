# C_teaching_assistant

# Some examples

Names of functions without comments

	query(info, transform = "name", grep = "not comment")

Names and comments of functions that return void and whose documentation has a @returns keyword

	query(info, transform = "[name, comment]", grep = "len(comment) > 0 and return == 'void' and '@returns' in comment")
	query(info, transform = "[name, comment]", grep = "comment and return == 'void' and '@returns' in comment")

Names and cyclometric complexity of the functions whose cyclomatic_complexity is above 10

	query(info, transform = "[name, cyclomatic_complexity]", grep = "cyclomatic_complexity > 10")

Names and cyclometric complexity of the functions whose maintainability_index is below 80

	query(info, transform = "[name, cyclomatic_complexity]", grep = "maintainability_index < 80")

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	query(info, transform = '[name, list(args.keys()), re.findall(r"@param\s+(\S+)", comment, re.M)]', grep = 'set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))')

The last example with output
	>>> query(info, transform = '[name, list(args.keys()), re.findall(r"@param\s+(\S+)", comment, re.M)]', grep = 'set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))')
	[['parse', ['line'], ['strtok', 'sobra', 'strtol']], ['main', [], ['BUFSIZ']], ['soma', ['s'], []], ['subtrai', ['s'], []], ['multiplica', ['s'], []], ['dividir', ['s'], []], ['decrementa', ['s'], []], ['incrementa', ['s'], []], ['modulo', ['s'], []], ['expoente', ['s'], []], ['e', ['s'], []], ['ou', ['s'], []], ['xorr', ['s'], []], ['nott', ['s'], []], ['PUSH', ['s', 'valor'], ['valor']], ['POP', ['s'], []], ['PRINT_STACK', ['s'], []]]

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	arg_doc_problems = lambda args, comment: set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))
	query(info, transform = '[name]', grep = "arg_doc_problems(args, comment)")

Output:
	['parse', 'main', 'soma', 'subtrai', 'multiplica', 'dividir', 'decrementa', 'incrementa', 'modulo', 'expoente', 'e', 'ou', 'xorr', 'nott', 'PUSH', 'POP', 'PRINT_STACK']
