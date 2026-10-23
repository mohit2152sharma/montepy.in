---
title: "Tokenisation"
date: 2026-10-23T14:36:43+05:30
draft: false
tags: ["llm", "ai"]
canonicalUrl: https://montepy.in/posts/tokenisation
ShowBreadCrumbs: true
---

As we all know, neural networks understand one and only one thing i.e. numbers, so how are they able to work with text data like `"what's your name?"`? If that's the case, then how do we convert text into numbers, what's the best way to do it, and is one way better than another and why? We need a way to convert text into numbers and numbers back to text.

> Tokenisation is the process of converting the text into numbers and numbers back to text.

Let's start with a simple text: "low lower lowest slower 🐢"

Before we set out to explore approaches, let's define a metric which can help us compare across different approaches. 

Compression ratio: It's the ratio of number of bytes over number of tokens, and it measures how efficiently we are able to encode text into numbers (or tokens). The higher the better, because the more we are able to compress, the fewer tokens we will need to run our computation.

# Approach 1: Character-level tokenisation

It's the first way that comes to mind i.e. split the text by characters. This is known as character-level tokenisation. For our toy example, the number of tokens will be 25 and number of bytes will be 28 (🐢 takes 4 bytes in UTF-8). The compression ratio is around 1.12. It isn't much better than not compressing at all. In addition to that, our vocabulary size is huge: Unicode defines ~150k+ characters.

Here's how our toy example looks after character-level tokenisation (25 tokens), using each character's Unicode code point as its token ID:

```
"low lower lowest slower 🐢"
→ [108, 111, 119, 32, 108, 111, 119, 101, 114, 32, 108, 111, 119, 101, 115, 116, 32, 115, 108, 111, 119, 101, 114, 32, 128034]

Breakdown:
"low"     → [108, 111, 119]
" "       → [32]
"lower"   → [108, 111, 119, 101, 114]
" "       → [32]
"lowest"  → [108, 111, 119, 101, 115, 116]
" "       → [32]
"slower"  → [115, 108, 111, 119, 101, 114]
" "       → [32]
"🐢"      → [128034]                        ← emoji is a single token
```

> Is a large vocabulary a bad thing? As it turns out, yes. With a large vocabulary many characters are rare, and the model doesn't learn rare tokens well because it sees them so few times during training. A larger vocabulary also means more memory: the embedding table at the input is vocab_size × d_model. And more computation at the output, where the model has to score every one of the ~150k characters at every position.

# Approach 2: Byte level tokenisation

Where each byte is represented by one token. If we tokenise over bytes, then the compression ratio will be 1, well we didn't compress anything. However our vocabulary size is small: `256` (each byte comprises `8` bits, so 2⁸), but the sequence length is bigger.

Here's how our toy example looks after byte-level tokenisation (28 tokens):

```
"low lower lowest slower 🐢"
→ [108, 111, 119, 32, 108, 111, 119, 101, 114, 32, 108, 111, 119, 101, 115, 116, 32, 115, 108, 111, 119, 101, 114, 32, 240, 159, 144, 162]

Breakdown:
"low"     → [108, 111, 119]
" "       → [32]
"lower"   → [108, 111, 119, 101, 114]
" "       → [32]
"lowest"  → [108, 111, 119, 101, 115, 116]
" "       → [32]
"slower"  → [115, 108, 111, 119, 101, 114]
" "       → [32]
"🐢"      → [240, 159, 144, 162]            ← one emoji, 4 tokens
```

> Is a bigger sequence length a bad thing? As it turns out, yes. The attention computation grows by N² where `N` is the number of tokens. Context window fills faster. Token generation is slower.

# Approach 3: Word-level tokenisation

We can split by space and treat each word as a token. For our toy example, the compression ratio will be 28/5 = 5.6.

Here's how our toy example looks after word-level tokenisation (5 tokens). The vocabulary is every distinct word we've seen: `low` → 1, `lower` → 2, `lowest` → 3, `slower` → 4, `🐢` → 5, with `0` reserved for `UNKNOWN`:

```
"low lower lowest slower 🐢"
→ [1, 2, 3, 4, 5]

Breakdown:
"low"     → [1]
"lower"   → [2]    ← unrelated to "low" (1), even though it's "low" + "er"
"lowest"  → [3]    ← unrelated to "low" (1), even though it's "low" + "est"
"slower"  → [4]    ← unrelated to "lower" (2), even though it contains it
"🐢"      → [5]
```

Any word not in this vocabulary, say `lowly`, would become `UNKNOWN` (0).

