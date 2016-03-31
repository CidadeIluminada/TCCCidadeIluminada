#coding: UTF-8
import unicodecsv as csv
from collections import defaultdict


def _split_bairros(bairros):
    _bairros = bairros.split(';')
    if len(_bairros) == 1 and ',' in _bairros[0]:
        _bairros = _bairros[0].split(',')
    return _bairros


def _clean_bairro(bairro):
    _bairro = bairro.strip()
    if '(' in _bairro and ')' in _bairro:
        _open = _bairro.find('(')
        _close = _bairro.find(')') + 1
        substring = _bairro[_open:_close]
        _bairro = _bairro.replace(substring, '')
    return _bairro

bairro_map = defaultdict(list)

with open("regioes_bairros.txt", 'rb') as f:
    r = csv.reader(f, delimiter=' ', skipinitialspace=True)
    for row in r:
        regiao = row[0]
        splitted = _split_bairros(row[1])
        bairros = [_clean_bairro(bairro) for bairro in splitted if bairro]
        bairro_map[regiao].extend(bairros)

with open('regioes_bairros.csv', 'wb') as outfile:
    writer = csv.DictWriter(outfile, [u'regiao', u'bairro'])
    writer.writeheader()
    for regiao, bairros in bairro_map.iteritems():
        for bairro in bairros:
            writer.writerow({
                u'regiao': regiao,
                u'bairro': bairro,
            })
