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

	name                  cyclomatic_complexity    halstead_bugprop        maintainability_index
	--------------------  -----------------------  ----------------------  -----------------------
	is_empty              🟩 0                      🟥 0.05945908824849729   🟩 100
	penultimo             🟩 0                      🟥 0.05042249444035256   🟩 100
	pop                   🟩 0                      🟥 0.06532882502259622   🟩 100
	top                   🟩 0                      🟥 0.05805500935039566   🟩 100
	has_type              🟩 1                      🟥 0.0639185198671346    🟩 100
	main                  🟩 1                      🟩 0.048981851742056784  🟩 100
	duplica               🟩 2                      🟥 0.056                 🟩 100
	enesimo               🟩 2                      🟥 0.07739760316291208   🟩 100
	ler_linha             🟩 2                      🟩 0.04531122681006491   🟩 100
	new_stack             🟩 2                      🟥 0.1144587448783573    🟩 100
	popp                  🟩 2                      🟩 0.03426619429851844   🟩 100
	rodatres              🟩 2                      🟥 0.0945183000326924    🟩 100
	trocadois             🟩 2                      🟥 0.072211843528756     🟩 100
	copian                🟥 3                      🟥 0.0651348885394683    🟩 100
	parse2                🟥 3                      🟥 0.08784634845557522   🟩 100
	verifica_carater      🟥 3                      🟥 0.07347277761308517   🟩 100
	nott                  🟥 5                      🟥 0.10248740653150443   🟩 100
	push                  🟥 3                      🟥 0.14366215835592955   🟩 99.92049769252367
	parse                 🟥 3                      🟥 0.12364402679889169   🟩 97.99452174359152
	converte_para_char    🟥 5                      🟥 0.11920902501875007   🟩 96.52391934110824
	converte_para_double  🟥 6                      🟥 0.12245462935514195   🟩 96.1542362975608
	converte_para_long    🟥 6                      🟥 0.12444899364539821   🟩 96.07022845886661
	decrementa            🟥 8                      🟥 0.17861670928936146   🟩 91.56801924883034
	incrementa            🟥 8                      🟥 0.20030645508573347   🟩 89.06398158095722
	print_stack           🟥 3                      🟥 0.23726196660226548   🟩 84.6730866972618
	xorr                  🟥 10                     🟥 0.3637687348656868    🟩 81.5303145267608
	e                     🟥 10                     🟥 0.37596692505913476   🟩 80.66933794117628
	ou                    🟥 10                     🟥 0.38079620756152743   🟥 79.94165314864951
	modulo                🟥 6                      🟥 0.4454815561106713    🟥 78.20989263681746
	soma                  🟥 19                     🟥 0.7723816908105884    🟥 63.62646972307609
	multiplica            🟥 20                     🟥 0.8004060628641838    🟥 62.87710754667034
	expoente              🟥 20                     🟥 0.8525042728448817    🟥 62.54920051887836
	subtrai               🟥 20                     🟥 0.8092380785463633    🟥 62.492758972679226
	dividir               🟥 11                     🟥 0.9346917038929904    🟥 61.40891224648385
	tokenizador           🟥 51                     🟥 1.057869301211152     🟥 47.186473217293056


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

