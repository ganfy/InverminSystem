with open("src/router/nav.ts", encoding="utf-8") as f:
    c = f.read()

lines = c.split("\n")
for i, line in enumerate(lines):
    if "'Comercial'," in line and "'JefeComercial'" not in line:
        lines[i] = line.replace("'Comercial',", "'Comercial', 'JefeComercial',")
    if "'Comercial']" in line and "'JefeComercial'" not in line:
        lines[i] = line.replace("'Comercial']", "'Comercial', 'JefeComercial']")

with open("src/router/nav.ts", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
