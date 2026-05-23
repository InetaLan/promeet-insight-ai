from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd
from .pipeline import process_transcript, save_result, save_jira_payloads


def iter_files(input_dir: Path):
    for ext in ("*.docx", "*.txt"):
        yield from sorted(input_dir.glob(ext))


def main():
    parser = argparse.ArgumentParser(description="ProMeet Insight AI MVP pipeline")
    parser.add_argument("--input-dir", required=True, help="Folder with .docx/.txt transcripts")
    parser.add_argument("--output-dir", default="data/outputs", help="Folder for JSON outputs")
    parser.add_argument("--use-openai", action="store_true", help="Use GPT-4o extraction if OPENAI_API_KEY is set")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for file in iter_files(input_dir):
        result = process_transcript(file, use_openai=args.use_openai)
        result_path = save_result(result, output_dir)
        jira_path = save_jira_payloads(result, output_dir)

        rows.append({
            "transcript": file.name,
            "segments": result.validation_summary.get("segment_count"),
            "validation_status": result.validation_summary.get("status"),
            "tasks": len(result.tasks),
            "decisions": len(result.decisions),
            "risks": len(result.risks),
            "mode": result.validation_summary.get("extraction_mode"),
            "result_json": str(result_path),
            "jira_payloads": str(jira_path),
        })

    df = pd.DataFrame(rows)
    summary_path = output_dir / "mvp_summary.csv"
    df.to_csv(summary_path, index=False, encoding="utf-8")
    print(df.to_string(index=False))
    print(f"\nSaved summary: {summary_path}")


if __name__ == "__main__":
    main()
