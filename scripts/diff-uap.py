import re, zipfile, html as h

z = zipfile.ZipFile("/opt/data/profiles/nura/cache/documents/doc_7481106b28b6_UAP_International_Intelligence_Dossier_Final.docx")
xml = z.read("word/document.xml").decode("utf-8", "replace")
text = re.sub(r"</w:p>", "\n", xml)
text = re.sub(r"<w:tab[^>]*/>", "\t", text)
text = re.sub(r"<[^>]+>", "", text)
text = h.unescape(text)
open("/tmp/uap-docx.txt", "w").write(text)

a = open("/tmp/uap-dossier.txt").read()
b = open("/tmp/uap-docx.txt").read()
norm = lambda s: re.sub(r"\s+", " ", s).strip()
na, nb = norm(a), norm(b)
print("pdf chars:", len(na), "| docx chars:", len(nb))
print("IDENTICAL:", na == nb)
if na != nb:
    for i in range(min(len(na), len(nb))):
        if na[i] != nb[i]:
            print("first diff at", i)
            print("PDF:  ...", na[max(0, i - 60):i + 100])
            print("DOCX: ...", nb[max(0, i - 60):i + 100])
            break
    print("ends match:", na[-150:] == nb[-150:])
