import numpy as np
import xlsxwriter
import psycopg2
import pandas.io.sql as psql
import time
import sys


class Aggregation:

    @staticmethod
    def get_preferences_matrices(estimates, direction):
        direction = list(map(lambda x: 1 if x == 'max' else 0, direction))
        estimates = np.array(estimates)
        preferences_matrices = []
        for col, k_v in enumerate(estimates.T):
            p_m = np.zeros((len(k_v), len(k_v)))
            for i in range(len(k_v)):
                for j in range(len(k_v)):
                    if direction[col] == 1:
                        p_m[i][j] = k_v[j] / (k_v[i] + k_v[j])
                    else:
                        p_m[i][j] = k_v[i] / (k_v[i] + k_v[j])

            preferences_matrices.append(p_m)

        return np.array(preferences_matrices)

    @staticmethod
    def get_total_preferences_matrix(preferences_matrices, coefficients):
        return sum(map(lambda x, y: x * y, preferences_matrices, coefficients))

    @staticmethod
    def Q_arithmetic(preferences_matrices, coefficients):
        return sum(map(lambda x, y: x * y, preferences_matrices, coefficients)) / len(preferences_matrices)

    @staticmethod
    def Q_median(preferences_matrices, coefficients):
        return np.median(np.array(list(map(lambda x, y: x * y, preferences_matrices, coefficients))), 0)

    @staticmethod
    def Q_minimax(preferences_matrices, coefficients):
        return (np.array(list(map(lambda x, y: x * y, preferences_matrices, coefficients))).min(0) + np.array(
            list(map(lambda x, y: x * y, preferences_matrices, coefficients))).max(0)) / 2

    @staticmethod
    def get_weights_matrix(matrix):
        n = len(matrix)
        temp = np.ndarray((n, n))
        for i in range(n):
            for j in range(n):
                if matrix[i][j] - matrix[j][i] >= 0:
                    temp[i][j] = matrix[i][j] - matrix[j][i]
                else:
                    temp[i][j] = 0

        return temp

    @staticmethod
    def get_adjacency_matrix(matrix):
        temp = Aggregation.zero_diag(matrix)
        return np.where(temp > temp.T, 1, 0)

    @staticmethod
    def zero_diag(matrix):
        temp = matrix.copy()
        np.fill_diagonal(temp, 0)
        return temp

    @staticmethod
    def transitive_closure(matrix, calc_lengths=False):
        n = len(matrix)
        Z = np.zeros((n, n))
        I = np.full((n, n), np.inf)
        T = np.where(matrix == Z, I, matrix)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if T[i][k] < np.inf and T[k][j] < np.inf and T[i][k] + T[k][j] < T[i][j]:
                        if calc_lengths:
                            T[i][j] = T[i][k] + T[k][j]
                        else:
                            T[i][j] = 1

        T = np.where(T == I, Z, T)
        np.fill_diagonal(T, 0)

        return T

    @staticmethod
    def has_cycles(matrix):
        flag = False
        for i in range(1, len(matrix)):
            powered = np.linalg.matrix_power(matrix, i)
            if np.any(np.diagonal(powered)):
                flag = True

        return flag

    @staticmethod
    def demucron(matrix):
        if Aggregation.has_cycles(matrix):
            print('Граф содержит контуры, нельзя разбить на уровни с помощью адгоритма Демукрона\n')
            return []
        levels = []
        val = None
        alternatives = sorted(list(enumerate(np.sum(matrix, 1))), key=lambda x: x[1])
        for alt in alternatives:
            if val != alt[1]:
                val = alt[1]
                levels.append([])
            levels[-1].append(alt[0] + 1)

        print(f"Алгоритм Демукрона:\n{levels}\n")
        return levels

    @staticmethod
    def copeland(matrix):
        c = np.sum(matrix, 0) - np.sum(matrix, 1)
        levels = []
        val = None
        alternatives = sorted(list(enumerate(c)), key=lambda x: x[1], reverse=True)
        for alt in alternatives:
            if val != alt[1]:
                val = alt[1]
                levels.append([])
            levels[-1].append(alt[0] + 1)

        print(f"Процедура Коупленда:\n{c}\n{levels}\n")
        return levels

    @staticmethod
    def weight_difference(matrix):
        c = np.sum(matrix, 0) - np.sum(matrix, 1)
        levels = []
        val = None
        alternatives = sorted(list(enumerate(c)), key=lambda x: x[1], reverse=True)
        for alt in alternatives:
            if val != alt[1]:
                val = alt[1]
                levels.append([])
            levels[-1].append(alt[0] + 1)

        print(f"Процедура Разности Весов:\n{c}\n{levels}\n")
        return levels

    @staticmethod
    def weight_ratio(matrix):
        c = np.sum(matrix, 0) / np.sum(matrix, 1)
        levels = []
        val = None
        alternatives = sorted(list(enumerate(c)), key=lambda x: x[1], reverse=True)
        for alt in alternatives:
            if val != alt[1]:
                val = alt[1]
                levels.append([])
            levels[-1].append(alt[0] + 1)

        print(f"Процедура Отношения Весов:\n{c}\n{levels}")
        return levels

    @staticmethod
    def get_levels_with(matrix):
        weights_matrix = Aggregation.get_weights_matrix(matrix)
        adjacency_matrix = Aggregation.get_adjacency_matrix(matrix)
        print(adjacency_matrix)
        levels = [Aggregation.demucron(adjacency_matrix), Aggregation.copeland(adjacency_matrix),
                  Aggregation.weight_difference(weights_matrix), Aggregation.weight_ratio(weights_matrix)]

        return levels


