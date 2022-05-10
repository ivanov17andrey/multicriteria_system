import pandas as pd
import re
import sys
import os
from solver import Solver

_, timestamp_arg, method = sys.argv

try:
    os.remove('logs/logs.txt')
except OSError:
    pass

filename = f'input{timestamp_arg}.xlsx'

df_helicopters_from_file = pd.read_excel(f'ruby/public/uploads/{filename}', sheet_name=0)
criteria_temp = pd.read_excel(f'ruby/public/uploads/{filename}', sheet_name=1)
df_criteria_from_file = pd.DataFrame(criteria_temp.to_numpy().T, columns=['name', 'coefficient', 'direction'])
df_criteria_from_file.insert(0, 'num', [x + 1 for x in range(len(df_criteria_from_file))])
df_groups_from_file = pd.read_excel(f'ruby/public/uploads/{filename}', sheet_name=2)
groups_from_file = list(
    map(lambda x: list(dict.fromkeys(list(map(lambda x: int(x) - 1, re.sub("[^0-9,]", "", x[0]).split(','))))),
        list(df_groups_from_file.to_numpy())))

solver = Solver(df_helicopters_from_file, df_criteria_from_file)
solver.get_xls(int(method), groups_from_file, f'ruby/public/results/result{timestamp_arg}.xlsx')
