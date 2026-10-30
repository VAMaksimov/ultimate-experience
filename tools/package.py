"""Package only original source and declared assets, never dependencies."""
from pathlib import Path
import hashlib, zipfile, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'
OUT.mkdir(exist_ok=True)
manifest=ET.parse(ROOT/'UltimateExperience.modinfo').getroot()
runtime=['UltimateExperience.modinfo','LICENSE','README.md','COLLECTION.md','TESTING.md','ROADMAP.md','RELEASE_NOTES.md','installed-mods.json']+[f.text for f in manifest.findall('Files/File')]
source=runtime+['.gitignore']+[p.relative_to(ROOT).as_posix() for folder in ['tools','tests'] for p in (ROOT/folder).glob('*.py')]
for kind,files in [('mod',runtime),('source',source)]:
    path=OUT/f'ultimate-experience-0.1.0-rc.1-{kind}.zip'
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(files)):
            file=(ROOT/name).resolve()
            if not file.is_relative_to(ROOT) or not file.is_file(): raise ValueError(name)
            archive.write(file,'Ultimate_Experience/'+name)
    print(path.name,hashlib.sha256(path.read_bytes()).hexdigest())
