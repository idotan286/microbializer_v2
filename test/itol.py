from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).parent.resolve()

NEWICK_PATH = SCRIPT_DIR / 'final_species_tree.newick'
API_KEY = "IxlwRnTM3o8axLxxYqX2gA"

url = 'https://itol.embl.de/batch_uploader.cgi'

with open(NEWICK_PATH, 'rb') as tree:
    files = {'treeFile': tree}
    data = {
        'projectName': 'MyTreeProject',
        'treeName': 'ExampleTree',
        'apikey': API_KEY,
    }
    response = requests.post(url, files=files, data=data)

print(response.text)