class Solver:

    def __init__(self, df, direction, coefficients):
        self.df = df
        self.estimates = df.iloc[:, 1:]
        self.direction = direction
        self.coefficients = coefficients

    def with_selected_coeff(self, selected):
        estimates = np.array(self.estimates)[:, selected]
        direction = np.array(self.direction)[selected]
        coefficients = np.array(self.coefficients)[selected]
        preferences_matrices = Aggregation.get_preferences_matrices(estimates, direction)
        # Q_median = Aggregation.Q_median(preferences_matrices, coefficients)
        # median = Aggregation.get_levels_with(Q_median)
        Q_arithmetic = Aggregation.Q_arithmetic(preferences_matrices, coefficients)
        arith = Aggregation.get_levels_with(Q_arithmetic)

        return arith[1]

    def get_table(self, coeff_groups):
        tab = []
        for gr in coeff_groups:
            tab.append([gr, self.with_selected_coeff(gr)])

        with xlsxwriter.Workbook(f'ruby/public/result{sys.argv[1]}.xlsx') as workbook:
            worksheet = workbook.add_worksheet()

            v_align = {'valign': 'vcenter'}
            align_center = {'align': 'center'}
            text_wrap = {'text_wrap': True}
            align_center_format = workbook.add_format(v_align | align_center | text_wrap)

            length = 0
            headings = ['#']
            for i, col_data in enumerate(tab):
                if len(col_data[1]) > length:
                    length = len(col_data[1])
                heading = ', '.join(list(map(lambda x: f"K{x + 1}", col_data[0])))
                headings.append(heading)
                worksheet.write(1, i + 1, heading, align_center_format)
                for j, level in enumerate(col_data[1]):
                    worksheet.write(j + 2, i + 2, ', '.join(list(map(lambda x: f"A{x}", level))))

            for k in range(length):
                worksheet.write(k + 2, 1, k)

            worksheet.add_table(1, 1, length + 1, len(tab) + 1, {
                'columns': [{'header': h} for h in headings],
                'banded_rows': True,
                'banded_columns': True,
                'first_column': True,
                'style': 'Table Style Light 12'
            })

            worksheet.set_column(1, 100, 20)
            for i in range(1, 100):
                worksheet.set_row(i, 50, align_center_format)
            worksheet.set_row(1, 60, align_center_format)

            # worksheet.set_column(1, 1, 5)
            # worksheet.set_column(2, len(tab) + 1, 20)

            self.helicopters_table(1, 3 + len(tab), self.df, worksheet, workbook)

    def helicopters_table(self, row, col, df, worksheet, workbook):

        v_align = {'valign': 'vcenter'}
        align_center = {'align': 'center'}
        text_wrap = {'text_wrap': True}
        align_center_format = workbook.add_format(v_align | align_center | text_wrap)

        df_copy = df.copy()
        df_copy.insert(0, 'Num', [f'A{x + 1}' for x in range(len(df))])
        shape = np.array(df_copy).shape
        worksheet.add_table(row, col, row + shape[0], col + shape[1] - 1, {
            'data': df_copy.to_numpy(),
            'columns': [
                {'header': '#',
                 'format': align_center_format},
                {'header': 'Название',
                 'format': align_center_format},
                {'header': f'Вес\nКоэф. = {self.coefficients[0]}\n{self.direction[0]}',
                 'format': align_center_format},
                {'header': f'Время полета\nКоэф. = {self.coefficients[1]}\n{self.direction[1]}',
                 'format': align_center_format},
                {'header': f'Дальность\nКоэф. = {self.coefficients[2]}\n{self.direction[2]}',
                 'format': align_center_format},
                {'header': f'Высота\nКоэф. = {self.coefficients[3]}\n{self.direction[3]}',
                 'format': align_center_format},
                {'header': f'Скорость\nКоэф. = {self.coefficients[4]}\n{self.direction[4]}',
                 'format': align_center_format},
                {'header': f'Разрешение\nКоэф. = {self.coefficients[5]}\n{self.direction[5]}',
                 'format': align_center_format},
                {'header': f'FPS\nКоэф. = {self.coefficients[6]}\n{self.direction[6]}',
                 'format': align_center_format},
                {'header': f'Рейтинг\nКоэф. = {self.coefficients[7]}\n{self.direction[7]}',
                 'format': align_center_format},
                {'header': f'Стоимость\nКоэф. = {self.coefficients[8]}\n{self.direction[8]}',
                 'format': align_center_format},
            ]
        })


DB_CFG = {
    'dbname': 'diploma',
    'user': 'diploma',
    'password': 'diploma',
    'host': 'localhost'
}

direction = ['min', 'max', 'max', 'max', 'max', 'max', 'max', 'max', 'min']
coefficients = list(map(lambda x: int(x), sys.argv[2].split(',')))

conn = psycopg2.connect(**DB_CFG)
df = psql.read_sql('''SELECT name,
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

print(coefficients)

solver = Solver(df, direction, coefficients)


groups = list(map(lambda x: list(map(lambda y: int(y), x.split(','))), sys.argv[3:]))
solver.get_table(groups)

