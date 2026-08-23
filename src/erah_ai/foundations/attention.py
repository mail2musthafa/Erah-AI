"""Transformer mechanics: Scaled dot-product attention, multi-head attention, and causal masking."""

from __future__ import annotations
import numpy as np
from typing import Tuple, Optional


def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically stable softmax."""
    e_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
    return e_x / np.sum(e_x, axis=axis, keepdims=True)


def create_causal_mask(seq_len: int) -> np.ndarray:
    """Create a causal upper-triangular mask (0 for visible tokens, -inf for future tokens)."""
    mask = np.triu(np.ones((seq_len, seq_len)), k=1)
    mask = np.where(mask == 1, -1e9, 0.0)
    return mask


def scaled_dot_product_attention(
    q: np.ndarray,
    k: np.ndarray,
    v: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Scaled Dot-Product Attention: Attention(Q, K, V) = softmax(Q * K^T / sqrt(d_k) + Mask) * V.

    Args:
        q: Query matrix of shape (..., seq_len_q, d_k)
        k: Key matrix of shape (..., seq_len_k, d_k)
        v: Value matrix of shape (..., seq_len_k, d_v)
        mask: Optional mask matrix of shape (..., seq_len_q, seq_len_k)

    Returns:
        output: Attended values of shape (..., seq_len_q, d_v)
        attention_weights: Attention matrix of shape (..., seq_len_q, seq_len_k)
    """
    d_k = q.shape[-1]
    # Matrix multiplication: Q * K^T
    scores = np.matmul(q, np.swapaxes(k, -2, -1)) / np.sqrt(d_k)

    if mask is not None:
        scores = scores + mask

    attention_weights = softmax(scores, axis=-1)
    output = np.matmul(attention_weights, v)
    return output, attention_weights


class MultiHeadAttention:
    """Multi-Head Self-Attention implemented with NumPy.

    Splits embedding into H heads, computes scaled dot-product attention in parallel,
    and projects back to model dimension.
    """

    def __init__(self, d_model: int = 64, num_heads: int = 4, seed: int = 42):
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        rng = np.random.RandomState(seed)
        # Weight matrices for Q, K, V projections and Output projection
        self.w_q = rng.randn(d_model, d_model) * 0.02
        self.w_k = rng.randn(d_model, d_model) * 0.02
        self.w_v = rng.randn(d_model, d_model) * 0.02
        self.w_o = rng.randn(d_model, d_model) * 0.02

    def forward(
        self, x: np.ndarray, causal: bool = False
    ) -> tuple[np.ndarray, np.ndarray]:
        """Forward pass for multi-head attention.

        Args:
            x: Input embeddings of shape (batch_size, seq_len, d_model)
            causal: Whether to apply autoregressive causal masking
        """
        batch_size, seq_len, _ = x.shape

        # Linear projections
        q = np.dot(x, self.w_q)
        k = np.dot(x, self.w_k)
        v = np.dot(x, self.w_v)

        # Reshape for multi-head: (batch, seq_len, num_heads, d_k) -> (batch, num_heads, seq_len, d_k)
        q = q.reshape(batch_size, seq_len, self.num_heads, self.d_k).swapaxes(1, 2)
        k = k.reshape(batch_size, seq_len, self.num_heads, self.d_k).swapaxes(1, 2)
        v = v.reshape(batch_size, seq_len, self.num_heads, self.d_k).swapaxes(1, 2)

        mask = create_causal_mask(seq_len) if causal else None

        # Compute scaled dot product attention for all heads
        attn_out, attn_weights = scaled_dot_product_attention(q, k, v, mask=mask)

        # Recombine heads: (batch, num_heads, seq_len, d_k) -> (batch, seq_len, d_model)
        attn_out = attn_out.swapaxes(1, 2).reshape(batch_size, seq_len, self.d_model)

        # Output projection
        output = np.dot(attn_out, self.w_o)
        return output, attn_weights
