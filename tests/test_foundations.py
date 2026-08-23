"""Unit tests for Phase 01: Foundations & Model Mechanics."""

import numpy as np
import pytest

from erah_ai.foundations.tokenizer import SimpleTokenizer, BPETokenizer
from erah_ai.foundations.embeddings import (
    cosine_similarity,
    euclidean_distance,
    SemanticSearchEngine,
)
from erah_ai.foundations.attention import (
    scaled_dot_product_attention,
    MultiHeadAttention,
    create_causal_mask,
)
from erah_ai.foundations.classifier import IntentClassifier, get_sample_intent_dataset
from erah_ai.foundations.data_lab import DataLab


def test_simple_tokenizer():
    tok = SimpleTokenizer()
    corpus = ["Hello world!", "Welcome to Erah AI."]
    tok.fit(corpus)
    encoded = tok.encode("Hello Erah")
    decoded = tok.decode(encoded)
    assert len(encoded) == 2
    assert "Hello" in decoded


def test_bpe_tokenizer():
    bpe = BPETokenizer(vocab_size=50)
    corpus = ["low lower lowest new newer newest"]
    bpe.train(corpus)
    encoded = bpe.encode("lowest")
    decoded = bpe.decode(encoded)
    assert len(encoded) > 0
    assert "lowest" in decoded


def test_vector_similarity():
    v1 = np.array([1.0, 0.0, 0.0])
    v2 = np.array([1.0, 0.0, 0.0])
    v3 = np.array([0.0, 1.0, 0.0])

    assert np.isclose(cosine_similarity(v1, v2), 1.0)
    assert np.isclose(cosine_similarity(v1, v3), 0.0)
    assert np.isclose(euclidean_distance(v1, v2), 0.0)


def test_semantic_search_engine():
    engine = SemanticSearchEngine(embedding_dim=32)
    engine.add_document("doc1", "Billing and invoices", {"category": "billing"})
    engine.add_document("doc2", "Database crash error", {"category": "tech"})

    results = engine.search("Billing details", top_k=1)
    assert len(results) == 1
    assert "score" in results[0]


def test_scaled_dot_product_attention():
    q = np.ones((1, 2, 4))
    k = np.ones((1, 2, 4))
    v = np.ones((1, 2, 4))
    out, weights = scaled_dot_product_attention(q, k, v)

    assert out.shape == (1, 2, 4)
    assert weights.shape == (1, 2, 2)
    assert np.allclose(np.sum(weights, axis=-1), 1.0)


def test_multi_head_attention_causal():
    mha = MultiHeadAttention(d_model=16, num_heads=2)
    x = np.random.randn(1, 4, 16)
    out, weights = mha.forward(x, causal=True)

    assert out.shape == (1, 4, 16)
    assert weights.shape == (1, 2, 4, 4)
    # Check upper triangle is 0 (future tokens masked)
    for h in range(2):
        for i in range(4):
            for j in range(i + 1, 4):
                assert weights[0, h, i, j] == 0.0


def test_intent_classifier():
    texts, labels = get_sample_intent_dataset()
    clf = IntentClassifier().fit(texts, labels)
    preds = clf.predict(["I need an invoice", "500 server error"])
    assert len(preds) == 2
    metrics = clf.evaluate(texts, labels)
    assert metrics["accuracy"] >= 0.8


def test_data_lab_deduplication():
    lab = DataLab([
        {"question": "How to pay?", "language": "en"},
        {"question": "how to pay?", "language": "en"},
        {"question": "Comment payer?", "language": "fr"},
    ])
    orig, rem = lab.deduplicate("question")
    assert orig == 3
    assert rem == 2
    assert lab.profile_languages() == {"en": 1, "fr": 1}
