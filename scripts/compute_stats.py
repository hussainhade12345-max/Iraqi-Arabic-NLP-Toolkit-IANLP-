import pandas as pd
import os
import json

stats = {}

# --- CORPUS ---
corpus_files = {
    "train":      "corpus/train.csv",
    "validation": "corpus/validation.csv",
    "test":       "corpus/test.csv",
}

total_posts = 0
split_sizes = {}
all_text    = []
all_govs    = []
all_labels  = []

for split, path in corpus_files.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        split_sizes[split] = len(df)
        total_posts += len(df)

        text_col = next(
            (c for c in df.columns
             if c.lower() in ["text","post","content","tweet","نص","المنشور"]),
            df.columns[0] if len(df.columns) > 0 else None
        )
        if text_col:
            all_text.extend(df[text_col].dropna().tolist())

        gov_col = next(
            (c for c in df.columns
             if c.lower() in ["governorate","gov","province","محافظة"]),
            None
        )
        if gov_col:
            all_govs.extend(df[gov_col].dropna().tolist())

        label_col = next(
            (c for c in df.columns
             if c.lower() in ["label","domain","category","تصنيف","النوع"]),
            None
        )
        if label_col:
            all_labels.extend(df[label_col].dropna().tolist())
    else:
        split_sizes[split] = "File not found"

stats["corpus"] = {
    "total_posts":        total_posts if total_posts > 0 else "No data collected yet",
    "training_set":       split_sizes.get("train", "File not found"),
    "validation_set":     split_sizes.get("validation", "File not found"),
    "test_set":           split_sizes.get("test", "File not found"),
    "avg_post_length":    round(sum(len(str(t).split()) for t in all_text) / len(all_text), 1)
                          if all_text else "No data",
    "governorates":       len(set(all_govs)) if all_govs else "Not yet tagged",
    "domain_labels":      len(set(all_labels)) if all_labels else "8 (defined, not yet collected)",
}

# --- LEXICON ---
lex_path = "lexicon/iraqi_lexicon.csv"
if os.path.exists(lex_path):
    lex = pd.read_csv(lex_path)

    word_col = next(
        (c for c in lex.columns
         if c.lower() in ["word","iraqi","arabic","كلمة","العراقية"]),
        lex.columns[0] if len(lex.columns) > 0 else None
    )
    pos_col = next(
        (c for c in lex.columns
         if c.lower() in ["pos","part_of_speech","الجزء"]),
        None
    )
    gov_col = next(
        (c for c in lex.columns
         if c.lower() in ["governorate","gov","province","محافظة"]),
        None
    )
    reg_col = next(
        (c for c in lex.columns
         if c.lower() in ["register","style","مستوى"]),
        None
    )
    vocab_col = next(
        (c for c in lex.columns
         if c.lower() in ["msa","msa_equivalent","الفصحى"]),
        None
    )

    corpus_vocab = set(
        w for t in all_text
        for w in str(t).split()
    ) if all_text else set()

    lex_words = set(lex[word_col].dropna().tolist()) if word_col else set()
    coverage  = (
        round(len(lex_words & corpus_vocab) / len(corpus_vocab) * 100, 1)
        if corpus_vocab else "N/A — corpus empty"
    )

    stats["lexicon"] = {
        "total_entries":       len(lex),
        "unique_words":        lex[word_col].nunique() if word_col else "Column not found",
        "geographic_regions":  lex[gov_col].nunique() if gov_col else "Column not found",
        "pos_categories":      lex[pos_col].nunique() if pos_col else "Column not found",
        "register_types":      lex[reg_col].nunique() if reg_col else "Column not found",
        "coverage_percent":    coverage,
    }
else:
    stats["lexicon"] = {"error": "lexicon/iraqi_lexicon.csv not found"}

print(json.dumps(stats, indent=2, ensure_ascii=False))

os.makedirs("scripts", exist_ok=True)
with open("scripts/stats_output.json", "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)

print("\nStats saved to scripts/stats_output.json")