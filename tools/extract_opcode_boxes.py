#!/usr/bin/env python3
"""Extract the opcode boxes of SPRU172C chapter 4 from `pdftotext -layout spru172c.pdf` output, with the printed page
of each box.   extract_opcode_boxes.py <spru172c.txt> <out.json>"""
import re, sys, json
lines = open(sys.argv[1], encoding='utf-8').read().split('\n')
start = next(i for i,l in enumerate(lines) if l.lstrip('\f').startswith('ABDST Absolute Distance'))
footer = re.compile(r'(?:^\s*(\d+-\d+)\s+Assembly Language Instructions)|(?:Assembly Language Instructions\s+(\d+-\d+)\s*$)')
hdr = re.compile(r'^(?:Opcode)?(\s*)15\s+14\s+13\s+12\s+11\s+10\s+9\s+8\s+7\s+6\s+5\s+4\s+3\s+2\s+1\s+0\s*$')
title_re = re.compile(r'^([A-Z][A-Z0-9\[\]\|\(\) ]*?)\s{1,}([A-Z][a-z].*)$')
# page label for each line = next footer label after it
page_of = [None]*len(lines); nxt=None
for i in range(len(lines)-1, -1, -1):
    m = footer.search(lines[i])
    if m: nxt = m.group(1) or m.group(2)
    page_of[i] = nxt
out=[]; title=None; syn=None; syntaxes={}
i=start
while i < len(lines):
    l = lines[i].lstrip('\f')
    if footer.search(l) and i+1 < len(lines):
        # next line is the running header with title
        t = lines[i+1].strip()
        if t: title = t
    if l.startswith('Syntax'):
        syntaxes = {}
        j=i
        while j < len(lines) and not lines[j].startswith('Operands') and not lines[j].startswith('Opcode'):
            s = lines[j][len('Syntax'):] if j==i else lines[j]
            m = re.match(r'\s*(\d+):\s+(.*\S)', s)
            if m: syntaxes[int(m.group(1))] = m.group(2)
            elif j==i: syntaxes[0] = s.strip()
            j+=1
    m = re.match(r'^(?:Opcode)?\s*(\d+):\s*$', l)
    if m and i+1<len(lines) and hdr.match(lines[i+1]): syn=int(m.group(1))
    h = hdr.match(l)
    if h:
        cols = [mm.start()+len(mm.group())/2 for mm in re.finditer(r'\d+', l)]
        rows=[]; j=i+1
        while j < len(lines) and lines[j].strip() and not re.match(r'^(Execution|Status|Operands|\s*\d+:\s*$)', lines[j]) and not hdr.match(lines[j]):
            rows.append(lines[j]); j+=1
        words=[]
        for r in rows:
            toks=[(mm.start(), mm.group()) for mm in re.finditer(r'\S+', r)]
            if len(toks)==16 and all(len(t)<=2 for _,t in toks):
                words.append(''.join(t for _,t in toks))
            else:
                words.append('RAW:'+r.strip())
        out.append(dict(page=page_of[i], title=title, syn=syn, syntax=syntaxes.get(syn if syn else 0, syntaxes), words=words, line=i+1))
        syn=None; i=j; continue
    i+=1
json.dump(out, open(sys.argv[2],'w'), indent=1, ensure_ascii=False)
print(len(out))
