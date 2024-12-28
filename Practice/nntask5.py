import argparse
import sys
import numpy as np
import re
from math import exp

def sigmoid_activation(x):
    return 1 / (1 + exp(-x))

def propagate_forward(layers, inputs):
    try:
        for idx, layer in enumerate(layers):
            if idx == 0:
                layer['x'] = inputs
            for i in range(layer['n']):
                weighted_sum = sum(layer['w'][i][j] * layer['x'][j] for j in range(layer['m']))
                layer['y_'][i] = sigmoid_activation(weighted_sum)
                layer['df'][i] = layer['y_'][i] * (1 - layer['y_'][i])
            if idx < len(layers) - 1:
                if layers[idx + 1]['m'] != len(layer['y_']):
                    raise ValueError(f"Не совпадает размерность матриц: {layers[idx + 1]['m']} != {len(layer['y_'])}")
                layers[idx + 1]['x'] = layer['y_']
        return layers[-1]['y_']
    except ValueError as e:
        print(f"ValueError: {e}")
        sys.exit(1)

def propagate_backward(layers, expected_output):
    total_error = 0
    last_layer = layers[-1]
    output_length = len(expected_output)
    deltas = [None] * len(layers)
    deltas[-1] = np.zeros(output_length)
    for i in range(output_length):
        error = last_layer['y_'][i] - expected_output[i]
        deltas[-1][i] = error * last_layer['df'][i]
        total_error += error ** 2 / 2
    for idx in range(len(layers) - 1, 0, -1):
        current_layer = layers[idx]
        deltas[idx - 1] = np.zeros(current_layer['m'])
        for i in range(current_layer['m']):
            for j in range(current_layer['n']):
                deltas[idx - 1][i] += current_layer['w'][j][i] * deltas[idx][j]
            deltas[idx - 1][i] *= layers[idx - 1]['df'][i]
    return total_error, deltas

def adjust_weights(layers, deltas, learning_rate):
    for k, layer in enumerate(layers):
        for i in range(layer['n']):
            for j in range(layer['m']):
                layer['w'][i][j] -= learning_rate * deltas[k][i] * layer['x'][j]

def train_network(layers, input_data, output_data, max_epochs, learning_rate, error_threshold):
    it = 0
    total_error = 1
    history = ''
    while it < max_epochs and total_error > error_threshold:
        it += 1
        epoch_errors = []
        for i in range(len(input_data)):
            propagate_forward(layers, input_data[i])
            total_error, deltas = propagate_backward(layers, output_data[i])
            epoch_errors.append(total_error)
            adjust_weights(layers, deltas, learning_rate)
        total_error = np.mean(epoch_errors)
        history += f'{it}: {total_error}\n'
    for i in range(len(input_data)):
        print(f'Вход: {input_data[i]}, Ожидаемый выход: {output_data[i]}, Полученный выход: {propagate_forward(layers, input_data[i])}')
    return history

def load_matrices_from_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return parse_matrices_from_text(data)

def parse_matrices_from_text(data):
    matrices = {}
    matches = re.findall(r"(\S+)\s*:\s*\[\[(.*?)\]\]", data, re.DOTALL)
    for name, matrix_str in matches:
        matrix_str = matrix_str.replace(" ", "")
        rows = matrix_str.split('],[')
        
        matrix_data = []
        for row in rows:
            try:
                row_data = list(map(float, row.split(',')))
                matrix_data.append(row_data)
            except ValueError as e:
                print(f"Ошибка при обработке матрицы {name}: строка '{row}' не может быть преобразована в числа.")
                sys.exit(1)
        row_lengths = [len(row) for row in matrix_data]
        if len(set(row_lengths)) > 1:
            print(f"Ошибка при обработке матрицы {name}: строки имеют разные длины: {row_lengths}")
            sys.exit(1)
        matrices[name] = np.array(matrix_data)
    return matrices


def parse_parameters_from_text(data):
    matches = re.findall(r"(\S+)\s*=\s*(\S+)", data)
    return {key.strip(): value.replace(',', '') for key, value in matches}

def load_parameters_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            params = {}
            for line in file:
                key, value = line.strip().split('=')
                params[key.strip()] = value.strip()
        return params
    except FileNotFoundError:
        raise ValueError(f"Файл {file_path} не найден.")
    except Exception as e:
        raise ValueError(f"Ошибка при чтении файла {file_path}: {str(e)}")

def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('params', nargs='+', type=lambda param: param.split('='))
    args = parser.parse_args()
    return {param[0]: param[1] for param in args.params}

def main():
    args = create_argument_parser()
    input1, input2, input3, output1 = args['input1'], args['input2'], args['input3'], args['output1']

    weights = load_matrices_from_file(input1)
    layers = [{'w': weight, 'n': weight.shape[0], 'm': weight.shape[1], 'x': np.zeros(weight.shape[1]), 'y_': np.zeros(weight.shape[0]), 'df': np.zeros(weight.shape[0])} for weight in weights.values()]
    
    first_weight = list(weights.values())[0]

    data = load_matrices_from_file(input2)
    x_data, y_data = data['x'], data['y']
    if len(x_data) != len(y_data):
        raise ValueError(f"Не совпадает размерность матриц: x и y")
    try:
        if len(x_data[0]) != first_weight.shape[1]:
            raise ValueError("Не совпадает размерность матриц: x и weights")
    except ValueError as e:
        print(e)
        sys.exit(1)
    try:
        params = load_parameters_from_file(input3)
        try:
            max_epochs = int(params['iters'])
        except ValueError:
            raise ValueError(f"Неверное значение для 'iters' в файле {input3}. Ожидалось целое число.")
        
        try:
            learning_rate = float(params['alpha'])
        except ValueError:
            raise ValueError(f"Неверное значение для 'alpha' в файле {input3}. Ожидалось число с плавающей точкой.")
        
        try:
            error_threshold = float(params['eps'])
        except ValueError:
            raise ValueError(f"Неверное значение для 'eps' в файле {input3}. Ожидалось число с плавающей точкой.")
    except ValueError as e:
        print(e)
        sys.exit(1)
    result = train_network(layers, x_data, y_data, max_epochs, learning_rate, error_threshold)
    with open(output1, 'w', encoding="utf-8") as output_file:
        output_file.write(result)
    print('История обучения записана в файл', output1)

if __name__ == "__main__":
    main()
