import numpy as np
import xml.etree.ElementTree as ET
from xml.dom import minidom
import argparse


def read_matrices(file_path):
    matrices = []
    try:
        with open(file_path, 'r') as file:
            data = file.read().split("\n")
            for line in data:
                if line.strip():
                    matrix = eval(line.split(":")[1].strip())
                    matrices.append(np.array(matrix))
    except Exception as e:
        raise ValueError(f"Ошибка при чтении матриц: {e}")
    return matrices


def read_input_vector(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
            vector = np.array([float(x) for x in data.split(",")])
    except Exception as e:
        raise ValueError(f"Ошибка при чтении входного вектора: {e}")
    return vector

def build_nn(matrices, input_vector):
    activations = [input_vector]
    for i, matrix in enumerate(matrices):
        if activations[-1].shape[0] != matrix.shape[1]:
            raise ValueError(
                f"Несоответствие размеров: матрица {i+1} ожидает вход {matrix.shape[1]}, а получила {activations[-1].shape[0]}"
            )
        z = np.dot(matrix, activations[-1])
        a = 1 / (1 + np.exp(-z))
        activations.append(a)
    return activations

def serialize_to_xml(matrices, output_file):
    root = ET.Element("NeuralNetwork")
    for i, matrix in enumerate(matrices):
        layer = ET.SubElement(root, "Layer", attrib={"index": str(i + 1)})
        for row in matrix.tolist():
            ET.SubElement(layer, "Weights").text = str(row)
    xml_string = ET.tostring(root, encoding="unicode")
    pretty_xml = minidom.parseString(xml_string).toprettyxml(indent="  ")
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(pretty_xml)

def write_output_vector(vector, output_file):
    with open(output_file, 'w') as file:
        file.write(", ".join(map(str, vector)))

def parse_arguments():
    parser = argparse.ArgumentParser(description="Построение многослойной нейронной сети.")
    parser.add_argument('--input1', type=str, default='input1.txt', help='Путь к файлу с матрицами весов.')
    parser.add_argument('--input2', type=str, default='input2.txt', help='Путь к файлу с входным вектором.')
    parser.add_argument('--output1', type=str, default='output1.txt', help='Путь к файлу для сохранения выходного вектора.')
    parser.add_argument('--output2', type=str, default='output2.xml', help='Путь к файлу для сохранения нейронной сети в XML.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    weight_file = args.input1
    input_file = args.input2
    output_vector_file = args.output1
    output_xml = args.output2
    try:
        matrices = read_matrices(weight_file)
        input_vector = read_input_vector(input_file)
        activations = build_nn(matrices, input_vector)
        serialize_to_xml(matrices, output_xml)
        write_output_vector(activations[-1], output_vector_file)
        print("Многослойная нейронная сеть успешно построена.")
        print(f"Результаты сохранены в файлы: {output_xml}, {output_vector_file}")

    except ValueError as e:
        print(f"Ошибка: {e}")
