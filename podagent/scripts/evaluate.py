#!/usr/bin/env python3
"""
Evaluate a predicted summary against a reference using ROUGE-L and optional BERTScore.
"""
import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from podagent.eval.metrics import compute_bert_score, compute_rouge_l  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Evaluate summaries.")
    parser.add_argument("--reference", required=True, help="Reference summary text.")
    parser.add_argument("--prediction", required=True, help="Model summary text.")
    args = parser.parse_args()

    rouge = compute_rouge_l(args.reference, args.prediction)
    bert = compute_bert_score(args.reference, args.prediction)
    print("ROUGE-L:", rouge)
    print("BERTScore:", bert)


if __name__ == "__main__":
    main()
