import numpy as np
import xlsxwriter
from aggregation import Aggregation
from utils import *

np.set_printoptions(precision=3, suppress=True)


class Solver:

    def __init__(self, df_helicopters, df_criteria):
        self.df_helicopters = df_helicopters
        self.df_criteria = df_criteria
        self.estimates = df_helicopters.iloc[:, 1:]
        self.direction = df_criteria['direction']
        self.coefficients = df_criteria['coefficient']

    def with_selected_coeff(self, method, selected):
        estimates = np.array(self.estimates)[:, selected]
        coefficients = np.array(self.coefficients)[selected]
        direction = np.array(self.direction)[selected]
        print('_____________________________________________________')
        print(f"Группа критериев {', '.join(list(map(lambda x: f'K{x + 1}', selected)))}\n")
        print(f"Оценки по выбранным критерям\n{estimates}\n")
        print(f"Коэффициенты по выбранным критерям\n{coefficients}\n")
        print(f"Направление по выбранным критерям\n{direction}\n")

        preferences_matrices = Aggregation.get_preferences_matrices(estimates, direction)
        log_to_file('----- Метод Среднего Aрифметического -----\n')
        Q_arithmetic = Aggregation.Q_arithmetic(preferences_matrices, coefficients)
        d_arithm = Aggregation.calc_distance(preferences_matrices, Q_arithmetic)
        arithm = Aggregation.get_levels_with(Q_arithmetic)
        log_to_file('----- Метод Медианы -----\n')
        Q_median = Aggregation.Q_median(preferences_matrices, coefficients)
        d_median = Aggregation.calc_distance(preferences_matrices, Q_median)
        median = Aggregation.get_levels_with(Q_median)
        log_to_file('----- Метод Минимакса -----\n')
        Q_minimax = Aggregation.Q_minimax(preferences_matrices, coefficients)
        d_minimax = Aggregation.calc_distance(preferences_matrices, Q_minimax)
        minimax = Aggregation.get_levels_with(Q_minimax)

        l = [(1, 'Среднее арифметическое', d_arithm, Q_arithmetic, arithm),
             (2, 'Медиана', d_median, Q_median, median),
             (3, 'Минимакс', d_minimax, Q_minimax, minimax)]
        with_min_d = min(l, key=lambda x: x[2])

        if method == 0:
            selected = with_min_d
            for meth in l:
                print(f"{meth[1]}, суммарное расстояние {meth[2]}")
            print(f"Метод с минимальным суммарным расстоянием '{selected[1]}'")
            print(f"Суммарное расстояние {selected[2]}")
            print(f"Матрица имеет вид:\n'{selected[3]}")
        else:
            selected = next(x for x in l if x[0] == method)
            print(f"Выбранный метод '{selected[1]}'")
            print(f"Суммарное расстояние {selected[2]}")
            print(f"Матрица имеет вид:\n {selected[3]}")

        return selected[4][1]

    def get_xls(self, method, coeff_groups, filepath):
        tab = []
        for gr in coeff_groups:
            tab.append([gr, self.with_selected_coeff(method, gr)])

        with xlsxwriter.Workbook(filepath) as workbook:
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
                worksheet.write(0, i, heading, align_center_format)
                for j, level in enumerate(col_data[1]):
                    worksheet.write(j + 1, i + 1, ', '.join(list(map(lambda x: f"A{x}", level))))

            for k in range(length):
                worksheet.write(k + 1, 0, k)

            worksheet.add_table(0, 0, length, len(tab), {
                'columns': [{'header': h} for h in headings],
                # 'banded_rows': True,
                # 'banded_columns': True,
                # 'first_column': True,
                # 'style': 'Table Style Light 12'
            })

            worksheet.set_column(1, 100, 20)
            worksheet.set_row(0, 60, align_center_format)
            for i in range(1, 100):
                worksheet.set_row(i, 50, align_center_format)

            self.helicopters_sheet(0, 0, self.df_helicopters, self.df_criteria, workbook)
            self.criteria_sheet(0, 0, self.df_criteria, workbook)
            self.criteria_groups_sheet(0, 0, coeff_groups, workbook)

    def helicopters_sheet(self, row, col, df_helicopters, df_criteria, workbook):
        v_align = {'valign': 'vcenter'}
        align_center = {'align': 'center'}
        text_wrap = {'text_wrap': True}
        align_center_format = workbook.add_format(v_align | align_center | text_wrap)

        worksheet = workbook.add_worksheet()
        worksheet.set_column(1, 100, 20)
        worksheet.set_row(0, 60, align_center_format)
        for i in range(1, 100):
            worksheet.set_row(i, 50, align_center_format)

        df_copy = df_helicopters.copy()
        df_copy.insert(0, 'Num', [f'A{x + 1}' for x in range(len(df_copy))])
        data = df_copy.to_numpy()
        shape = data.shape
        columns = [
            {'header': '#',
             'format': align_center_format},
            {'header': 'Название',
             'format': align_center_format}
        ]
        for criteria_name in df_criteria['name']:
            columns.append({'header': criteria_name,
                            'format': align_center_format})
        worksheet.add_table(row, col, row + shape[0], col + shape[1] - 1, {
            'data': data,
            'columns': columns
        })

    def criteria_sheet(self, row, col, df_criteria, workbook):
        v_align = {'valign': 'vcenter'}
        align_center = {'align': 'center'}
        text_wrap = {'text_wrap': True}
        align_center_format = workbook.add_format(v_align | align_center | text_wrap)

        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 100, 20)
        worksheet.set_row(0, 60, align_center_format)
        for i in range(1, 100):
            worksheet.set_row(i, 50, align_center_format)

        headers = df_criteria['num'].apply(lambda x: f'K{x}')
        data = df_criteria[['name', 'coefficient', 'direction']].to_numpy().T
        shape = data.shape
        columns = []
        for criteria_num in headers:
            columns.append({'header': criteria_num,
                            'format': align_center_format})
        worksheet.add_table(row, col, row + shape[0], col + shape[1] - 1, {
            'data': data,
            'columns': columns
        })

    def criteria_groups_sheet(self, row, col, groups, workbook):
        v_align = {'valign': 'vcenter'}
        align_center = {'align': 'center'}
        text_wrap = {'text_wrap': True}
        align_center_format = workbook.add_format(v_align | align_center | text_wrap)

        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, 100, 20)
        worksheet.set_row(0, 60, align_center_format)
        for i in range(1, 100):
            worksheet.set_row(i, 50, align_center_format)

        for i, group in enumerate(groups):
            gr_string = ', '.join(list(map(lambda x: f"K{x + 1}", group)))
            worksheet.write(row + i + 1, col + 0, gr_string)

        worksheet.add_table(0, 0, len(groups), 0, {
            'columns': [{'header': 'Группы критериев'}]
        })
