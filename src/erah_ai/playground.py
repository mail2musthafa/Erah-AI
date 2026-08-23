"""Erah AI Playground - Interactive CLI Deliverable for Phase 01."""

from __future__ import annotations
import sys
import platform
import numpy as np

from erah_ai.foundations.tokenizer import SimpleTokenizer, BPETokenizer
from erah_ai.foundations.embeddings import (
    cosine_similarity,
    euclidean_distance,
    SemanticSearchEngine,
)
from erah_ai.foundations.attention import MultiHeadAttention, scaled_dot_product_attention
from erah_ai.foundations.classifier import IntentClassifier, get_sample_intent_dataset
from erah_ai.foundations.data_lab import DataLab


def print_header(title: str) -> None:
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def run_environment_inspection() -> None:
    print_header("1. Environment & Runtime Inspection")
    print(f"Python Version      : {platform.python_version()} ({platform.python_implementation()})")
    print(f"Operating System    : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"NumPy Version       : {np.__version__}")

    # Check optional ML libs
    for lib in ["torch", "transformers", "sklearn", "pandas"]:
        try:
            mod = __import__(lib)
            ver = getattr(mod, "__version__", "Available")
            print(f"{lib.capitalize():<20}: {ver}")
        except ImportError:
            print(f"{lib.capitalize():<20}: [Not Installed]")


def run_ml_classification() -> None:
    print_header("2. ML Classification & Intent Routing")
    texts, labels = get_sample_intent_dataset()
    print(f"Loaded {len(texts)} training samples across {len(set(labels))} classes: {sorted(list(set(labels)))}")

    clf = IntentClassifier().fit(texts, labels)

    test_queries = [
        "Why was my card billed twice?",
        "Our backend API returned a 500 status code",
        "We want to purchase 20 licenses for our enterprise team",
        "Which regions are your cloud instances hosted in?",
    ]

    print("\nPredicting test customer queries:")
    preds = clf.predict(test_queries)
    for q, p in zip(test_queries, preds):
        print(f"  - Query  : \"{q}\"")
        print(f"    Intent : [bold]{p}[/bold]")

    eval_results = clf.evaluate(texts, labels)
    print(f"\nTraining Set Accuracy: {eval_results['accuracy'] * 100:.1f}%")


def run_tensor_explorer() -> None:
    print_header("3. Tensor & Matrix Math Explorer")
    print("Generating simulated token embeddings (batch_size=2, seq_len=4, d_model=8)...")
    rng = np.random.RandomState(42)
    tensors = rng.randn(2, 4, 8)
    print(f"Tensor Shape: {tensors.shape}")
    print(f"L2 Norm per token vector:\n{np.linalg.norm(tensors, axis=-1)}")
    print(f"Mean: {tensors.mean():.4f}, Std: {tensors.std():.4f}")


def run_tokenizer_explorer() -> None:
    print_header("4. Tokenizer & Subword BPE Explorer")
    sample_corpus = [
        "Erah AI connects governed AI agents to real business data and tools.",
        "Production AI systems require robust tokenization and evaluation.",
        "Agents understand, reason, retrieve, act, and respond in multiple languages.",
    ]

    bpe = BPETokenizer(vocab_size=60)
    bpe.train(sample_corpus)

    test_sentence = "Erah AI agents understand business tools"
    encoded_ids = bpe.encode(test_sentence)
    decoded_text = bpe.decode(encoded_ids)
    compression = bpe.get_compression_ratio(test_sentence)

    print(f"Trained BPE Vocab Size : {len(bpe.vocab)} tokens")
    print(f"Input Sentence         : \"{test_sentence}\"")
    print(f"Encoded Token IDs      : {encoded_ids}")
    print(f"Decoded Text           : \"{decoded_text}\"")
    print(f"Compression Ratio      : {compression:.2f} chars/token")


def run_embedding_similarity() -> None:
    print_header("5. Embedding Similarity Math")
    rng = np.random.RandomState(42)
    v1 = rng.randn(64)
    v2 = v1 + rng.randn(64) * 0.2  # Similar vector
    v3 = -v1 + rng.randn(64) * 0.2  # Dissimilar / opposite vector

    print(f"Vector 1 vs Similar Vector 2    - Cosine Similarity: {cosine_similarity(v1, v2):.4f}")
    print(f"Vector 1 vs Dissimilar Vector 3 - Cosine Similarity: {cosine_similarity(v1, v3):.4f}")
    print(f"Vector 1 vs Vector 1 (Self)     - Cosine Similarity: {cosine_similarity(v1, v1):.4f}")
    print(f"Euclidean Distance (v1, v2)     : {euclidean_distance(v1, v2):.4f}")


def run_semantic_search() -> None:
    print_header("6. In-Memory Semantic Search Engine")
    engine = SemanticSearchEngine(embedding_dim=64)

    documents = [
        ("doc_1", "How to configure customer invoice and billing refund settings", {"category": "billing"}),
        ("doc_2", "Troubleshooting 500 internal server error and connection timeouts", {"category": "tech"}),
        ("doc_3", "Enterprise licensing, pricing calculator, and volume discounts", {"category": "sales"}),
        ("doc_4", "Multi-agent control tower architecture and security policies", {"category": "architecture"}),
    ]
    engine.add_documents(documents)
    print(f"Indexed {len(documents)} knowledge documents in-memory.")

    query = "I have an issue with subscription payment"
    print(f"\nQuery: \"{query}\"")
    results = engine.search(query, top_k=2)
    for i, res in enumerate(results, 1):
        print(f"  {i}. [Score: {res['score']:.4f}] {res['id']}: \"{res['text']}\" (Category: {res['metadata'].get('category')})")


def run_transformer_attention() -> None:
    print_header("7. Multi-Head Self-Attention & Causal Masking")
    seq_len = 4
    d_model = 16
    num_heads = 2

    print(f"Initializing Multi-Head Attention (d_model={d_model}, heads={num_heads})...")
    mha = MultiHeadAttention(d_model=d_model, num_heads=num_heads)

    rng = np.random.RandomState(42)
    sample_input = rng.randn(1, seq_len, d_model)

    # Autoregressive Causal Attention
    output, attention_weights = mha.forward(sample_input, causal=True)
    print(f"Output Shape: {output.shape}")
    print(f"Attention Weights Shape (batch, heads, seq, seq): {attention_weights.shape}")
    print("\nCausal Attention Matrix (Head 0):\n", np.round(attention_weights[0, 0], 3))


def run_experiment_report() -> None:
    print_header("8. Phase 01 Engineering Experiment Report")
    print("Generating comprehensive Phase 01 summary:")
    print("  ✓ NumPy Vectorization & Linear Algebra")
    print("  ✓ Pure Subword Byte-Pair Encoding (BPE)")
    print("  ✓ Scaled Dot-Product & Multi-Head Self-Attention")
    print("  ✓ In-Memory Semantic Vector Search Engine")
    print("  ✓ Intent Classifier & Risk Evaluation Pipeline")
    print("  ✓ Data Lab Dataset Profiler & Deduplicator")
    print("\nPhase 01 status: ALL FOUNDATIONS READY.")


def main() -> None:
    menu = """
=================================================================
                 ERAH AI — FOUNDATIONS PLAYGROUND
                Phase 01: AI Foundations & Mechanics
=================================================================
1. Environment Inspection
2. ML Classification
3. Tensor Explorer
4. Tokenizer Explorer
5. Embedding Similarity
6. Semantic Search
7. Transformer Multi-Head Attention
8. Experiment Report
9. Run All Demos
0. Exit
=================================================================
"""
    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print(menu)
        choice = input("Select an option (0-9): ").strip()

    actions = {
        "1": run_environment_inspection,
        "2": run_ml_classification,
        "3": run_tensor_explorer,
        "4": run_tokenizer_explorer,
        "5": run_embedding_similarity,
        "6": run_semantic_search,
        "7": run_transformer_attention,
        "8": run_experiment_report,
    }

    if choice == "9":
        for num in sorted(actions.keys()):
            actions[num]()
    elif choice in actions:
        actions[choice]()
    elif choice == "0":
        print("Exiting Erah AI Playground. Goodbye!")
    else:
        print(f"Invalid option: {choice}")


if __name__ == "__main__":
    main()
