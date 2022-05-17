import psycopg2
import pandas.io.sql as psql
import pandas as pd
import numpy as np
import sys
import os
from solver import Solver

DB_CFG = {
    'dbname': 'diploma',
    'user': 'diploma',
    'password': 'diploma',
    'host': 'localhost'
}

_, timestamp_arg, method_arg, alternatives_names_arg, criteria_names_arg, estimates_arg, coeffs_arg, directions_arg, groups_arg = sys.argv

try:
    os.remove('logs/logs.txt')
except OSError:
    pass

alternatives_names = list(map(lambda x: x, alternatives_names_arg.split('|')))
criteria_names = list(map(lambda x: x, criteria_names_arg.split('|')))
estimates = np.array(list(
    map(lambda y: np.fromstring(y, dtype=float, sep=';'), map(lambda x: x, estimates_arg.split('|')))))
coeffs = list(map(lambda x: int(x), coeffs_arg.split('|')))
directions = list(map(lambda x: x, directions_arg.split('|')))
groups = list(
    map(lambda y: list(map(lambda z: int(z[1:]) - 1, y.split(';'))), list(map(lambda x: x, groups_arg.split('|')))))

# print(alternatives_names, criteria_names, estimates, coeffs, directions, groups)

criteria_dict = {
    'name': criteria_names,
    'coefficient': coeffs,
    'direction': directions
}
df_criteria = pd.DataFrame.from_dict(criteria_dict, orient='index').transpose()
df_criteria.insert(0, 'num', list(map(lambda x: x + 1, list(range(len(df_criteria))))))

df_alternatives = pd.concat([pd.DataFrame({'name': alternatives_names}), pd.DataFrame(estimates)], axis=1)

# print(df_criteria)
# print(df_alternatives)

solver = Solver(df_alternatives, df_criteria)
solver.get_xls(int(method_arg), groups, f'ruby/public/results/result{timestamp_arg}.xlsx')

# coefficients = list(map(lambda x: int(x), coeffs_arg.split(',')))
# direction = list(map(lambda x: x, directions_arg.split(',')))
# groups = list(map(lambda x: list(map(lambda y: int(y), x.split(','))), groups_arg))
#
# conn = psycopg2.connect(**DB_CFG)
# df_helicopters = psql.read_sql('''SELECT name,
#                                weight,
#                                duration,
#                                distance,
#                                height,
#                                speed,
#                                pixels,
#                                fps,
#                                rating,
#                                price
#                         FROM helicopters
#                         ORDER BY id''', conn)
#
# df_criteria = psql.read_sql('''SELECT num, name
#                         FROM criteria
#                         ORDER BY num''', conn)
#
# df_criteria.insert(2, 'coefficient', coefficients)
# df_criteria.insert(3, 'direction', direction)
#
# solver = Solver(df_helicopters, df_criteria)
#
# solver.get_xls(int(method_arg), groups, f'ruby/public/results/result{timestamp_arg}.xlsx')
