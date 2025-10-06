import re
import numpy as np
from pathlib import Path

def read_mats(path):
    txt = Path(path).read_text()
    blocks = re.split(r'\n\s*\n', txt.strip())
    def block_to_matrix(block):
        rows = [line.strip() for line in block.strip().splitlines() if line.strip() != ""]
        data = [list(map(float, re.split(r'\s+', row))) for row in rows]
        return np.array(data, dtype=float)
    return block_to_matrix(blocks[0]), block_to_matrix(blocks[1])

def write_matrix(path, mat):
    with open(path, 'w') as f:
        for row in mat:
            f.write(" ".join(f"{float(x):.9g}" for x in row) + "\n")

def rescale_mats(A, B):
    gA = np.exp(np.mean(np.log(A[A != 0])))
    gB = np.exp(np.mean(np.log(B[B != 0])))
    if gA == 0.0:
        gA = float(np.mean(A))
    if gB == 0.0:
        gB = float(np.mean(B))
    if gA <= 0 or gB <= 0:
        return A.copy(), B.copy()
    target = float((gA * gB) ** 0.5)
    sA = target / gA
    sB = target / gB
    return A * sA, B * sB
