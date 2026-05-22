import requests
from pathlib import Path

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def fetch_full_text_xml():
    url = "https://www.ecfr.gov/api/versioner/v1/full/current/title-29.xml?part=1910"
    fallback_url = "https://www.ecfr.gov/api/versioner/v1/full/2024-01-01/title-29.xml?part=1910"
    
    print("Downloading 29 CFR Part 1910 from eCFR...")
    
    for attempt_url in [url, fallback_url]:
        try:
            resp = requests.get(attempt_url, stream=True, timeout=60)
            if resp.status_code == 200:
                out_path = OUTPUT_DIR / "cfr_29_part1910.xml"
                with open(out_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                size = out_path.stat().st_size / 1e6
                print(f"Saved to {out_path} ({size:.1f} MB)")
                return out_path
            else:
                print(f"URL returned {resp.status_code}, trying fallback...")
        except Exception as e:
            print(f"Error: {e}, trying fallback...")
    
    raise Exception("Could not download from eCFR. Check your internet connection.")

if __name__ == "__main__":
    fetch_full_text_xml()