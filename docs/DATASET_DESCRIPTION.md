# Iraqi Arabic NLP Toolkit (IANLP) — Dataset Description

## Executive Summary

The **Iraqi Arabic NLP Toolkit (IANLP)** dataset is a linguistically annotated corpus of Iraqi Arabic text designed to advance natural language processing research on low-resource Arabic dialects. This document provides comprehensive technical and methodological details for researchers intending to utilize the dataset.

---

## 1. Dataset Overview

### 1.1 Purpose and Scope

Iraqi Arabic (also known as Mesopotamian Arabic, *al-lugha al-'iraqiyya*) represents a significant linguistic variety with approximately 40+ million native speakers across Iraq and diaspora communities. Despite its scale, Iraqi Arabic suffers from severe under-resourcing in computational linguistics:

- **Linguistic Distance**: Distinct phonology, morphology, and lexicon compared to Modern Standard Arabic (MSA/Fusha)
- **NLP Gap**: Mainstream Arabic NLP models (BERT variants, GPT models) exhibit substantial performance degradation on Iraqi dialect input
- **Corpus Absence**: No publicly available, systematically annotated corpora existed prior to IANLP

**IANLP addresses this gap** by providing:
- An 8-domain annotated complaint corpus with multi-label classifications
- A dialect lexicon mapping Iraqi terms to MSA equivalents with register labels
- Iraqi-specific preprocessing utilities
- Code-switching detection mechanisms

### 1.2 Dataset Composition

| Component | Status | Purpose |
|-----------|--------|---------|
| Complaint Corpus | Core resource | Domain classification, sentiment analysis, intent detection |
| Dialect Lexicon | Reference resource | Vocabulary mapping, register analysis, dialect feature extraction |
| Preprocessing Utilities | Tools | Character normalization, diacritic handling, code-switching detection |

---

## 2. Corpus Description

### 2.1 Data Modality

**Primary Data Type**: Written social media text and civic discourse transcriptions

**Sources**:
- Social media platforms: X (Twitter), Facebook, Instagram, TikTok
- Direct field observation transcriptions (2023-2025)
- Civic complaint documentation

**Temporal Coverage**: Ongoing collection; current snapshot represents 2023-2025 observations

### 2.2 Domain Distribution

The corpus is annotated across **8 complaint domains**:

| Domain | Description | Example Contexts |
|--------|-------------|------------------|
| **Infrastructure & Services** | Complaints about utilities and public services | Electricity outages, water quality, transportation delays |
| **Healthcare** | Health system complaints | Hospital capacity, medication availability, specialist access |
| **Education** | Educational system issues | School infrastructure, curriculum, teacher availability |
| **Employment** | Labor and job-related issues | Wage disputes, workplace conditions, unemployment |
| **Security** | Safety and security concerns | Crime, police response, neighborhood safety |
| **Housing** | Residential and real estate issues | Rent disputes, housing quality, construction delays |
| **Administrative Services** | Government bureaucracy | Document processing, licensing, permit delays |
| **Mixed/Other** | Multi-domain or unclear complaints | Complex civic issues spanning multiple domains |

### 2.3 Dialectal Variation

Iraqi Arabic exhibits significant regional linguistic variation:

**Governorates Represented** (in current collection):
1. Baghdad (Central Iraqi)
2. Basra (Southern/Gulf Iraqi)
3. Wasit (Central Iraqi)
4. Karbala (Central Iraqi)
5. Najaf (Southern Iraqi)
6. Dhi Qar (Southern Iraqi)
7. Maysan (Southeastern Iraqi)

**Linguistic Features Reflected**:
- Phonological variation (e.g., *q* vs. *g* in Baghdad)
- Lexical differences (e.g., "شنو" [šnu] vs. "إيش" ['iš] for "what")
- Morphological patterns (e.g., verb form variations)
- Register mixing (colloquial, slang, informal formal)

### 2.4 Text Characteristics

**Average Post Length**: [Ongoing analysis — expected 15-80 tokens]

**Language Mix**: 
- Primarily Iraqi Arabic with code-switching to English
- English appears in: hashtags, URLs, brand names, technical terms
- Estimated English ratio: 2-8% of tokens (varies by post)

**Special Characters**:
- Iraqi-specific graphemes: چ (ch), گ (g), پ (p), ڤ (v)
- Diacritical marks: Tashkeel (vowel marks) — removed in preprocessing
- Punctuation: Varied; includes both ASCII and Arabic punctuation

---

## 3. Data Format Specification

### 3.1 Corpus Format

**File Format**: CSV with UTF-8 encoding

**Required Columns**:

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `text_id` | String | Unique identifier | `IRQ_2024_001234` |
| `text` | String | Raw Iraqi Arabic text | `هسة الكهربا قطعت من أمس` |
| `label_primary` | String | Primary complaint domain | `infrastructure` |
| `label_secondary` | String (nullable) | Secondary domain if multi-domain | `healthcare` |
| `text_normalized` | String | Preprocessed text (diacritics removed, normalized) | `هسه الكهربا قطعت من امس` |
| `dialect_region` | String | Geographic origin (if known) | `baghdad` |
| `is_codeswitched` | Boolean | Whether text contains non-Arabic | `true` |
| `english_tokens` | String (nullable) | Comma-separated English terms | `wifi,internet,problem` |
| `register` | String | Formality level | `colloquial` |
| `source` | String | Data origin | `twitter`, `field_observation`, `facebook` |
| `collection_date` | Date | Collection timestamp (or range) | `2024-03-15` |
| `annotator_id` | String | Annotator identifier (for consensus tracking) | `ANNOTATOR_01` |
| `annotation_confidence` | Float [0-1] | Confidence score for annotation | `0.92` |

### 3.2 Lexicon Format

**File Format**: CSV with UTF-8 encoding

**Columns**:

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| `iraqi_term` | String | Iraqi Arabic word/phrase | `شنو` |
| `msa_equivalent` | String | Modern Standard Arabic equivalent | `ما` + `ذا` → `ماذا` |
| `pos_tag` | String | Part-of-speech | `PRON` (pronoun) |
| `register` | String | Register/style label | `colloquial` |
| `region` | String | Geographic prevalence | `all_regions` / `baghdad` / `southern` |
| `usage_frequency` | String | Estimated frequency | `high` / `medium` / `low` |
| `example_sentence` | String | Context of use | `شنو أخبارك؟` |
| `example_translation` | String | English translation | `How are you?` |
| `notes` | String (nullable) | Linguistic or cultural notes | `Informal greeting` |

### 3.3 Sample Data Structure

**Corpus Sample** (CSV):
```
text_id,text,label_primary,label_secondary,text_normalized,dialect_region,is_codeswitched,english_tokens,register,source
IRQ_2024_0001,هسة الكهربا قطعت من أمس ويا ويلي,infrastructure,,هسه الكهربا قطعت من امس ويا ويلي,baghdad,false,,colloquial,twitter
IRQ_2024_0002,الدراسة توقفت بسبب شي مشاكل في المدرسة,education,,الدراسة توقفت بسبب شي مشاكل في المدرسة,basra,false,,colloquial,facebook
IRQ_2024_0003,My hospital appointment was postponed again اهو الدكتور ما جاهز,healthcare,,my hospital appointment was postponed again اهو الدكتور ما جاهز,najaf,true,my,appointment,was,postponed,colloquial,instagram
```

**Lexicon Sample** (CSV):
```
iraqi_term,msa_equivalent,pos_tag,register,region,usage_frequency,example_sentence,example_translation,notes
شنو,ماذا,PRON,colloquial,all_regions,high,شنو أخبارك؟,What's your news?,Common greeting
خوش,جميل,ADJ,colloquial,central,high,خوش يوم هسه,Nice day today,Positive adjective
يا ويل,يا ويل,INTERJ,colloquial,southern,medium,يا ويل على الزمن,Woe to time,Exclamation of hardship
```

---

## 4. Collection Methodology

### 4.1 Data Collection Approach

**Phase 1: Field Observation (2023-2025)**
- Direct observation across 7 Iraqi governorates
- Transcription of natural civic discourse
- Documentation of complaint contexts
- Ethical protocols: informed consent where possible, anonymization of identifiable information

**Phase 2: Social Media Aggregation**
- Publicly available posts from major platforms
- Anonymization: removal of account handles, timestamps, location data
- Compliance with platform terms of service
- Focus on civic and complaint-related content

**Phase 3: Ongoing Collection**
- Continuous aggregation to expand dialect coverage
- Planned expansion to additional governorates
- Longitudinal tracking of linguistic evolution

### 4.2 Data Cleaning and Normalization

**Preprocessing Pipeline**:

1. **Character Normalization**
   - Alef variants: أ, إ, آ → ا
   - Teh marbuta: ة → ه (context-dependent)
   - Alef maksura: ى → ي
   - Shadda (sukun): Preserved for analysis, removed in normalized version

2. **URL and Mention Removal**
   - URLs stripped (preserved in metadata)
   - @mentions and #hashtags removed (content preserved)
   - Emoji removed (type logged if significant)

3. **Whitespace Normalization**
   - Multiple spaces collapsed to single space
   - Leading/trailing whitespace removed
   - Newlines normalized to spaces

4. **Spelling Variation Handling**
   - Common phonetic misspellings noted but not corrected (reflect actual usage)
   - Repeated characters: multiple repeated vowels normalized (e.g., "ياااا" → "يا")

---

## 5. Annotation Scheme

### 5.1 Domain Classification

**Multi-label Annotation**: Each text receives one primary label and optionally secondary labels for multi-domain complaints.

**Inter-annotator Agreement**:
- Target Cohen's kappa ≥ 0.75 for primary labels
- Dispute resolution protocol: third-party adjudication

### 5.2 Confidence Scoring

Annotations include confidence scores (0.0-1.0) reflecting:
- Annotator certainty in domain classification
- Clarity of complaint type in text
- Presence of ambiguous or overlapping domains

---

## 6. Dataset Statistics

### 6.1 Corpus Size and Distribution

| Metric | Value | Status |
|--------|-------|--------|
| **Total Documents** | [In Progress] | Ongoing collection |
| **Total Tokens** | [In Progress] | Estimated 500K+ at completion |
| **Vocabulary Size** | [In Progress] | Estimated 20K+ unique terms |
| **Average Doc Length** | [In Progress] | Expected 20-80 tokens |
| **Min Doc Length** | [In Progress] | ~ 5 tokens |
| **Max Doc Length** | [In Progress] | ~ 200+ tokens |

### 6.2 Domain Distribution

| Domain | Count | Percentage | Status |
|--------|-------|-----------|--------|
| Infrastructure & Services | [Pending] | — | In collection |
| Healthcare | [Pending] | — | In collection |
| Education | [Pending] | — | In collection |
| Employment | [Pending] | — | In collection |
| Security | [Pending] | — | In collection |
| Housing | [Pending] | — | In collection |
| Administrative Services | [Pending] | — | In collection |
| Mixed/Other | [Pending] | — | In collection |

### 6.3 Dialect Region Coverage

| Region | Documents | Percentage |
|--------|-----------|-----------|
| Baghdad | [In Progress] | — |
| Basra | [In Progress] | — |
| Wasit | [In Progress] | — |
| Karbala | [In Progress] | — |
| Najaf | [In Progress] | — |
| Dhi Qar | [In Progress] | — |
| Maysan | [In Progress] | — |

### 6.4 Code-switching Statistics

| Metric | Value |
|--------|-------|
| Documents with English tokens | [In Progress] |
| Average English ratio (mixed docs) | [In Progress] |
| Most common English terms | [In Progress] |

---

## 7. Intended NLP Applications

### 7.1 Supported Tasks

1. **Multi-class Text Classification**
   - Complaint domain identification
   - Intent detection (complaint, inquiry, suggestion)
   - Urgency prediction

2. **Sentiment Analysis**
   - Polarity classification
   - Emotion detection (frustration, hope, anger)

3. **Named Entity Recognition**
   - Organization names (ministry, hospital, company)
   - Location entities (governorates, districts)
   - Person names (anonymized in dataset)

4. **Dialect Identification**
   - Region prediction from text
   - Dialect feature extraction
   - Register classification

5. **Code-switching Analysis**
   - Language boundary detection
   - Code-switch ratio calculation
   - Loanword identification

### 7.2 Baseline Task Definitions

**Task 1: Domain Classification** (Supervised)
- Input: Raw Iraqi Arabic text
- Output: Primary domain label + confidence score
- Evaluation: Macro-F1, Micro-F1, per-domain precision/recall
- Train/Val/Test split: [To be specified]

**Task 2: Register Classification** (Semi-supervised)
- Input: Iraqi Arabic text
- Output: Register label (colloquial, slang, formal)
- Evaluation: Accuracy, balanced accuracy

---

## 8. Dataset Limitations and Biases

### 8.1 Known Limitations

1. **Ongoing Collection**: Dataset remains under active development; statistics are preliminary
2. **Geographic Imbalance**: Baghdad and southern regions may be over-represented
3. **Source Bias**: Social media text exhibits genre-specific characteristics (informal, topical)
4. **Temporal Snapshot**: Collection reflects 2023-2025 period; linguistic evolution not yet tracked longitudinally
5. **Dialect Simplification**: Regional variations simplified into broad categories; intra-regional variation not fully captured
6. **Annotation Coverage**: Multi-label annotations incomplete; primary labels prioritized

### 8.2 Potential Biases

- **Socioeconomic Bias**: Social media users may not represent full population spectrum
- **Age Bias**: Younger demographics over-represented in online sources
- **Gender**: Unknown gender distribution of online complaint authors
- **Topic Bias**: Urban civic complaints over-represented; rural concerns may be under-sampled

### 8.3 Privacy and Ethical Considerations

✓ **Anonymized**: Personal identifiers systematically removed
✓ **Public Source Only**: No private messages or communications included
✓ **Terms of Service Compliant**: Collection respects platform policies
⚠️ **Consent**: Field observation phase includes appropriate consent protocols

---

## 9. Data Access and Licensing

### 9.1 License

**Data License**: CC BY 4.0 (Creative Commons Attribution 4.0 International)

- Free for academic and commercial use
- Attribution required: cite IANLP and original author (Hussein Hadeh)
- Adaptation permitted with attribution

**Code License**: MIT License

### 9.2 Distribution

- **Repository**: https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-
- **Format**: CSV files in `/corpus` and `/lexicon` directories
- **Access**: Public; no registration required

### 9.3 Restrictions

- Do not remove attribution or license notices
- Derivative works must retain CC BY 4.0 license
- No warranty provided; use as-is

---

## 10. Versioning and Updates

### 10.1 Dataset Versioning Scheme

Format: `v{MAJOR}.{MINOR}`
- **v1.0**: Initial public release (Target: 2025)
- **v1.1**: Expanded corpus (~30% more documents)
- **v2.0**: Additional domains, extended dialect coverage

### 10.2 Changelog

See [CHANGELOG.md](../CHANGELOG.md) for detailed version history.

---

## 11. Citation and References

### 11.1 How to Cite

If you use IANLP dataset in research, please cite:

```bibtex
@dataset{hadeh2025ianlp,
  title={Iraqi Arabic NLP Toolkit (IANLP): 
          Annotated Corpus and Lexicon for Iraqi Dialect NLP},
  author={Hadeh, Hussein},
  year={2025},
  institution={Al-Iraqia University, Baghdad},
  url={https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-},
  note={CC BY 4.0}
}
```

### 11.2 Related Work and Inspiration

This dataset is positioned within the broader landscape of Arabic NLP resources:

- **MADAR Corpus** (Bouamor et al., 2014): Multi-dialect Arabic dataset
- **NADI Shared Task** (Abdul-Awal et al., 2020-2023): Arabic dialect identification benchmark
- **MARBERT** (Abdul-Mageed et al., 2021): Multilingual Arabic BERT model
- **AraBERT** (Antoun et al., 2020): Arabic language model

---

## 12. Contact and Support

**Dataset Maintainer**: Hussein Hadeh
- Email: hussainhade12345@gmail.com
- GitHub: https://github.com/hussainhade12345-max
- Affiliation: Al-Iraqia University, Baghdad

**Questions or Issues**: Open an issue on the GitHub repository or contact the maintainer directly.

---

**Last Updated**: June 2025  
**Dataset Version**: v0.9 (Pre-release)  
**Status**: 🚀 Active Development
