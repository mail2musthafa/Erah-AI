"""Tokenizer and Byte-Pair Encoding (BPE) mechanics for Erah AI."""

from __future__ import annotations
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple


class SimpleTokenizer:
    """A whitespace & punctuation regex tokenizer with special token handling."""

    def __init__(self, special_tokens: list[str] | None = None):
        self.special_tokens = special_tokens or ["<PAD>", "<UNK>", "<BOS>", "<EOS>"]
        self.vocab: dict[str, int] = {tok: idx for idx, tok in enumerate(self.special_tokens)}
        self.inverse_vocab: dict[int, str] = {idx: tok for tok, idx in self.vocab.items()}

    def fit(self, texts: list[str]) -> None:
        """Build vocabulary from corpus."""
        tokens = set()
        for text in texts:
            tokens.update(self._tokenize_raw(text))
        for token in sorted(tokens):
            if token not in self.vocab:
                idx = len(self.vocab)
                self.vocab[token] = idx
                self.inverse_vocab[idx] = token

    def _tokenize_raw(self, text: str) -> list[str]:
        # Split words and punctuation
        pattern = r"\w+|[^\w\s]"
        return re.findall(pattern, text.strip())

    def encode(self, text: str) -> list[int]:
        """Convert text into token IDs."""
        tokens = self._tokenize_raw(text)
        unk_id = self.vocab.get("<UNK>", 1)
        return [self.vocab.get(tok, unk_id) for tok in tokens]

    def decode(self, ids: list[int]) -> str:
        """Convert token IDs back to text."""
        return " ".join([self.inverse_vocab.get(i, "<UNK>") for i in ids])

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)


class BPETokenizer:
    """Byte-Pair Encoding (BPE) tokenizer implemented from first principles.

    Demonstrates how subword tokenizers like GPT-2/4, LLaMA, and BERT are trained
    and how text is segmented into subwords.
    """

    def __init__(self, vocab_size: int = 300):
        self.target_vocab_size = vocab_size
        self.merges: dict[tuple[str, str], str] = {}
        self.vocab: dict[str, int] = {}
        self.inverse_vocab: dict[int, str] = {}

    def _get_stats(self, word_freqs: dict[tuple[str, ...], int]) -> dict[tuple[str, str], int]:
        """Count frequencies of adjacent symbol pairs."""
        pairs: dict[tuple[str, str], int] = defaultdict(int)
        for word, freq in word_freqs.items():
            for i in range(len(word) - 1):
                pair = (word[i], word[i + 1])
                pairs[pair] += freq
        return pairs

    def _merge_vocab(
        self, pair: tuple[str, str], word_freqs: dict[tuple[str, ...], int]
    ) -> dict[tuple[str, ...], int]:
        """Merge most frequent pair in all word representations."""
        new_word_freqs: dict[tuple[str, ...], int] = {}
        bigram = pair
        replacement = "".join(pair)
        for word, freq in word_freqs.items():
            new_word = []
            i = 0
            while i < len(word):
                if i < len(word) - 1 and (word[i], word[i + 1]) == bigram:
                    new_word.append(replacement)
                    i += 2
                else:
                    new_word.append(word[i])
                    i += 1
            new_word_freqs[tuple(new_word)] = freq
        return new_word_freqs

    def train(self, texts: list[str]) -> None:
        """Train BPE merge rules on corpus."""
        # Initialize word frequencies with character splits and end-of-word symbol </w>
        raw_words = []
        for text in texts:
            words = re.findall(r"\w+|[^\w\s]", text)
            raw_words.extend(words)

        word_counts = Counter(raw_words)
        word_freqs: dict[tuple[str, ...], int] = {
            tuple(list(w) + ["</w>"]): count for w, count in word_counts.items()
        }

        # Initialize base vocab with all unique characters
        unique_chars = set()
        for word in word_freqs:
            unique_chars.update(word)

        self.vocab = {"<PAD>": 0, "<UNK>": 1, "<BOS>": 2, "<EOS>": 3}
        for char in sorted(unique_chars):
            if char not in self.vocab:
                self.vocab[char] = len(self.vocab)

        num_merges = max(0, self.target_vocab_size - len(self.vocab))
        for _ in range(num_merges):
            pairs = self._get_stats(word_freqs)
            if not pairs:
                break
            best_pair = max(pairs, key=pairs.get)
            merged_token = "".join(best_pair)

            word_freqs = self._merge_vocab(best_pair, word_freqs)
            self.merges[best_pair] = merged_token

            if merged_token not in self.vocab:
                self.vocab[merged_token] = len(self.vocab)

        self.inverse_vocab = {idx: tok for tok, idx in self.vocab.items()}

    def tokenize_word(self, word: str) -> list[str]:
        """Segment a single word into subwords using learned merge rules."""
        symbols = list(word) + ["</w>"]
        for pair, merged in self.merges.items():
            i = 0
            new_symbols = []
            while i < len(symbols):
                if i < len(symbols) - 1 and (symbols[i], symbols[i + 1]) == pair:
                    new_symbols.append(merged)
                    i += 2
                else:
                    new_symbols.append(symbols[i])
                    i += 1
            symbols = new_symbols
        return symbols

    def encode(self, text: str) -> list[int]:
        """Encode text to token IDs using learned BPE rules."""
        words = re.findall(r"\w+|[^\w\s]", text)
        token_ids: list[int] = []
        unk_id = self.vocab.get("<UNK>", 1)
        for w in words:
            subwords = self.tokenize_word(w)
            for sub in subwords:
                token_ids.append(self.vocab.get(sub, unk_id))
        return token_ids

    def decode(self, ids: list[int]) -> str:
        """Decode token IDs back to string."""
        tokens = [self.inverse_vocab.get(i, "<UNK>") for i in ids]
        text = "".join(tokens).replace("</w>", " ").strip()
        return text

    def get_compression_ratio(self, text: str) -> float:
        """Compute character-to-token compression ratio."""
        char_count = len(text)
        token_count = len(self.encode(text))
        return char_count / max(1, token_count)
