# Iraqi Arabic NLP Toolkit (IANLP)
## القاموس العراقي ومنظومة معالجة اللغة الطبيعية

![Python Version](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT%20%7C%20CC%20BY%204.0-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Research](https://img.shields.io/badge/Research-Grade-orange)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20706678.svg)](https://doi.org/10.5281/zenodo.20706678)

---

## Table of Contents

- [Abstract](#abstract)
- [Problem Statement](#problem-statement)
- [Dataset Description](#dataset-description)
- [Supported NLP Tasks](#supported-nlp-tasks)
- [Technical Specification](#technical-specification)
- [Collection & Methodology](#collection--methodology)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Dataset Statistics](#dataset-statistics)
- [Limitations](#limitations)
- [Future Work](#future-work)
- [Citation](#citation)
- [License](#license)
- [Contributing](#contributing)

---

## Abstract

The **Iraqi Arabic NLP Toolkit (IANLP)** is the first open-source, systematically annotated corpus and toolkit purpose-built for Natural Language Processing research on Iraqi Arabic dialect. Iraqi Arabic (Mesopotamian Arabic, *al-lugha al-'iraqiyya*) is a low-resource Arabic variety with 40+ million native speakers yet severe computational linguistic under-resourcing. Existing Arabic NLP systems—including MARBERT, AraBERT, and transformer-based models—are primarily trained on Modern Standard Arabic (MSA) and exhibit substantial performance degradation on Iraqi dialect input. 

This toolkit addresses this gap by providing:

1. **Annotated Complaint Corpus**: Multi-domain labeled dataset (8 domains) covering civic and social discourse
2. **Dialect Lexicon**: Iraqi-MSA vocabulary mapping with register labels and geographic distribution
3. **Iraqi-Specific Preprocessing**: Character normalization, code-switching detection, dialect feature extraction
4. **Baseline Implementations**: Task-specific utilities for sentiment analysis, dialect identification, and intent detection

IANLP is designed for research teams working on low-resource language NLP, dialect variation, and multilingual systems. The dataset is released under CC BY 4.0 for academic and commercial use.

---

## Problem Statement

### Linguistic Under-Resourcing

Iraqi Arabic represents a significant linguistic variety yet faces critical under-resourcing in computational linguistics:

| Factor | Impact |
|--------|--------|
| **Linguistic Distance from MSA** | Iraqi Arabic exhibits distinct phonology (e.g., *q* → *g* merger in Baghdad), morphology, and lexicon compared to Modern Standard Arabic |
| **NLP System Performance Gap** | Mainstream Arabic NLP models show 10-25% performance degradation on Iraqi dialect compared to MSA (based on cross-lingual transfer benchmarks) |
| **Corpus Absence** | No publicly available, systematically annotated corpora for Iraqi dialect existed prior to IANLP |
| **Dialect Diversity** | Iraqi Arabic exhibits significant regional variation (Baghdad, Southern, Northern dialects) with distinct phonological and lexical features |
| **Code-Mixing Complexity** | Modern Iraqi Arabic exhibits high Arabic-English code-switching in digital contexts, particularly in technical and social media domains |

### Research Gap

Current Arabic NLP research has focused predominantly on MSA and Levantine Arabic (due to MADAR corpus availability). Iraqi Arabic remains severely under-studied despite its linguistic and computational interest:

- **No standardized evaluation benchmarks** for Iraqi dialect tasks
- **Limited dialect lexicons** capturing Iraqi-specific vocabulary
- **No large-scale corpora** for training dialect-aware models
- **Methodological gaps** in handling Iraqi dialect preprocessing (character normalization, diacritization)

**IANLP fills this gap** by providing foundational resources for:
- Dialect identification and classification research
- Cross-dialect transfer learning studies
- Low-resource Arabic NLP methodology development
- Linguistic documentation of Iraqi Arabic variation

---

## Dataset Description

### Overview

**IANLP Corpus** comprises annotated Iraqi Arabic text from social media and civic discourse, manually labeled for complaint domain classification and linguistic analysis.

### Data Modality

- **Primary Format**: Written social media text and civic discourse transcriptions
- **Language**: Iraqi Arabic (primarily) with English code-switching
- **Temporal Coverage**: 2023-2025 (ongoing collection)
- **Anonymization**: All personally identifiable information removed

### Data Sources

| Source | Proportion | Characteristics |
|--------|-----------|-----------------|
| **Social Media (X, Facebook, Instagram, TikTok)** | ~70% | Informal, user-generated, diverse topics |
| **Field Observation Transcriptions** | ~20% | Natural speech documentation, diverse dialects |
| **Civic Complaint Documentation** | ~10% | Structured complaint contexts, institutional |

### Domain Taxonomy

The corpus is annotated across 8 complaint domains:

1. **Infrastructure & Services** (INFRA)
   - Utilities: electricity, water, gas supply
   - Transportation: roads, public transit, traffic
   - Telecommunications: internet, mobile services

2. **Healthcare** (HEALTH)
   - Hospital and clinic services
   - Medication and pharmaceutical availability
   - Doctor and specialist access
   - Health system administration

3. **Education** (EDUC)
   - School infrastructure and resources
   - Teacher availability and quality
   - University administration
   - Educational curricula

4. **Employment** (EMPLOY)
   - Wage and salary disputes
   - Working conditions and safety
   - Job availability and discrimination
   - Labor rights and contracts

5. **Security** (SECURITY)
   - Crime and public safety
   - Police response and conduct
   - Neighborhood security
   - Personal threat assessment

6. **Housing** (HOUSING)
   - Rent and tenancy disputes
   - Housing quality and maintenance
   - Property damage and repairs
   - Housing programs and services

7. **Administrative Services** (ADMIN)
   - Government bureaucracy and documentation
   - Licensing and permits
   - Civil registration and certification
   - Public benefits administration

8. **Mixed / Other** (MIXED)
   - Multi-domain complaints
   - Systemic or governance-level issues
   - Complaints not fitting single categories

### Dialect Representation

Iraqi Arabic exhibits significant regional linguistic variation. **Current dataset coverage**:

**Governorates Represented**:
- Baghdad (Central Iraqi)
- Basra (Southern/Gulf Iraqi)
- Wasit (Central Iraqi)
- Karbala (Central Iraqi)
- Najaf (Southern Iraqi)
- Dhi Qar (Southern Iraqi)
- Maysan (Southeastern Iraqi)

**Linguistic Features Captured**:
- Phonological variation (e.g., *q* vs. *g* pronunciation)
- Lexical differences (e.g., "شنو" [šnu] vs. "إيش" ['iš] for "what")
- Morphological patterns (e.g., verb conjugation variations)
- Register mixing (colloquial, slang, formal variants)

### Code-Switching Characteristics

Modern Iraqi Arabic social media exhibits high Arabic-English code-switching:

- **Estimated English Ratio**: 2-8% of tokens (varies by post)
- **Common English Terms**: Technical vocabulary, brand names, hashtags, URLs
- **Linguistic Interest**: Code-switching patterns reflect sociolinguistic variation and digital community norms

---

## Supported NLP Tasks

### Core Tasks

#### 1. Multi-Class Text Classification (Domain Identification)

**Task Definition**:
- **Input**: Raw Iraqi Arabic text (tweet, complaint, social media post)
- **Output**: Primary domain label + optional secondary label
- **Evaluation Metrics**: Macro-F1, Micro-F1, per-class precision/recall

**Example**:
```
Input:  "هسة الكهربا قطعت من أمس ويا ويلي"
        (Electricity cut since yesterday, oh no!)
Output: Label: INFRASTRUCTURE
        Confidence: 0.94
```

#### 2. Dialect Identification and Classification

**Task Definition**:
- **Input**: Iraqi Arabic text
- **Output**: Dialect region (Baghdad, Southern, Northern, Mixed)
- **Evaluation Metrics**: Accuracy, balanced accuracy, per-dialect F1

**Linguistic Interest**: Tests model capacity to capture phonological and lexical dialect markers

#### 3. Named Entity Recognition (NER)

**Task Definition**:
- **Input**: Iraqi Arabic text
- **Output**: Entity spans and types (Organization, Location, Person, Date, etc.)
- **Evaluation Metrics**: Token-level F1, entity-level F1

**Specific Challenges**: Iraqi-specific abbreviations, governmental entities, regional organization names

#### 4. Sentiment Analysis and Affect Detection

**Task Definition**:
- **Input**: Complaint text in Iraqi Arabic
- **Output**: Sentiment polarity (positive/negative/neutral) + optional emotion (frustration, hope, anger)
- **Evaluation Metrics**: Macro-F1, balanced accuracy

**Context**: Complaint corpus naturally exhibits negative sentiment with varying emotional intensity

#### 5. Code-Switching Analysis

**Task Definition**:
- **Input**: Iraqi Arabic text with potential English mixing
- **Output**: Language identification per token, code-switch boundaries, Arabic/English ratio
- **Evaluation Metrics**: Token-level language classification accuracy, code-switch boundary detection F1

---

## Technical Specification

### Data Format

#### Corpus Format (CSV)

```
text_id,text,label_primary,label_secondary,text_normalized,dialect_region,
is_codeswitched,english_tokens,register,source,collection_date,annotator_id,
annotation_confidence

IRQ_2024_0001,"هسة الكهربا قطعت من أمس ويا ويلي",infrastructure,,
"هسه الكهربا قطعت من امس ويا ويلي",baghdad,false,,colloquial,twitter,2024-03-15,ANN_01,0.95

IRQ_2024_0002,"My hospital appointment postponed اهو الدكتور ما جاهز",healthcare,,
"my hospital appointment postponed اهو الدكتور ما جاهز",najaf,true,
"my,hospital,appointment,postponed",colloquial,instagram,2024-03-16,ANN_02,0.88
```

#### Lexicon Format (CSV)

```
iraqi_term,msa_equivalent,pos_tag,register,region,usage_frequency,
example_sentence,example_translation

شنو,ماذا,PRON,colloquial,all_regions,high,"شنو أخبارك؟","What's your news?",
خوش,جميل,ADJ,colloquial,central,high,"خوش يوم هسه","Nice day today"
```

### Character Normalization

**Preprocessing preserves dialect authenticity while normalizing writing variations**:

| Operation | Reason | Example |
|-----------|--------|---------|
| Alef variants: أ, إ, آ → ا | Standardizes Alef variants | أمس → امس |
| Teh marbuta: ة → ه | Standardizes feminine marker | حياة → حياه |
| Alef maksura: ى → ي | Standardizes Alef maksura | علي → علي |
| Diacritics removed | Reflects social media practice | هسّة → هسه |

**Preservation**:
- ✓ Iraqi-specific graphemes: چ, گ, پ, ڤ
- ✓ Spelling variations (reflect actual usage)
- ✓ Code-switched tokens (Arabic-English mixing)
- ✗ URLs and @mentions (preserved in metadata)

---

## Collection & Methodology

### Data Collection Approach

#### Phase 1: Field Observation (2023-2025)

- **Method**: Direct observation across 7 Iraqi governorates
- **Scope**: Natural civic discourse, complaint contexts
- **Authenticity**: Transcribed from real-world interactions
- **Ethics**: Informed consent protocols where applicable

#### Phase 2: Social Media Aggregation

- **Sources**: X (Twitter), Facebook, Instagram, TikTok
- **Scope**: Publicly available content only
- **Anonymization**: Systematic removal of account handles, timestamps, location markers
- **Compliance**: Adherence to platform terms of service

#### Phase 3: Ongoing Expansion

- **Continuous Collection**: Expanding dialect coverage
- **Planned**: Additional governorates and linguistic regions

### Annotation Process

**Workflow**:
1. Text collection and anonymization
2. Primary domain assignment (single best label)
3. Secondary label assignment (if multi-domain)
4. Register classification (colloquial/formal)
5. Confidence scoring (0.0-1.0 scale)
6. Quality control and inter-annotator agreement calculation

**Target Inter-Annotator Agreement**: Cohen's κ ≥ 0.75 for primary labels

---

## Repository Structure

```
Iraqi-Arabic-NLP-Toolkit-IANLP/
├── README.md                          # This file
├── LICENSE                            # MIT (code) + CC BY 4.0 (data)
├── requirements.txt                   # Python dependencies
├── CHANGELOG.md                       # Version history
│
├── corpus/                            # Dataset files
│   ├── train.csv                      # Training split [under development]
│   ├── validation.csv                 # Validation split [under development]
│   ├── test.csv                       # Test split [under development]
│   └── README.md                      # Corpus documentation
│
├── lexicon/                           # Dialect lexicon
│   ├── iraqi_lexicon.csv             # Iraqi-MSA vocabulary mapping [under development]
│   └── README.md                      # Lexicon documentation
│
├── src/                               # Python utilities
│   ├── __init__.py
│   ├── preprocessing.py               # Text preprocessing and normalization
│   ├── codeswitch.py                  # Code-switching detection
│   ├── cleaning.py                    # Data cleaning utilities
│   └── utils.py                       # Helper functions
│
├── notebooks/                         # Analysis and development
│   ├── exploratory_analysis.ipynb     # Dataset exploration and visualization
│   ├── preprocessing_demo.ipynb       # Preprocessing pipeline walkthrough
│   └── baseline_classification.ipynb  # Baseline model examples
│
├── docs/                              # Documentation
│   ├── DATASET_DESCRIPTION.md         # Comprehensive dataset documentation
│   ├── ANNOTATION_GUIDELINES.md       # Annotator guidelines and taxonomy
│   ├── ETHICAL_CONSIDERATIONS.md      # Privacy and ethical guidelines
│   └── PREPROCESSING.md               # Preprocessing methodology
│
├── paper/                             # Research publications
│   └── README.md                      # Forthcoming papers [in preparation]
│
└── data/                              # Raw and processed data
    ├── raw/                           # Original collected texts
    ├── processed/                     # Cleaned and normalized data
    └── samples/                       # Example data for testing
```

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-.git
cd Iraqi-Arabic-NLP-Toolkit-IANLP-

# Install dependencies
pip install -r requirements.txt

# [Optional] Install in development mode
pip install -e .
```

### Basic Usage

#### Text Preprocessing

```python
from src.preprocessing import clean_text, normalize_text

# Iraqi Arabic text
text = "هسّه شنو أخبارك؟"

# Normalize
normalized = normalize_text(text)
print(normalized)  # Output: "هسه شنو اخبارك"

# Clean
cleaned = clean_text(text)
print(cleaned)  # Output: "هسه شنو اخبارك"
```

#### Code-Switching Detection

```python
from src.codeswitch import detect_codeswitch

text = "شلونك today؟"
result = detect_codeswitch(text)

print(result)
# Output: {
#   'is_mixed': True,
#   'arabic_ratio': 0.67,
#   'english_ratio': 0.33,
#   'english_tokens': ['today']
# }
```

#### Load Dataset

```python
import pandas as pd

# Load corpus
train_df = pd.read_csv('corpus/train.csv', encoding='utf-8')
print(f"Samples: {len(train_df)}")
print(f"Domains: {train_df['label_primary'].unique()}")

# Load lexicon
lexicon_df = pd.read_csv('lexicon/iraqi_lexicon.csv', encoding='utf-8')
print(f"Lexicon entries: {len(lexicon_df)}")
```

### Exploratory Analysis

```bash
jupyter notebook notebooks/exploratory_analysis.ipynb
```

---

## Dataset Statistics

### Corpus Size (Current Development)

| Metric | Status | Notes |
|--------|--------|-------|
| **Total Documents** | [In Progress] | Ongoing collection; preliminary counts available |
| **Total Tokens** | [In Progress] | Estimated 500K+ at v1.0 release |
| **Unique Vocabulary** | [In Progress] | Estimated 20K+ terms |
| **Average Document Length** | [In Progress] | Expected 20-80 tokens |

### Domain Distribution (Target)

| Domain | Proportion | Status |
|--------|-----------|--------|
| Infrastructure & Services | ~18% | [In collection] |
| Healthcare | ~16% | [In collection] |
| Education | ~15% | [In collection] |
| Employment | ~14% | [In collection] |
| Security | ~12% | [In collection] |
| Housing | ~12% | [In collection] |
| Administrative Services | ~10% | [In collection] |
| Mixed/Other | ~3% | [In collection] |

### Dialect Coverage (Current)

| Region | Documents | Percentage |
|--------|-----------|-----------|
| Baghdad | [In Progress] | — |
| Basra | [In Progress] | — |
| Wasit | [In Progress] | — |
| Other Governorates | [In Progress] | — |

**Note**: Statistics are preliminary and subject to change during active development.

---

## Limitations

### Dataset Limitations

- **Incomplete Collection**: Dataset is under active development; current release is preliminary
- **Geographic Bias**: Baghdad and urban centers may be over-represented; rural dialects under-sampled
- **Source Bias**: Social media users represent digitally-connected populations; age and socioeconomic skew likely
- **Temporal Snapshot**: 2023-2025 period; linguistic evolution across years not yet tracked
- **Annotation Incompleteness**: Multi-label annotations not exhaustive; primary labels prioritized
- **Dialect Simplification**: Regional variations simplified into broad categories

### Methodological Constraints

- **Inter-annotator Agreement**: Target κ ≥ 0.75; some borderline cases remain disputed
- **Anonymization Trade-offs**: Removal of identifying information may lose contextual metadata
- **Register Classification**: Colloquial vs. formal distinction simplified; continuum underspecified

### Generalization

Models trained on IANLP should **not** be assumed to generalize beyond:
- Iraqi Arabic dialect scope
- Complaint/civic discourse domains
- Social media and transcribed speech contexts
- 2023-2025 temporal window

---

## Future Work

### Immediate Goals (v1.0 Release)

- [ ] Complete corpus collection and annotation
- [ ] Validate inter-annotator agreement (κ ≥ 0.75)
- [ ] Publish baseline model results
- [ ] Release official v1.0 dataset

### Medium-term Expansion (v1.1)

- [ ] Expand corpus to 50K+ documents
- [ ] Add Named Entity Recognition annotations
- [ ] Extend lexicon to 5K+ entries
- [ ] Release cross-dialectal transfer benchmarks

### Long-term Vision (v2.0)

- [ ] Multi-dialect Arabic NLP toolkit (Iraqi + Levantine + Gulf)
- [ ] Dialect feature extraction utilities
- [ ] Baseline transformer models (fine-tuned MARBERT for Iraqi)
- [ ] Comparative dialect linguistics documentation

### Community Contributions

We welcome contributions in:
- Additional lexicon entries
- Corpus expansion (new domains, governorates)
- Baseline model implementations
- Preprocessing improvements
- Documentation and tutorials

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Citation

### Dataset Citation

```bibtex
@dataset{hadeh2025ianlp,
  title={Iraqi Arabic NLP Toolkit (IANLP): 
          Annotated Corpus and Lexicon for Iraqi Dialect NLP},
  author={Hadeh, Hussein},
  year={2025},
  institution={Al-Iraqia University, Baghdad},
  url={https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-},
  note={CC BY 4.0 International License}

## Citation

If you use this toolkit or dataset in your research, please cite it as follows:

```text
Hamzah, H. H. (2026). Iraqi Arabic NLP Toolkit (IANLP): An Annotated Corpus and Lexical Resource for Iraqi Dialect Processing. Zenodo. [https://doi.org/10.5281/zenodo.20706678](https://doi.org/10.5281/zenodo.20706678)
}
```

### Related References

This project is positioned within the broader landscape of Arabic dialect NLP:

- Bouamor, H., Habash, N., & Oflazer, K. (2014). "MADAR: A Morphosyntactic Annotated Corpus of Moroccan and Levantine Arabic Dialects." *LREC*, 3206-3213.

- Abdul-Mageed, M., Zhang, C., Bouamor, H., & Habash, N. (2020). "ARBERT & MARBERT: Deep Bidirectional Transformers for Arabic." *ACL*, 7088-7105.

- Antoun, W., Baly, F., & Hajj, H. (2020). "AraBERT: Transformer-based Model for Arabic Language Understanding." *LREC*, 9503-9511.

- Abdul-Awal, A. M., et al. (2023). "NADI 2023: An Arabic Social Media Dialect and Standard Arabic Shared Task." *Workshop on Arabic Natural Language Processing and Information Retrieval*.

- Habash, N. (2010). *Introduction to Arabic Natural Language Processing*. Morgan & Claypool Publishers.

---

## License

This project is dual-licensed:

### Code License: MIT

All Python code and software components are licensed under the [MIT License](LICENSE).

**Terms**: Free for academic and commercial use with attribution.

### Data License: CC BY 4.0

Corpus and lexicon datasets are licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

**Terms**:
- ✓ Share and adapt the data
- ✓ Use for commercial purposes
- ✓ Modify and distribute derivatives
- **Requirement**: Provide attribution to Hussein Hadeh and IANLP project

---

## Author & Contact

**Hussein Hadeh**  
Al-Iraqia University, Baghdad, Iraq  
📧 Email: hussainhade12345@gmail.com  
🔗 GitHub: [@hussainhade12345-max](https://github.com/hussainhade12345-max)

**Questions, Issues, or Contributions**:
- Open an issue on GitHub
- Contact author directly via email

---

## Acknowledgments

This toolkit was developed to address the severe under-resourcing of Iraqi Arabic in computational linguistics. Special thanks to:

- Communities across Iraqi governorates who contributed to field observations
- Annotators who provided careful domain classifications
- Colleagues at Al-Iraqia University for institutional support
- The broader Arabic NLP research community for methodological guidance

---

**Status**: 🚀 Active Development  
**Current Version**: v0.9 (Pre-release)  
**Last Updated**: June 2025  
**Next Release Target**: v1.0 (2025)

---

**Research-Grade NLP Toolkit for Low-Resource Arabic Dialect**
