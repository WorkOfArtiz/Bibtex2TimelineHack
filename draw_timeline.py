#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import sys
from argparse import ArgumentParser
from collections import defaultdict
import bibtexparser

# Dot template
DOT = """
digraph main {{
    compound=true;
    rank=.75;
    size="7.5, 7.5";

    {{
        node [shape="plaintext", fontsize=16];
        edge [shape=dashed, arrowhead=none];

        {year_code};
    }}

    node [shape=box];
    {rank_code}

    {node_code}

    {edge_code}
}}
"""

# Commmand line parsing
PARSER = ArgumentParser(description='draw paper shit')
PARSER.add_argument('bibtex')
PARSER.add_argument('edges')
ARGS = PARSER.parse_args()

def stringify(x):
    "A small function to put quotes around something in Dot style"
    return ''.join(['"', x.replace('"', "'"),'"'])

# Bibtex parsing happens here
with open(ARGS.bibtex) as bibtex_file:
    bib_db = bibtexparser.load(bibtex_file)

# Get all years from papers with abbreviation
years = sorted({ x['year'] for x in bib_db.entries if x.get('abbreviation')})

# Generate the edges between the years for correct embedding
year_code = '\n        '.join('%s->%s' % (before, after) for before,after in zip(years[:-1], years[1:]))

# Since Im lazy I created 3 data structures
papers_years = defaultdict(list)    # year => [papers]
papers_total = []                   # a list of all paper abbreviations
paper_description = {}              # abbreviation => bibtex paper data

# Loop through all papers
for x in bib_db.entries:
    if x.get('abbreviation') != None:
        title = x['abbreviation']
    else:
        continue # skip papers in references without the abbreviation attr 
    
    # Fill relevant data structures
    paper_description[title] = x
    papers_years[x['year']].append(title)
    papers_total.append(title)

# Make sure the papers from a year are in the same rank as that year
rank_code = '\n    '.join('{rank=same; %s, %s}' % (year, ', '.join(stringify(x) for x in papers_years[year])) for year in years)


# Code for loading the edges between papers from a file
# File format is:
# paper_abbreviation => paper_abbreviation
# 
# With allowed comments and empty lines
with open(ARGS.edges) as edges:
    edge_code = []
    
    for line in edges:
        line = line.split('#')[0].strip()

        if not line:
            continue

        influencer, influencee = map(str.strip, line.split('=>'))
        edge_code.append('%s -> %s' % (influencer, influencee))

edge_code = '\n    '.join(edge_code)

# Code for making the nodes coloured if they have the "class" attribute in BibTex
node_code = []
classes = sorted({v['class'] for v in paper_description.values() if v.get('class')})

for paper in papers_total:
    desc = paper_description[paper]

    if not desc.get('class'):
        continue
    
    node_code.append('%s [colorscheme=set26, style=filled, color=%d];' % (stringify(paper), classes.index(desc['class']) + 1))

node_code = '\n    '.join(node_code)

print(DOT.format(**locals()))
