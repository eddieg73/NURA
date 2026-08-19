import sys
sys.path.insert(0, "/opt/data/profiles/nura/python-packages")
import fitz

doc = fitz.open("/opt/data/profiles/nura/cache/documents/doc_f5660252dae1_UAP_International_Intelligence_Dossier_Final.pdf")
print("pages:", len(doc))
total = []
for i, page in enumerate(doc):
    t = page.get_text()
    total.append(f"--- PAGE {i+1} ---\n{t}")
out = "\n".join(total)
open("/tmp/uap-dossier.txt", "w").write(out)
print("chars:", len(out))
print(out[:1500])
