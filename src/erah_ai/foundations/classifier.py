"""Customer query intent classification & risk assessment module."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np


class IntentClassifier:
    """Scikit-Learn based text classifier for customer intent routing and risk scoring."""

    def __init__(self):
        self.classes_: list[str] = []
        self.is_fitted = False
        self._pipeline = None

    def fit(self, texts: list[str], labels: list[str]) -> IntentClassifier:
        """Fit TF-IDF + Classifier pipeline on training data."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.linear_model import LogisticRegression
            from sklearn.pipeline import make_pipeline

            self.classes_ = sorted(list(set(labels)))
            self._pipeline = make_pipeline(
                TfidfVectorizer(ngram_range=(1, 2), max_features=5000),
                LogisticRegression(max_iter=1000, random_state=42),
            )
            self._pipeline.fit(texts, labels)
            self.is_fitted = True
            return self
        except ImportError:
            # Fallback lightweight heuristic if scikit-learn is not installed in current environment
            self.classes_ = sorted(list(set(labels)))
            self.is_fitted = True
            return self

    def predict(self, texts: list[str]) -> list[str]:
        """Predict intent label for texts."""
        if not self.is_fitted:
            raise ValueError("Classifier has not been trained yet. Call fit() first.")

        if self._pipeline is not None:
            return list(self._pipeline.predict(texts))

        # Fallback simple keyword classifier
        preds = []
        for t in texts:
            t_low = t.lower()
            if any(w in t_low for w in ["refund", "billing", "invoice", "payment", "charge"]):
                preds.append("billing")
            elif any(w in t_low for w in ["broken", "error", "bug", "fail", "not working"]):
                preds.append("tech_support")
            elif any(w in t_low for w in ["buy", "upgrade", "pricing", "plan", "cost"]):
                preds.append("sales")
            else:
                preds.append("general_inquiry")
        return preds

    def evaluate(
        self, texts: list[str], labels: list[str]
    ) -> dict[str, Any]:
        """Evaluate model and return accuracy, precision, recall, and F1."""
        predictions = self.predict(texts)
        total = len(labels)
        correct = sum(1 for p, y in zip(predictions, labels) if p == y)
        accuracy = correct / max(1, total)

        # Compute per-class precision and recall
        class_metrics = {}
        for c in self.classes_:
            tp = sum(1 for p, y in zip(predictions, labels) if p == c and y == c)
            fp = sum(1 for p, y in zip(predictions, labels) if p == c and y != c)
            fn = sum(1 for p, y in zip(predictions, labels) if p != c and y == c)

            prec = tp / max(1, tp + fp)
            rec = tp / max(1, tp + fn)
            f1 = 2 * (prec * rec) / max(1e-9, prec + rec)
            class_metrics[c] = {"precision": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4)}

        return {
            "total_samples": total,
            "accuracy": round(accuracy, 4),
            "class_metrics": class_metrics,
        }


def get_sample_intent_dataset() -> tuple[list[str], list[str]]:
    """Return a multilingual customer support sample dataset for testing."""
    samples = [
        # Billing
        ("I was charged twice on my credit card last month", "billing"),
        ("Please send me the invoice for my subscription", "billing"),
        ("Can I get a refund for the unused days?", "billing"),
        ("My payment failed but money was deducted", "billing"),
        ("Where can I download tax receipts?", "billing"),
        ("Update my credit card details", "billing"),
        # Tech Support
        ("The API is throwing a 500 Internal Server Error", "tech_support"),
        ("Login authentication token keeps expiring instantly", "tech_support"),
        ("System crashes every time I upload a PDF", "tech_support"),
        ("I cannot connect to the WebSocket streaming endpoint", "tech_support"),
        ("Database migration script failed with constraint error", "tech_support"),
        ("App freezes on the dashboard page", "tech_support"),
        # Sales
        ("What are the pricing tiers for enterprise scale?", "sales"),
        ("We want to upgrade our plan from Pro to Enterprise", "sales"),
        ("Can we schedule a product demo with your team?", "sales"),
        ("Do you offer discounts for annual commitments?", "sales"),
        ("How many team seats are included in the Business tier?", "sales"),
        ("Requesting a quote for 50 developer licenses", "sales"),
        # General Inquiry
        ("What languages does Erah AI support?", "general_inquiry"),
        ("Where are your data centers located?", "general_inquiry"),
        ("What is your SLA for response times?", "general_inquiry"),
        ("Is there a public roadmap for upcoming features?", "general_inquiry"),
        ("How do I contact your media relations team?", "general_inquiry"),
        ("Tell me more about Erah AI ecosystem architecture", "general_inquiry"),
    ]
    texts, labels = zip(*samples)
    return list(texts), list(labels)
