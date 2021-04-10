import tabfun
trim = lambda x: 1 if x > 1 else 0 if x < 0 else x
scale_upper = lambda L, U: lambda x: trim((x - L) / (U - L))
scale_lower  = lambda L, U: lambda x: trim((U - x) / (U - L))
arg_doc_problems = lambda args, comment: set(args.keys()) != set(re.findall(r"@param\s+(\S+)", comment, re.M))
documented = lambda comment: re.findall(r"@param\s+(\S+)", comment, re.M)

palette = lambda fun: lambda x: tabfun.colors[int(fun(x) * 3)]
