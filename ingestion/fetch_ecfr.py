import requests
from pathlib import Path

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# All major OSHA parts under Title 29
OSHA_PARTS = [
    {"part": "1903", "title": "Inspections, Citations and Proposed Penalties"},
    {"part": "1904", "title": "Recording and Reporting Occupational Injuries and Illnesses"},
    {"part": "1910", "title": "Occupational Safety and Health Standards (General Industry)"},
    {"part": "1915", "title": "Occupational Safety and Health Standards for Shipyard Employment"},
    {"part": "1926", "title": "Safety and Health Regulations for Construction"},
]

def fetch_part(part_number):
    urls = [
        f"https://www.ecfr.gov/api/versioner/v1/full/current/title-29.xml?part={part_number}",
        f"https://www.ecfr.gov/api/versioner/v1/full/2024-01-01/title-29.xml?part={part_number}",
    ]
    out_path = OUTPUT_DIR / f"cfr_29_part{part_number}.xml"

    if out_path.exists():
        print(f"  Part {part_number}: using cached file")
        return out_path

    for url in urls:
        try:
            resp = requests.get(url, stream=True, timeout=120)
            if resp.status_code == 200:
                with open(out_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                size = out_path.stat().st_size / 1e6
                print(f"  Part {part_number}: saved ({size:.1f} MB)")
                return out_path
            else:
                print(f"  Part {part_number}: URL returned {resp.status_code}, trying fallback...")
        except Exception as e:
            print(f"  Part {part_number}: error {e}, trying fallback...")

    print(f"  Part {part_number}: FAILED to download")
    return None

def fetch_all_parts():
    print("Downloading all OSHA CFR parts...")
    paths = []
    for p in OSHA_PARTS:
        print(f"\nFetching 29 CFR Part {p['part']} - {p['title']}")
        path = fetch_part(p["part"])
        if path:
            paths.append({"path": path, **p})
    print(f"\nDone. {len(paths)}/{len(OSHA_PARTS)} parts downloaded.")
    return paths

if __name__ == "__main__":
    fetch_all_parts()