# C_teaching_assistant

# Some examples

Names of functions without comments

	function_query(info, transform = "name", grep = "len(comment) == 0")

Names and comments of functions that return void and whose documentation has a @returns keyword

	function_query(info, transform = "[name, comment]", grep = "len(comment) > 0 and return == 'void' and '@returns' in comment")

Names and cyclometric complexity of the functions whose cyclomatic_complexity is above 10

	function_query(info, transform = "[name, cyclomatic_complexity]", grep = "cyclomatic_complexity > 10")

Names and cyclometric complexity of the functions whose maintainability_index is below 80

	function_query(info, transform = "[name, cyclomatic_complexity]", grep = "maintainability_index < 80")

Names, arguments and documented arguments in cases where either an argument was not documented or something that was not an argument was documented as an argument

	function_query(info, transform = '[name, args.keys(), re.findall(r"@param\s+(\S+)", comment, re.M)]', grep = 'set(args.keys()) == set(re.findall(r"@param\s+(\S+)", comment, re.M))').values()
