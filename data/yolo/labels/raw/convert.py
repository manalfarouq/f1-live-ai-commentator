import json
import os
import glob

CLASSES = ["in pit",
           "Yellow exclamation mark",
           "Red exclamation mark",
           "purple stopwatch icon",
           "Yellow flag",
           "Virtual Safety Car",
           "Checkered",
           "Green flag",
           "Safety Car",
           "out",
           "Red flag",
           "VSC ending"
           ]

for json_file in glob.glob("*.json"):
    with open(json_file) as f:
        data = json.load(f)

    w = data["imageWidth"]
    h = data["imageHeight"]
    lines = []

    for shape in data["shapes"]:
        if shape["label"] not in CLASSES:
            print(f"⚠️  Label inconnu ignoré : '{shape['label']}' dans {json_file}")
            continue
        cls = CLASSES.index(shape["label"])
        pts = shape["points"]
        x1, y1 = min(pts[0][0], pts[1][0]), min(pts[0][1], pts[1][1])
        x2, y2 = max(pts[0][0], pts[1][0]), max(pts[0][1], pts[1][1])
        cx, cy = ((x1+x2)/2)/w, ((y1+y2)/2)/h
        bw, bh = (x2-x1)/w, (y2-y1)/h
        lines.append(f"{cls} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")

    name = json_file.replace(".json", ".txt")
    with open(name, "w") as f:          # ← écrit dans le dossier courant
        f.write("\n".join(lines))
    print(f"✅ {name}")

print("Terminé !")