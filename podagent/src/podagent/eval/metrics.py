from typing import Dict, Tuple


def compute_rouge_l(reference: str, prediction: str) -> Dict[str, float]:
    """
    Compute ROUGE-L using rouge-score if available; otherwise return zeros.
    """
    try:
        from rouge_score import rouge_scorer  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        return {"rougeL_f": 0.0, "rougeL_p": 0.0, "rougeL_r": 0.0}

    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = scorer.score(reference, prediction)["rougeL"]
    return {"rougeL_f": scores.fmeasure, "rougeL_p": scores.precision, "rougeL_r": scores.recall}


def compute_bert_score(reference: str, prediction: str) -> Dict[str, float]:
    """
    Compute BERTScore if the package is installed; otherwise return zeros.
    """
    try:
        from bert_score import score  # type: ignore
    except Exception:  # pragma: no cover - optional dependency
        return {"bert_p": 0.0, "bert_r": 0.0, "bert_f1": 0.0}

    P, R, F1 = score([prediction], [reference], lang="en", verbose=False)
    return {"bert_p": float(P.mean()), "bert_r": float(R.mean()), "bert_f1": float(F1.mean())}