> With a compression ratio of 5.6, is it all better? Not really, we are back to the vocabulary size problem, vocabulary is basically unbounded, it's every word in every language. Plus many of the words in the language are rare. Also, any typo or unseen word (which is not in vocabulary) will get the `UNKNOWN` token and it's meaning is lost. Then there are related words like `low` and `lowest`. 

With byte level encoding, we have too small of a vocabulary and with words level encoding we have too big of a vocabulary. We need something in middle.

# Approach 4: BPE (byte pair encoding) Tokenisation 

The idea of BPE is simple, start with individual bytes and keep merging the most frequent adjacent pair of tokens until the vocabulary reaches the desired size or no more merges are possible. 

In our toy example: 

Every word starts as its bytes: `l o w`, `␣ l o w e r`, `␣ l o w e s t`, `␣ s l o w e r` and `␣` + the 4 bytes of 🐢. Now we merge, one pair at a time:

| Step | Pair merged | Pair as IDs | Times seen | New token | New ID | Words after the merge |
|---|---|---|---|---|---|---|
| 1 | `l` + `o` | (108, 111) | 4 | `lo` | 256 | `lo w`, `␣ lo w e r`, `␣ lo w e s t`, `␣ s lo w e r` |
| 2 | `lo` + `w` | (256, 119) | 4 | `low` | 257 | `low`, `␣ low e r`, `␣ low e s t`, `␣ s low e r` |
| 3 | `low` + `e` | (257, 101) | 3 | `lowe` | 258 | `low`, `␣ lowe r`, `␣ lowe s t`, `␣ s lowe r` |
| 4 | `␣` + `lowe` | (32, 258) | 2 | `␣lowe` | 259 | `low`, `␣lowe r`, `␣lowe s t`, `␣ s lowe r` |

Each new token is built from two existing tokens, and those can themselves be earlier merges: `low` (257) is `lo` (256) + `w` (119), and `lo` (256) is `l` (108) + `o` (111). The new ID itself is arbitrary. It's simply the next unused number after the 256 byte values, and it says nothing about what the token contains. What gives it meaning is the merge rule we write down at each step:

```
(108, 111) → 256    # l    + o    = lo
(256, 119) → 257    # lo   + w    = low
(257, 101) → 258    # low  + e    = lowe
(32,  258) → 259    # ␣    + lowe = ␣lowe
```

This list of merges is what the tokeniser saves. Encoding applies the rules in this order, and decoding uses them in reverse: 259 → (32, 258) → (32, (257, 101)) → … all the way down to bytes.

After step 4, no pair appears more than once, so we stop. Our vocabulary is 256 bytes + 4 merges = **260** tokens. BPE found the piece all four words share (`low`), and then learned `␣lowe` with the space built in, because `␣lower` and `␣lowest` both start with it. (At step 4, `lowe` + `r` was tied at 2 as well; we broke the tie by taking the pair that appeared first.)

Here's how our toy example looks after BPE tokenisation (15 tokens):

```
"low lower lowest slower 🐢"
→ [257, 259, 114, 259, 115, 116, 32, 115, 258, 114, 32, 240, 159, 144, 162]

Breakdown (␣ marks a space):
"low"      → [257]                       ← "low"
"␣lower"   → [259, 114]                  ← "␣lowe" + "r": the space costs nothing
"␣lowest"  → [259, 115, 116]             ← "␣lowe" + "s" + "t": shares "␣lowe" with "␣lower"
"␣slower"  → [32, 115, 258, 114]         ← "␣" + "s" + "lowe" + "r"
"␣🐢"      → [32, 240, 159, 144, 162]    ← seen only once, stays as raw bytes
```

Putting all four approaches side by side on our toy example:

| Approach | Tokens | Compression ratio | Vocabulary size | Related words share pieces? | New words |
|---|---|---|---|---|---|
| Character-level | 25 | 1.12 | ~150k | only single characters | fine, but the vocabulary is huge |
| Byte-level | 28 | 1.0 | 256 | only single bytes | fine, but sequences are long |
| Word-level | 5 | 5.6 | grows with every new word | no: `low`, `lower`, `lowest` are unrelated IDs | `UNKNOWN` |
| **BPE** | **15** | **1.87** | **260** | **yes: `low`, `lowe`, `␣lowe`** | **fall back to smaller pieces or bytes, never `UNKNOWN`** |


In our toy example, BPE kept the vocabulary small (260) and still cut the number of tokens from 28 (bytes) to 15. With a larger training corpus, there are enough repeated pairs to keep merging, so the vocabulary grows to tens of thousands of tokens and common words become single tokens, which pushes the compression ratio much higher (GPT-2 gets around 4 bytes per token on English).
