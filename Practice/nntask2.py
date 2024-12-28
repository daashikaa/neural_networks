import xml.etree.ElementTree as ET
from collections import defaultdict
import sys

def read_xml(pth):
	tree = ET.parse(pth)
	root = tree.getroot()
	vertices = set()
	edges = defaultdict(list)
	in_edgs = defaultdict(int)
	out_edgs = defaultdict(int)
	
	# извлечение вершин
	for vertex in root.findall('.//vertex'):
		vertices.add(vertex.text)

	# извлечение ребер
	for arc in root.findall('.//arc'):
		from_v = arc.find('from').text
		to_v = arc.find('to').text
		ord = int(arc.find('order').text)
		edges[to_v].append((ord, from_v)) # инверование направления рёбер
		in_edgs[to_v] += 1
		out_edgs[from_v] += 1
	# сортировка ребер для каждой вершины по порядку
	for vertex in edges:
		edges[vertex].sort() # сортировка по порядку для каждого приёмника
	# возвращает: множество вершин, словарь ребер (ключ - вершина, знаение - список ребер, которые ведут к ней)
	# словарь исходящих ребер (ключ - вершина, значение - количество исходящих ребер)
	return vertices, edges, out_edgs

# проверка наличия цикла (поиск в глубину)
def detect_cycle(graph):
	# множество посещенных вершин
	vstd = set()
	# множетво вершин в стеке рекурсивных вызовов
	stck = set()

	def visit(vertex):
		# если верщина в стеке - цикл найден
		if vertex in stck:
			return True
		# если вершина посещена, цикла нет
		if vertex in vstd:
			return False
		vstd.add(vertex)
		stck.add(vertex)
		for _, neighbor in graph.get(vertex, []):
			if visit(neighbor):
				return True
		stck.remove(vertex)
		return False
	
	for v in list(graph.keys()):
		if visit(v):
			return True
	return False

def count_reachable(vertex, edges, visited=None):
	# подсчет количества вершин, достижимых из заданной
	if visited is None:
		visited = set()
	visited.add(vertex)
	# изначально достижима сама вершина
	count = 1
	for _, child in edges.get(vertex, []):
		if child not in visited:
			count += count_reachable(child, edges, visited)

	return count

# построение текстового представления функции
def bldr(vertex, edges, path=None):
	if path is None:
		# список пройденных вершин
		path = []
	path.append(vertex)
	# если детей нет, возвращаем имя вершины
	if vertex not in edges or not edges[vertex]:
		return f"{vertex}()"
	# сортировка детей по порядку
	children = sorted(edges[vertex], key=lambda x: x[0])
	# рекурсивное построение представления для детей
	children_repr = [bldr(child[1], edges, path[:]) for child in children]
	return f"{vertex}({', '.join(children_repr)})"

def to_fun(input, output):
	# преобразование XML в текстовое представление функции
	vertices, edges, out_edgs = read_xml(input)
	
	if detect_cycle(edges):
		return 'Ошибка. Граф содержит цикл!'
	
	# Поиск стоков (вершин без исходящих рёбер)
	root_nodes = [vertex for vertex in vertices if out_edgs[vertex] == 0]
	
	if not root_nodes:
		return 'Ошибка. Не найден корень или граф содержит цикл!'
	
	function_reprs = []
	
	# для всех стоков строим дерево
	for root in sorted(root_nodes, key=lambda v: count_reachable(v, edges), reverse=True):
		function_reprs.append(bldr(root, edges))
	
	# соединение представления функции
	function_repr = ', '.join(function_reprs)
	
	with open(f'{output}.txt', 'w') as f:
		f.write(function_repr)
		print('TXT успешно записан в ' + f'{output}.txt')

	return function_repr

def main():
	input1 = 'output.xml'
	output1 = 'output'
	for arg in sys.argv[1:]:
		if arg.startswith("input1="):
			input1 = arg.split('=')[1]
		elif arg.startswith("output1="):
			output1 = arg.split('=')[1][:-4]
	res = to_fun(input1, output1)
	if 'Ошибка' in res:
		print(res)

# main()
