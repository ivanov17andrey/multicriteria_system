import pandas as pd
import re
import sys
import os
from solver import Solver
from tabulate import tabulate

_, timestamp_arg, method = sys.argv

try:
    os.remove('logs/logs.txt')
except OSError:
    pass

filename = f'input{timestamp_arg}.xlsx'

df_alternatives = pd.read_excel(f'ruby/public/uploads/{filename}', sheet_name=0)
criteria_temp = pd.read_excel(f'ruby/public/uploads/{filename}', sheet_name=1)
df_criteria = pd.DataFrame(criteria_temp.to_numpy().T, columns=['name', 'coefficient', 'direction'])
df_criteria.insert(0, 'num', [x + 1 for x in range(len(df_criteria))])
df_groups = pd.read_excel(f'ruby/public/uploads/{filename}', sheet_name=2)
groups = list(
    map(lambda x: list(dict.fromkeys(list(map(lambda x: int(x) - 1, re.sub("[^0-9,]", "", x[0]).split(','))))),
        list(df_groups.to_numpy())))

solver = Solver(df_alternatives, df_criteria)
solver.get_xls(int(method), groups, f'ruby/public/results/result{timestamp_arg}.xlsx')

result = pd.read_excel(f'ruby/public/results/result{timestamp_arg}.xlsx', sheet_name=0)
result.fillna('', inplace=True)
print(tabulate(result, headers='keys', tablefmt='psql', showindex=False))