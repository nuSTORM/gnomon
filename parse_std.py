f = open('std')
for line in f:
    if 'dist' not in line or ')' not in line or '(' not in line:
        continue
    
    x,y,z = line.split()[1][1:-1].split(',')
    print x, y, z
f.close()
