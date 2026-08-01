# Iraqi Arabic NLP Toolkit — Dataset README

This directory contains cleaned, merged, and formatted resources collected for the Iraqi Arabic NLP Toolkit (IANLP).

Files included:
- data/lexicon/iraqi_lexicon.json — Lexicon entries with fields: word, meaning_fusha, pos, example.
- data/lexicon/dialect_to_standard.json — Mappings from dialect variants to standard Arabic terms.
- data/sentiment/sentiment_labels.csv — Sentences labeled for sentiment (text,label). UTF-8 CSV with header.
- data/normalization/normalization_pairs.json — Common orthographic/typing variants mapped to normalized forms.
- data/idioms/idioms.json — Idioms and proverbs with meanings and categories.
- data/ner/ner_examples.jsonl — NER examples, one JSON object per line: {text, entities}.
- data/intents/intents.json — Intent definitions with examples and canned responses.
- data/lexemes/stopwords_iraqi.txt — Frequent dialect tokens / stopwords.
- data/topics/topics_labeled.csv — Topic-labeled sentences (text,category).

Encoding & formats:
- All files use UTF-8 encoding.
- CSV files include a header row and are double-quoted where needed.
- JSON files are UTF-8 and valid JSON; JSONL uses one JSON object per line.

Suggested next steps:
- Add a LICENSE file (e.g., MIT or CC-BY) if you want to publish dataset under a specific license.
- Add a small example Jupyter notebook showing how to load and preprocess these files (notebooks/preview_preprocessing.ipynb).
- Optionally split sentiment/topics files into train/dev/test and add splits.csv with source indexes.

Commit message: "Add cleaned dataset splits and lexicons (initial import)"
