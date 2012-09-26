#!/bin/env python

from glob import glob
import json

for file in glob('*.json'):
    f = open(file, 'r')
    text = f.read()
    f.close()

    dict = json.loads(text)
    new_text = json.dumps(dict, sort_keys=True, indent=4)

    f = open('%s.bak' % file, 'w')
    f.write(text)
    f.close()

    f = open(file, 'w')
    f.write(new_text)
    f.close()

