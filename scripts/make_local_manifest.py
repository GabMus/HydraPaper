#!/usr/bin/env python3

import os
import sys
import json

in_file = sys.argv[1]
git_repo = os.path.join(os.path.dirname(in_file), '.git')
output = sys.argv[2]

manifest = json.load(open(in_file, encoding='utf-8'))
manifest['modules'][0]['sources'][0]['url'] = git_repo
json.dump(manifest, open(output, 'w', encoding='utf-8'))
