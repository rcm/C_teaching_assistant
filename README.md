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

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	function_query(info, transform = '[name, list(args.keys()), re.findall(r"@param\s+(\S+)", comment, re.M)]', grep = 'set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))')

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	function_query(info, transform = '[name]', grep = "arg_doc_problems(args, comment)")

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
		name;
		cyclomatic_complexity;
		maintainability_index;
		scale_lower(1,10)(cyclomatic_complexity);
		scale_upper(60,100)(maintainability_index);
		0.5*scale_lower(1,10)(cyclomatic_complexity)+
		0.5*scale_upper(60,100)(maintainability_index)
	HEADER name complexity maint_idx cmplxty_grd
		maint_grd assessment
	SORT -maintainability_index cyclomatic_complexity name
	COLOR
		complexity : scale_lower(1,10)(complexity);
		maint_idx : maint_idx > 80;
		cmplxty_grd : cmplxty_grd;
		maint_grd : maint_grd;
		assessment : assessment

	name         complexity    maint_idx            cmplxty_grd           maint_grd               assessment
	-----------  ------------  -------------------  --------------------  ----------------------  ----------------------
	NEW_STACK    🟥 1           🟩 100                🟥 1.0                 🟥 1.0                   🟥 1.0
	POP          🟥 1           🟩 100                🟥 1.0                 🟥 1.0                   🟥 1.0
	dividir      🟥 1           🟩 100                🟥 1.0                 🟥 1.0                   🟥 1.0
	main         🟥 1           🟩 100                🟥 1.0                 🟥 1.0                   🟥 1.0
	PUSH         🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	decrementa   🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	e            🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	expoente     🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	incrementa   🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	modulo       🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	multiplica   🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	nott         🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	ou           🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	soma         🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	subtrai      🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	xorr         🟧 2           🟩 100                🟧 0.8888888888888888  🟥 1.0                   🟧 0.9444444444444444
	PRINT_STACK  🟧 3           🟩 100                🟧 0.7777777777777778  🟥 1.0                   🟧 0.8888888888888888
	parse        🟩 28          🟥 61.85078965844583  🟩 0                   🟩 0.046269741461145666  🟩 0.023134870730572833

# Using the query system on other scripts

	>>> from teaching_assistant import *
	>>> info = extract_all_functions("/home/rui/repos/PL2G01")
	>>> function_query(info, transform = '[name]', grep = "arg_doc_problems(args, comment)")
	[['name'], ['parse'], ['main'], ['soma'], ['subtrai'], ['multiplica'], ['dividir'], ['decrementa'], ['incrementa'], ['modulo'], ['expoente'], ['e'], ['ou'], ['xorr'], ['nott'], ['PUSH'], ['POP'], ['PRINT_STACK']]