Produces the following output

	name                  complexity    maint_idx             cmplxty_grd           maint_grd               assessment
	--------------------  ------------  --------------------  --------------------  ----------------------  ----------------------
	is_empty              🟩 0           🟩 100                 🟩 1                   🟩 1.0                   🟩 1.0
	penultimo             🟩 0           🟩 100                 🟩 1                   🟩 1.0                   🟩 1.0
	pop                   🟩 0           🟩 100                 🟩 1                   🟩 1.0                   🟩 1.0
	top                   🟩 0           🟩 100                 🟩 1                   🟩 1.0                   🟩 1.0
	has_type              🟩 1           🟩 100                 🟩 1.0                 🟩 1.0                   🟩 1.0
	main                  🟩 1           🟩 100                 🟩 1.0                 🟩 1.0                   🟩 1.0
	duplica               🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	enesimo               🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	ler_linha             🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	new_stack             🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	popp                  🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	rodatres              🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	trocadois             🟩 2           🟩 100                 🟩 0.8888888888888888  🟩 1.0                   🟩 0.9444444444444444
	copian                🟩 3           🟩 100                 🟩 0.7777777777777778  🟩 1.0                   🟩 0.8888888888888888
	parse2                🟩 3           🟩 100                 🟩 0.7777777777777778  🟩 1.0                   🟩 0.8888888888888888
	verifica_carater      🟩 3           🟩 100                 🟩 0.7777777777777778  🟩 1.0                   🟩 0.8888888888888888
	nott                  🟨 5           🟩 100                 🟨 0.5555555555555556  🟩 1.0                   🟩 0.7777777777777778
	push                  🟩 3           🟩 99.92049769252367   🟩 0.7777777777777778  🟩 0.9980124423130917    🟩 0.8878951100454348
	parse                 🟩 3           🟩 97.99452174359152   🟩 0.7777777777777778  🟩 0.949863043589788     🟩 0.8638204106837829
	converte_para_char    🟨 5           🟩 96.52391934110824   🟨 0.5555555555555556  🟩 0.913097983527706     🟨 0.7343267695416308
	converte_para_double  🟧 6           🟩 96.1542362975608    🟧 0.4444444444444444  🟩 0.90385590743902      🟨 0.6741501759417322
	converte_para_long    🟧 6           🟩 96.07022845886661   🟧 0.4444444444444444  🟩 0.9017557114716652    🟨 0.6731000779580548
	decrementa            🟥 8           🟩 91.56801924883034   🟥 0.2222222222222222  🟩 0.7892004812207585    🟨 0.5057113517214904
	incrementa            🟥 8           🟩 89.06398158095722   🟥 0.2222222222222222  🟨 0.7265995395239304    🟧 0.4744108808730763
	print_stack           🟩 3           🟩 84.6730866972618    🟩 0.7777777777777778  🟨 0.6168271674315449    🟨 0.6973024726046613
	xorr                  🟥 10          🟩 81.5303145267608    🟥 0.0                 🟨 0.5382578631690201    🟧 0.26912893158451007
	e                     🟥 10          🟩 80.66933794117628   🟥 0.0                 🟨 0.5167334485294071    🟧 0.25836672426470353
	ou                    🟥 10          🟥 79.94165314864951   🟥 0.0                 🟧 0.4985413287162377    🟥 0.24927066435811884
	modulo                🟧 6           🟥 78.20989263681746   🟧 0.4444444444444444  🟧 0.45524731592043644   🟧 0.4498458801824404
	soma                  🟥 19          🟥 63.62646972307609   🟥 0                   🟥 0.09066174307690229   🟥 0.045330871538451147
	multiplica            🟥 20          🟥 62.87710754667034   🟥 0                   🟥 0.07192768866675844   🟥 0.03596384433337922
	expoente              🟥 20          🟥 62.54920051887836   🟥 0                   🟥 0.06373001297195895   🟥 0.03186500648597947
	subtrai               🟥 20          🟥 62.492758972679226  🟥 0                   🟥 0.062318974316980656  🟥 0.031159487158490328
	dividir               🟥 11          🟥 61.40891224648385   🟥 0                   🟥 0.035222806162096276  🟥 0.017611403081048138
	tokenizador           🟥 51          🟥 47.186473217293056  🟥 0                   🟥 0                     🟥 0.0


	SHOW name project return loc
	GROUP_BY project return
	AGGREG len(name) min(loc) mean(loc) max(loc)

	SHOW name project return loc
	GROUP_BY project return
	AGGREG mean(loc); (lambda L: len([x for x in L if x < 10]))(loc)


# Using the query system on other scripts

	>>> from teaching_assistant import *
	>>> info = extract_all_functions("/home/rui/repos/PL2G01")
	>>> function_query(info, transform = '[name]', grep = "arg_doc_problems(args, comment)")
	[['name'], ['parse'], ['main'], ['soma'], ['subtrai'], ['multiplica'], ['dividir'], ['decrementa'], ['incrementa'], ['modulo'], ['expoente'], ['e'], ['ou'], ['xorr'], ['nott'], ['PUSH'], ['POP'], ['PRINT_STACK']]

