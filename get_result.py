import psycopg2
import pandas.io.sql as psql
import sys
import os
from solver import Solver

DB_CFG = {
    'dbname': 'diploma',
    'user': 'diploma',
    'password': 'diploma',
    'host': 'localhost'
}

_, timestamp_arg, method, coeffs_arg, directions_arg, *groups_arg = sys.argv

try:
    os.remove('logs/logs.txt')
except OSError:
    pass

coefficients = list(map(lambda x: int(x), coeffs_arg.split(',')))
direction = list(map(lambda x: x, directions_arg.split(',')))
groups = list(map(lambda x: list(map(lambda y: int(y), x.split(','))), groups_arg))

conn = psycopg2.connect(**DB_CFG)
df_helicopters = psql.read_sql('''SELECT name,
                               weight,
                               duration,
                               distance,
                               height,
                               speed,
                               pixels,
                               fps,
                               rating,
                               price
                        FROM helicopters
                        ORDER BY id''', conn)

df_criteria = psql.read_sql('''SELECT num, name
                        FROM criteria
                        ORDER BY num''', conn)

df_criteria.insert(2, 'coefficient', coefficients)
df_criteria.insert(3, 'direction', direction)

solver = Solver(df_helicopters, df_criteria)

solver.get_xls(int(method), groups, f'ruby/public/results/result{timestamp_arg}.xlsx')
