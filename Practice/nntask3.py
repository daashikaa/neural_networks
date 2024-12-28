import xml.etree.ElementTree as ET
from collections import defaultdict
import sys
import operator
import math
import nntask1
import nntask2
import re

def read_operations(file_path):
	opers = {}
	with open(file_path, 'r') as f:
		lines = f.readlines()[1:-1]
		for line in lines:
			line = line.strip()
			match = re.match(r'(\w+)\s*:\s*(\S+)', line)
			if match:
				vertex_name, operation = match.groups()
				opers[vertex_name] = operation
			else:
				raise ValueError(f'Неверный формат строки: {line}')
	return opers

def calculate(vrtx, edgs, opers, res_lst, errors):
	if vrtx in res_lst:
		return res_lst[vrtx]
	operation = opers.get(vrtx)
	if operation is None:
		errors.append(f"Операция для вершины '{vrtx}' не найдена")
		return None
	if operation.isdigit() or (operation.replace('.', '', 1).isdigit() and operation.count('.') < 2):
		if edgs.get(vrtx):
			errors.append(f"Константа '{vrtx}' не может иметь дочерние элементы")
			return None
		result = float(operation)
	else:
		children = sorted(edgs.get(vrtx, []), key=lambda x: x[0])
		kids = [calculate(child[1], edgs, opers, res_lst, errors) for child in children]
		if operation == '+':
			result = sum(kids)
		elif operation == '*':
			result = math.prod(kids)
		elif operation == 'exp':
			result = math.exp(kids[0]) if kids else 1
		else:
			errors.append(f"Неизвестная операция '{operation}' в вершине '{vrtx}'")
			return None
	res_lst[vrtx] = result
	return result


def process_graph(inptxt_name, inpttxt_opers, output):
	vertices, edges, out_edgs = nntask2.read_xml(inptxt_name)
	opers = read_operations(inpttxt_opers)
	if nntask2.detect_cycle(edges):
			return 'Ошибка. Граф содержит цикл!'
	root_nodes = [vertex for vertex in vertices if out_edgs[vertex] == 0]
	if not root_nodes:
			return 'Ошибка. Не найден корень или граф содержит цикл!'
	computed_values = {}
	errors = []
	results = [calculate(root, edges, opers, computed_values, errors) for root in root_nodes]
	if errors:
			error_message = f"Ошибки в операциях: {'; '.join(errors)}"
			print(error_message)
			return error_message 
	with open(f'{output}.txt', 'w') as f:
			f.write(str(results[0]))
			print(f'Результат записан в {output}.txt')
	return results


def main():
	input1 = 'input1.txt'
	input2 = 'input2.txt'
	output = 'output'
	for arg in sys.argv[1:]:
			if arg.startswith('input1='):
					input1 = arg.split('=')[1]
			elif arg.startswith('input2='):
					input2 = arg.split('=')[1]
			elif arg.startswith('output='):
					output = arg.split('=')[1]
	vertices, arcs, errors = nntask1.read_txt(input1)
	if errors:
		for error in errors:
			print(error)
	else:
		nntask1.to_xml(vertices, arcs, output)
	input1 = 'output.xml'
	input2 = 'input2.txt'
	res = process_graph(input1, input2, output)
	if 'Ошибка' in str(res):
			print(res)

main()
