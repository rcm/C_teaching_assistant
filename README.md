# C_teaching_assistant

# Some examples

Names of functions without comments

	function_query(info, transform = "name", grep = "not comment")

Names and comments of functions that return void and whose documentation has a @returns keyword

	function_query(info, transform = "[name, comment]", grep = "len(comment) > 0 and return == 'void' and '@returns' in comment")
	function_query(info, transform = "[name, comment]", grep = "comment and return == 'void' and '@returns' in comment")

Names and cyclometric complexity of the functions whose cyclomatic_complexity is above 10

	function_query(info, transform = "[name, cyclomatic_complexity]", grep = "cyclomatic_complexity > 10")

Names and cyclometric complexity of the functions whose maintainability_index is below 80

	function_query(info, transform = "[name, cyclomatic_complexity]", grep = "maintainability_index < 80")
	tabfun.tabfun(["name cyclo maint".split()]  + function_query(info, transform = '[name, cyclomatic_complexity, maintainability_index]'), {1 : lambda x : tabfun.RED if x > 5 else tabfun.GREEN, 2 : lambda x: tabfun.RED if x < 80 else tabfun.GREEN})

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	function_query(info, transform = '[name, list(args.keys()), re.findall(r"@param\s+(\S+)", comment, re.M)]', grep = 'set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))')

The last example with output
	>>> function_query(info, transform = '[name, list(args.keys()), re.findall(r"@param\s+(\S+)", comment, re.M)]', grep = 'set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))')
	[['parse', ['line'], ['strtok', 'sobra', 'strtol']], ['main', [], ['BUFSIZ']], ['soma', ['s'], []], ['subtrai', ['s'], []], ['multiplica', ['s'], []], ['dividir', ['s'], []], ['decrementa', ['s'], []], ['incrementa', ['s'], []], ['modulo', ['s'], []], ['expoente', ['s'], []], ['e', ['s'], []], ['ou', ['s'], []], ['xorr', ['s'], []], ['nott', ['s'], []], ['PUSH', ['s', 'valor'], ['valor']], ['POP', ['s'], []], ['PRINT_STACK', ['s'], []]]

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	function_query(info, transform = '[name]', grep = "arg_doc_problems(args, comment)")

Output:
	['parse', 'main', 'soma', 'subtrai', 'multiplica', 'dividir', 'decrementa', 'incrementa', 'modulo', 'expoente', 'e', 'ou', 'xorr', 'nott', 'PUSH', 'POP', 'PRINT_STACK']

# Query language

	SHOW name
	COND not comment

	SHOW name comment
	COND comment and return == 'void' and '@returns' in comment

	SHOW name cyclomatic_complexity
	COND cyclomatic_complexity > 10

	SHOW name cyclomatic_complexity
	COND cyclomatic_complexity > 0
	SORT maintainability_index

	SHOW name cyclomatic_complexity
	COND cyclomatic_complexity > 0
	SORT -maintainability_index name

	SHOW name cyclomatic_complexity halstead_bugprop maintainability_index
	COLOR cyclomatic_complexity : cyclomatic_complexity < 3, maintainability_index : maintainability_index > 80

	name         cyclomatic_complexity      halstead_bugprop  maintainability_index
	-----------  -----------------------  ------------------  -----------------------
	parse        🟥 28                              0.604263   🟥 61.85078965844583
	main         🟩 1                               0.0312551  🟩 100
	soma         🟩 2                               0.0613119  🟩 100
	subtrai      🟩 2                               0.0613119  🟩 100
	multiplica   🟩 2                               0.06       🟩 100
	dividir      🟩 1                               0.0763541  🟩 100
	decrementa   🟩 2                               0.0517745  🟩 100
	incrementa   🟩 2                               0.0517745  🟩 100
	modulo       🟩 2                               0.0613119  🟩 100
	expoente     🟩 2                               0.0653994  🟩 100
	e            🟩 2                               0.0613119  🟩 100
	ou           🟩 2                               0.0613119  🟩 100
	xorr         🟩 2                               0.0613119  🟩 100
	nott         🟩 2                               0.0325574  🟩 100
	NEW_STACK    🟩 1                               0.0346667  🟩 100
	PUSH         🟩 2                               0.0633883  🟩 100
	POP          🟩 1                               0.0463246  🟩 100
	PRINT_STACK  🟥 3                               0.0663456  🟩 100


	SHOW name args documented(comment)
	COND arg_doc_problems(args, comment)

