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

	SHOW name cyclomatic_complexity
		halstead_bugprop maintainability_index
	SORT -maintainability_index cyclomatic_complexity name
	COLOR cyclomatic_complexity : cyclomatic_complexity < 3;
		maintainability_index : maintainability_index > 80;
		halstead_bugprop : halstead_bugprop < 0.05

	name         cyclomatic_complexity    halstead_bugprop        maintainability_index
	-----------  -----------------------  ----------------------  -----------------------
	NEW_STACK    🟩 1                      🟩 0.034666666666666665  🟩 100
	POP          🟩 1                      🟩 0.046324578867503845  🟩 100
	dividir      🟩 1                      🟥 0.07635406300967673   🟩 100
	main         🟩 1                      🟩 0.03125512476486815   🟩 100
	PUSH         🟩 2                      🟥 0.06338827872501465   🟩 100
	decrementa   🟩 2                      🟥 0.051774529322504294  🟩 100
	e            🟩 2                      🟥 0.06131194261875509   🟩 100
	expoente     🟩 2                      🟥 0.06539940546000543   🟩 100
	incrementa   🟩 2                      🟥 0.051774529322504294  🟩 100
	modulo       🟩 2                      🟥 0.06131194261875509   🟩 100
	multiplica   🟩 2                      🟥 0.06                  🟩 100
	nott         🟩 2                      🟩 0.03255742163007099   🟩 100
	ou           🟩 2                      🟥 0.06131194261875509   🟩 100
	soma         🟩 2                      🟥 0.06131194261875509   🟩 100
	subtrai      🟩 2                      🟥 0.06131194261875509   🟩 100
	xorr         🟩 2                      🟥 0.06131194261875509   🟩 100
	PRINT_STACK  🟥 3                      🟥 0.06634557535550285   🟩 100
	parse        🟥 28                     🟥 0.6042631877271641    🟥 61.85078965844583




	SHOW name args documented(comment)
	COND arg_doc_problems(args,comment)

	SHOW
		name
		cyclomatic_complexity
		maintainability_index
		scale_lower(1,10)(cyclomatic_complexity)
		scale_upper(60,100)(maintainability_index)
		0.5*scale_lower(1,10)(cyclomatic_complexity)+0.5*scale_upper(60,100)(maintainability_index)
	HEADER name complexity maint_idx complexity_assessment maint_assessment assessment
	SORT -maintainability_index cyclomatic_complexity name
	COLOR
		complexity : palette(scale_lower(1,10))(complexity);
		maint_idx : maint_idx > 80

	name         complexity    maint_idx              complexity_assessment    maint_assessment    assessment
	-----------  ------------  -------------------  -----------------------  ------------------  ------------
	NEW_STACK    🟥 1           🟩 100                               1                  1             1
	POP          🟥 1           🟩 100                               1                  1             1
	dividir      🟥 1           🟩 100                               1                  1             1
	main         🟥 1           🟩 100                               1                  1             1
	PUSH         🟧 2           🟩 100                               0.888889           1             0.944444
	decrementa   🟧 2           🟩 100                               0.888889           1             0.944444
	e            🟧 2           🟩 100                               0.888889           1             0.944444
	expoente     🟧 2           🟩 100                               0.888889           1             0.944444
	incrementa   🟧 2           🟩 100                               0.888889           1             0.944444
	modulo       🟧 2           🟩 100                               0.888889           1             0.944444
	multiplica   🟧 2           🟩 100                               0.888889           1             0.944444
	nott         🟧 2           🟩 100                               0.888889           1             0.944444
	ou           🟧 2           🟩 100                               0.888889           1             0.944444
	soma         🟧 2           🟩 100                               0.888889           1             0.944444
	subtrai      🟧 2           🟩 100                               0.888889           1             0.944444
	xorr         🟧 2           🟩 100                               0.888889           1             0.944444
	PRINT_STACK  🟧 3           🟩 100                               0.777778           1             0.888889
	parse        🟩 28          🟥 61.85078965844583                 0                  0.0462697     0.0231349
