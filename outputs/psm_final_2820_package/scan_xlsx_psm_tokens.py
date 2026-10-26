from pathlib import Path
from zipfile import ZipFile, BadZipFile

root=Path(r"C:\Users\user\iCloudDrive\5학기\연구미팅\20240108-2010 to 2015 firms")
tokens=[b"pscore",b"weight",b"pdif",b"pscore2"]
for p in sorted(root.glob("*.xlsx")):
    try:
        with ZipFile(p) as z:
            hits=set()
            data=b"".join(z.read(n) for n in z.namelist() if n.endswith(".xml"))
            low=data.lower()
            for t in tokens:
                if t.lower() in low: hits.add(t.decode())
            if hits:
                print(f"{p.name}\t{p.stat().st_size}\t{','.join(sorted(hits))}")
    except (BadZipFile, OSError) as e:
        print(f"ERROR\t{p.name}\t{e}")
