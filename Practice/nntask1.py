
import xml.etree.ElementTree as etr
from xml.dom import minidom
import re
from collections import defaultdict
import sys

def read_txt(pth):
	pttrn = re.compile(r'\(\s*(\w+)\s*,\s*(\w+)\s*,\s*(\d+)\s*\)')
	errors = []
	arcs = []
	vrtcs = set()
	arc_order_map = defaultdict(lambda: defaultdict(list))

	with open(pth, 'r', encoding='utf-8') as f:
		i = 0
		lines = f.readlines()
		for l in lines:
			i += 1
			l = l.strip().rstrip(',').replace(' ', '').replace('	', '').strip('()').split('),(')
			for trpl in l:
				if not trpl:
					continue
				trpl = '(' + trpl + ')'
				chck = pttrn.match(trpl)
				if chck:
					from_vrtx, to_vrtx, ord = chck.groups()
					ord = int(ord)
					vrtcs.update([from_vrtx, to_vrtx])
					arcs.append((from_vrtx, to_vrtx, ord))
					
					if ord in arc_order_map[to_vrtx]:
						other_from_vrtx = arc_order_map[to_vrtx][ord]
						errors.append(
							f"Ошибка на строке {i}: Дуга из {from_vrtx} в {to_vrtx} с порядковым номером {ord} уже существует для {other_from_vrtx}")
					else:
						arc_order_map[to_vrtx][ord] = from_vrtx

					for existing_ord in arc_order_map[to_vrtx].keys():
						if existing_ord != ord and arc_order_map[to_vrtx][existing_ord] == from_vrtx:
							errors.append(
								f"Ошибка на строке {i}: Конфликт номеров дуг для пары ({from_vrtx}, {to_vrtx}). Найдены порядковые номера {existing_ord} и {ord}")

				else:
					errors.append(f"Ошибка на строке {i}: {trpl}")
	return vrtcs, arcs, errors


def to_xml(vrtcs, arcs, pth):
	ordered_vrtcs = []
	visited = set()

	for from_vertex, to_vertex, order in arcs:
		if from_vertex not in visited:
			ordered_vrtcs.append(from_vertex)
			visited.add(from_vertex)
		if to_vertex not in visited:
			ordered_vrtcs.append(to_vertex)
			visited.add(to_vertex)

	# vertex_index_map = {v: i for i, v in enumerate(ordered_vrtcs)}
	# ordered_arcs = sorted(arcs, key=lambda x: (vertex_index_map[x[0]], vertex_index_map[x[1]]))

	g_el = etr.Element('graph')
	for v in ordered_vrtcs:
		v_el = etr.SubElement(g_el, 'vertex')
		v_el.text = v

	for from_vertex, to_vertex, order in arcs:
		arc_el = etr.SubElement(g_el, 'arc')
		from_el = etr.SubElement(arc_el, 'from')
		from_el.text = from_vertex
		to_el = etr.SubElement(arc_el, 'to')
		to_el.text = to_vertex
		order_el = etr.SubElement(arc_el, 'order')
		order_el.text = str(order)
	res = etr.tostring(g_el, encoding='utf-8', method='xml')
	frmttd = minidom.parseString(res).toprettyxml(indent='	')
	with open(pth + '.xml', 'w', encoding='utf-8') as xml_file:
		xml_file.write(frmttd)
		print('XML успешно записан в ' + pth + '.xml')


def main():
	input1 = 'input.txt'
	output1 = 'output'
	for arg in sys.argv[1:]:
		if arg.startswith("input1="):
			input1 = arg.split('=')[1]
		elif arg.startswith("output1="):
			output1 = arg.split('=')[1][:-4]
	vertices, arcs, errors = read_txt(input1)
	if errors:
		for error in errors:
			print(error)
	else:
		to_xml(vertices, arcs, output1)


# main()
