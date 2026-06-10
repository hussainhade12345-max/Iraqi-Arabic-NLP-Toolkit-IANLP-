# Iraqi Arabic NLP Toolkit (IANLP)
## القاموس العراقي ومنظومة معالجة اللغة الطبيعية

![Python Version](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT%20%7C%20CC%20BY%204.0-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## Overview

**Iraqi Arabic NLP Toolkit (IANLP)** is the first open-source natural language processing toolkit purpose-built for Iraqi Arabic dialect, featuring an annotated complaint corpus, dialect lexicon with geographic mapping, and specialized text processing utilities.

**Author**: Hussein Hadeh | Al-Iraqia University, Baghdad

---

## Motivation

Iraqi Arabic (Mesopotamian dialect) represents one of the most under-resourced language varieties in NLP. Existing Arabic NLP tools and datasets are built primarily for Modern Standard Arabic (MSA) and fail significantly when applied to Iraqi dialect due to:

- **Linguistic distance**: Iraqi Arabic has distinct phonology, morphology, and vocabulary compared to MSA
- **Lack of resources**: No substantial annotated corpora or lexicons for Iraqi dialect exist
- **AI readiness gap**: Mainstream language models perform poorly on Iraqi text, limiting applications for citizens

**IANLP bridges this gap** by providing linguistically grounded resources and tools that enable researchers, developers, and organizations to build Iraqi dialect-aware NLP applications.

---

## Features

✅ **Annotated Complaint Corpus** — 8-domain labeled dataset covering:
- Infrastructure & Services (electricity, water, transportation)
- Healthcare
- Education
- Employment
- Security
- Housing
- Administrative Services

✅ **Dialect Lexicon** — Iraqi Arabic words with:
- MSA equivalents for cross-dialect mapping
- Geographic distribution (region-specific variants)
- Register labels (colloquial, slang, informal, formal)
- Part-of-speech tags
- Example sentences

✅ **Text Preprocessing** — Iraqi Arabic-specific utilities:
- Diacritic removal
- Character normalization (أ/إ/آ → ا, ة → ه, ى → ي)
- Iraqi-specific character handling (چ, گ, پ, ڤ)
- URL, emoji, mention, and hashtag removal
- Whitespace normalization

✅ **Code-Switching Detection** — Identify Arabic/English mixing:
- Detect mixed-language text
- Calculate Arabic/English ratios
- Extract English tokens

---

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```python
from iraqi_nlp import normalize, detect_codeswitch, tokenize

# Normalize Iraqi Arabic text
text = "هسّه شنو أخبارك؟"
cleaned = normalize(text)
print(cleaned)  # Output: هسه شنو اخبارك

# Detect code-switching
mixed_text = "شلونك today؟"
result = detect_codeswitch(mixed_text)
print(result)
# Output: {
#   'is_mixed': True,
#   'arabic_ratio': 0.67,
#   'english_tokens': ['today']
# }

# Tokenize Iraqi Arabic
text = "خوش سالفة هسه"
tokens = tokenize(text)
print(tokens)  # Output: ['خوش', 'سالفة', 'هسه']
```

---

## Corpus Statistics

| Metric | Value |
|--------|-------|
| Total Posts | — |
| Training Set | — |
| Validation Set | — |
| Test Set | — |
| Governorates Covered | 7 |
| Average Post Length | — |
| Label Distribution | 8 domains (multi-label) |

---

## Lexicon Statistics

| Metric | Value |
|--------|-------|
| Total Entries | — |
| Unique Words | — |
| Geographic Regions | 10 |
| POS Categories | 6 |
| Register Types | 4 |
| Coverage (% of corpus) | — |

---

## Repository Structure

```
iraqi-arabic-nlp/
├── corpus/
│   ├── train.csv
│   ├── test.csv
│   └── validation.csv
├── lexicon/
│   └── iraqi_lexicon.csv
├── iraqi_nlp/
│   ├── __init__.py
│   ├── preprocessing.py
│   ├── topic.py
│   ├── sentiment.py
│   ├── intent.py
│   ├── urgency.py
│   └── codeswitch.py
├── docs/
│   └── annotation_guide.md
├── examples/
│   └── basic_usage.py
├── paper/
│   └── README.md
├── api/
│   └── README.md
├── README.md
├── LICENSE
├── requirements.txt
└── setup.py
```

---

## Data Collection Methodology

### Field Observation (2023-2025)
Data was collected through direct observation and interaction across multiple Iraqi governorates:
- **Wasit** | **Baghdad** | **Basra** | **Karbala** | **Najaf** | **Dhi Qar** | **Maysan**

Collection occurred during seasonal work assignments, allowing authentic documentation of spoken Iraqi Arabic in natural contexts.

### Social Media Analysis
Anonymized public content from:
- **X (Twitter)**
- **Facebook**
- **Instagram**
- **TikTok**

All personally identifiable information (names, phone numbers, locations, dates, account handles) has been systematically removed prior to annotation.

### Privacy & Ethics
✓ No personal data retained
✓ Anonymized at collection stage
✓ Public content only
✓ Compliant with platform terms of service

---

## Citation

If you use IANLP in your research, please cite:

```bibtex
@software{hadeh2025ianlp,
  title={Iraqi Arabic NLP Toolkit (IANLP): The First Open-Source NLP Toolkit for Iraqi Dialect},
  author={Hadeh, Hussein},
  year={2025},
  institution={Al-Iraqia University, Baghdad},
  url={https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-},
  note={First open-source NLP toolkit for Iraqi Arabic dialect}
}
```

---

## License

This project is dual-licensed:

### Code: MIT License
All Python code and software components are licensed under the MIT License (Hussein Hadeh, 2025).

### Data: Creative Commons Attribution 4.0 (CC BY 4.0)
Corpus and lexicon datasets are licensed under CC BY 4.0. You are free to share and adapt the data with appropriate attribution.

See [LICENSE](LICENSE) for full terms.

---

## Author

**Hussein Hadeh**  
Al-Iraqia University, Baghdad  
📧 Contact: hussainhade12345@gmail.com  
🔗 GitHub: [@hussainhade12345-max](https://github.com/hussainhade12345-max)

---

## Contributing

Contributions are welcome! Please open an issue or pull request with improvements to:
- Lexicon entries
- Corpus annotations
- Preprocessing utilities
- Documentation

---

## Acknowledgments

This toolkit was developed to address the severe under-resourcing of Iraqi Arabic in NLP. Special thanks to the communities across Iraqi governorates who contributed to the field observation phase.

---

**Status**: 🚀 Active Development | First Release: 2025
