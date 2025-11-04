import subprocess
import sys
from pathlib import Path

print("Script start")

def run(cmd):
    print("RUNNING COMMAND: ")
    print(" ".join(cmd))
    return subprocess.run(cmd, stdout=subprocess.PIPE, text=True).stdout

def clear_betti():
    b = Path('.') / 'betti'
    b.mkdir(exist_ok=True)
    for k in range(5):
        out = b / f'behavior{k}'
        out.mkdir(parents=True, exist_ok=True)
        for f in out.glob('flock*_h?.txt'):
            f.unlink()

def gen_betti():
    rg_0 = Path('../PHoDMSs') / 'betti_generator.py'
    rg_1 = Path('../PHoDMSs') / 'rank_generator.py'
    for k in range(5):
        for i in range(10):
            infile = Path('.') / f'behavior{k}' / f'flock{i}.txt.old'
            outdir = Path('.') / 'betti' / f'behavior{k}'
            run([sys.executable, str(rg_0), str(infile), str(outdir / f'flock{i}_h0.txt'), '0', '300', '6', '50'])
            run([sys.executable, str(rg_1), str(infile), str(outdir / f'flock{i}_h1.txt'), '0', '300', '25', '12', '1'])

def collect(h):
    files = []
    for k in range(5):
        for i in range(10):
            files.append(str(Path('.') / 'betti' / f'behavior{k}' / f'flock{i}_h{h}.txt'))
    return files

def distmat(files, out, script_name):
    n = len(files)
    m = [[0.0] * n for _ in range(n)]
    er = Path('../PHoDMSs') / script_name
    for i in range(n):
        for j in range(i + 1, n):
            o = run([sys.executable, str(er), files[i], files[j]])
            print(o)
            m[i][j] = m[j][i] = float(o.strip())
    with open(out, 'w') as f:
        for row in m:
            f.write(" ".join(map(str, row)) + "\n")

clear_betti()
print("Starting betti generation")
gen_betti()
h0 = collect(0)
h1 = collect(1)
distmat(h0, Path('.') / 'betti' / 'dist_mat_h0.txt', 'betti0_erosion_distance.py')
distmat(h1, Path('.') / 'betti' / 'dist_mat_h1.txt', 'rank_erosion.py')
