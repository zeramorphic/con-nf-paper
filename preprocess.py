import os
import sys
import re

index = ""
if os.path.isfile("index.csv"):
    with open("index.csv", "r") as f:
        index = f.read()
else:
    import urllib.request
    index = urllib.request.urlopen("https://leanprover-community.github.io/con-nf/index.csv").read().decode()
    with open("index.csv", "w") as f:
        f.write(index)

indexDict = {}
for line in index.splitlines():
    (name, module, line, column) = [m.strip() for m in line.split(",")]
    segments = name.split(".")
    for i in range(len(segments)):
        key = ".".join(segments[i:])
        if key not in indexDict:
            indexDict[key] = []
        indexDict[key].append((name, module, line, column))

def convertSmall1(char):
    if ord(char) in range(0x2080, 0x208A):
        return chr(ord(char) - 0x2080 + ord('0'))
    else:
        return char

def convertSmall(name):
    return "".join(convertSmall1(c) for c in name)

def sanitise(name):
    return re.sub(r"[^A-Za-z0-9'._α-ωΑ-Ω]", "_", convertSmall(name))

errored = False

def replaceLean(lean):
    global errored
    if lean[1] not in indexDict:
        print("did not find", lean[1])
        errored = True
        return
    results = indexDict[lean[1]]
    if len(results) == 1:
        (name, module, line, column) = results[0]
        base = "https://leanprover-community.github.io/con-nf/doc/"
        page = "/".join(module.split("."))
        url = base + page + ".html#" + name
        return r"\href{" + url + r"}{\(\forall\)}"
    else:
        print("definition", lean[1], "was ambiguous")
        errored = True

def preprocess(file):
    with open(file, "r") as f:
        contents = f.read()
    contents = re.sub(r"\\lean{(.*)}", replaceLean, contents.replace(".tex", ".l.tex"))
    with open(file[:-4] + ".l.tex", "w") as f:
        f.write(contents)

def walk(dir):
    for f in os.listdir(dir):
        if os.path.isfile(f) and f.endswith(".tex") and not f.endswith(".l.tex"):
            preprocess(os.path.join(dir, f))
        elif os.path.isdir(f):
            if f not in ["build", ".git"]:
                walk(os.path.join(dir, f))

walk(".")

if errored:
    sys.exit(1)
