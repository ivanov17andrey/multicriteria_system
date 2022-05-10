import numpy as np
from utils import *


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
            log_to_file('Граф содержит контуры, нельзя разбить на уровни с помощью алгоритма Демукрона')
            return []
        levels = []
        val = None
        alternatives = sorted(list(enumerate(np.sum(matrix, 1))), key=lambda x: x[1])
        for alt in alternatives:
            if val != alt[1]:
                val = alt[1]
                levels.append([])
            levels[-1].append(alt[0] + 1)

        log_to_file(f"Алгоритм Демукрона:\n{levels}\n")
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

        log_to_file(f"Процедура Коупленда:\n{c}\n{levels}\n")
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

        log_to_file(f"Процедура Разности Весов:\n{c}\n{levels}\n")
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

        log_to_file(f"Процедура Отношения Весов:\n{c}\n{levels}\n")
        return levels

    @staticmethod
    def get_levels_with(matrix):
        weights_matrix = Aggregation.get_weights_matrix(matrix)
        log_to_file(f"Матрица весов:\n{weights_matrix}\n")

        adjacency_matrix = Aggregation.get_adjacency_matrix(matrix)
        log_to_file(f"Матрица смежности:\n{adjacency_matrix}\n")

        levels = [Aggregation.demucron(adjacency_matrix), Aggregation.copeland(adjacency_matrix),
                  Aggregation.weight_difference(weights_matrix), Aggregation.weight_ratio(weights_matrix)]

        return levels

    @staticmethod
    def calc_distance(preferences_matrices, Q_matrix):
        distance = 0
        for m in preferences_matrices:
            distance += np.square(Q_matrix - m).sum()

        return distance
