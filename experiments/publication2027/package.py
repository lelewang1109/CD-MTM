"""Package public RG-MTM code/results; exclude manuscripts and raw inputs."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=ROOT / 'output/rgmtm')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    listed = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=ROOT)
    files = sorted({Path(name.decode()) for name in listed.split(b'\0') if name})
    bundle = args.out / 'RG-MTM-code-results.zip'
    with zipfile.ZipFile(bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
        for relative in files:
            source = ROOT / relative
            if not source.is_file() or source.is_symlink():
                continue
            if relative.parts[0] in {'output', 'tmp', '.venv', 'paper', 'notes', 'publications'}:
                continue
            if relative.parts[0] == 'data' and relative.parts[1] != 'geo' and relative.name != 'README.md':
                continue
            if relative.parts[0] == 'references' and source.suffix == '.pdf':
                continue
            archive.write(source, Path('RG-MTM') / relative)
    artifacts = {f.name: dict(bytes=f.stat().st_size, sha256=hashlib.sha256(f.read_bytes()).hexdigest())
                 for f in args.out.iterdir() if f.is_file() and f.name.startswith('RG-MTM-')}
    (args.out / 'manifest.json').write_text(json.dumps(artifacts, indent=2) + '\n')
    print('Packaged RG-MTM code/results (no manuscripts):', args.out)


if __name__ == '__main__':
    main()
