"""Run frozen renderer on in-memory synthetic fixtures, never benchmark outputs."""
import argparse
import json
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import test_bench001 as fixture

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", required=True)
    parser.add_argument("--playwright", required=True)
    parser.add_argument("--browser", required=True)
    args = parser.parse_args()
    h = fixture.h
    current = h.run_arm("C0", 1, fixture.SOURCE, fixture.Fake([fixture.extraction()]), h.RunLedger())
    neutral = h.run_arm("A", 1, fixture.SOURCE, fixture.Fake([fixture.envelope()]), h.RunLedger())
    artifacts = fixture.freeze.build()
    payload = {"kind": "SYNTHETIC_OFFLINE_CONTRACT_TEST",
        "current_html": h.render_output(current["output"]),
        "current_focus_count": len(current["output"]["plans"]),
        "neutral_html": [h.render_output({"source":fixture.SOURCE}), h.render_output(neutral["output"])],
        "styles": {n.rsplit("/",1)[-1]:b.decode() for n,b in artifacts.items() if n.startswith("renderer/") and n.endswith(".css")},
        "scripts": {n.rsplit("/",1)[-1]:b.decode() for n,b in artifacts.items() if n.startswith("renderer/") and n.endswith(".js")}}
    result = subprocess.run([args.node,str(ROOT/"tools/bench001_renderer_check.mjs")],
        input=json.dumps(payload),text=True,capture_output=True,
        env={**os.environ,"BENCH_PLAYWRIGHT":args.playwright,"BENCH_BROWSER_EXECUTABLE":args.browser})
    print(result.stdout, end="");print(result.stderr, end="",file=sys.stderr)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
