# Iraqi Arabic NLP Toolkit - Annotation Guidelines

## Overview

This document provides comprehensive guidelines for annotating the Iraqi Arabic corpus and lexicon. All annotators must follow these standards to ensure consistency and quality across the dataset.

---

## Part 1: Corpus Annotation Guidelines

### 1.1 Text Domain Classification

All posts in the corpus must be classified into one of 8 predefined domains. Each post can have **multiple labels** (multi-label classification).

#### Domain Definitions

| Domain | Label | Examples |
|--------|-------|----------|
| **Infrastructure & Services** | `infrastructure` | Roads, bridges, public transport, utilities |
| **Electricity & Water** | `electricity_water` | Power outages, water shortages, utility bills |
| **Healthcare** | `healthcare` | Hospital services, medicine availability, doctor access |
| **Education** | `education` | Schools, universities, educational resources, student issues |
| **Employment** | `employment` | Job availability, wages, working conditions, unemployment |
| **Security** | `security` | Safety concerns, crime, protests, conflicts |
| **Housing** | `housing` | Housing availability, rental prices, living conditions |
| **Administrative Services** | `admin_services` | Government services, permits, documentation, bureaucracy |

### 1.2 Multi-Label Classification Rules

Posts often express concerns about multiple domains. Follow these rules:

1. **Identify all applicable domains** — Do not limit to one label per post
2. **Use pipe separator** — Separate multiple labels with `|` (e.g., `healthcare|employment`)
3. **Include all relevant labels** — Even if one domain is primary, include all mentioned domains
4. **No redundancy** — Do not repeat the same label multiple times

**Example:**
```
Text: "المستشفى ما فيه أطباء والشغل ما فيه راتب كويس"
Translation: "The hospital has no doctors and the job doesn't pay well"
Labels: healthcare|employment
```

### 1.3 Confidence Scoring

Rate your confidence in the annotation using the following scale:

| Level | Value | Criteria |
|-------|-------|----------|
| **High** | 3 | Clear, unambiguous domain assignment; no interpretation needed |
| **Medium** | 2 | Reasonably clear; some minor ambiguity but assignment is defensible |
| **Low** | 1 | Ambiguous; multiple valid interpretations; domain assignment is uncertain |

**Examples:**

- **Confidence = 3 (High)**
  ```
  Text: "الكهرباء معطلة من 3 أيام"
  (The electricity has been cut off for 3 days)
  Labels: electricity_water
  ```

- **Confidence = 2 (Medium)**
  ```
  Text: "الشغل صعب والشارع ما آمن"
  (Work is hard and the street is not safe)
  Labels: employment|security
  (Could reasonably include others; context matters)
  ```

- **Confidence = 1 (Low)**
  ```
  Text: "الحال صعب الحمد لله"
  (Things are difficult, praise be to God)
  Labels: [ambiguous - could be multiple domains]
  ```

### 1.4 Governorate Tagging

Identify the governorate where the post originates or primarily references:

**Valid Governorate Values:**
- Wasit
- Baghdad
- Basra
- Karbala
- Najaf
- Dhi Qar
- Maysan
- Mosul
- Other
- Unknown (if not determinable)

**Tagging Rules:**
- Use the governorate **explicitly mentioned** in the text
- If multiple governorates mentioned, use the primary one
- If no governorate mentioned, use "Unknown"

### 1.5 Source Classification

Classify the origin of the post:

**Valid Sources:**
- `twitter` / `x` — X (formerly Twitter) posts
- `facebook` — Facebook posts
- `instagram` — Instagram posts
- `tiktok` — TikTok posts
- `direct_observation` — From field observation notes
- `other` — Other sources

### 1.6 CSV Schema for Corpus

```
post_id,text,governorate,source,date_collected,labels,confidence,notes
```

**Field Descriptions:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `post_id` | String | Unique identifier for the post | `BLOG_001_2024` |
| `text` | String | The full Iraqi Arabic text | `شلونك الحمد لله` |
| `governorate` | String | Governorate of origin | `Baghdad` |
| `source` | String | Source platform | `twitter` |
| `date_collected` | ISO 8601 Date | Collection date | `2024-06-10` |
| `labels` | String | Pipe-separated domain labels | `healthcare\|employment` |
| `confidence` | Integer (1-3) | Annotation confidence | `2` |
| `notes` | String | Optional notes on annotation | `Ambiguous context` |

---

## Part 2: Lexicon Annotation Guidelines

### 2.1 Lexicon Entry Structure

Each entry in the lexicon represents an Iraqi Arabic word or phrase with detailed linguistic information.

### 2.2 CSV Schema for Lexicon

```
id,word,msa_equivalent,english_translation,pos,governorate,register,source,example
```

**Field Descriptions:**

| Field | Type | Description | Rules |
|-------|------|-------------|-------|
| `id` | String | Unique identifier | Format: `LEX_001`, `LEX_002`, etc. |
| `word` | String | The Iraqi Arabic word/phrase | Must be in Arabic script |
| `msa_equivalent` | String | Modern Standard Arabic equivalent | For cross-dialect mapping |
| `english_translation` | String | English translation | Concise, primary meaning |
| `pos` | String | Part of speech | See POS list below |
| `governorate` | String | Geographic region of the word | See governorate list |
| `register` | String | Register/formality level | See register list |
| `source` | String | Where the word was found | `corpus`, `literature`, `speech`, etc. |
| `example` | String | Example usage in sentence | Full sentence in Iraqi Arabic |

### 2.3 Part of Speech (POS) Tags

Use the following POS categories:

| POS | Description | Examples |
|-----|-------------|----------|
| `Noun` | Nouns | كتاب (book), سيارة (car) |
| `Verb` | Verbs | كتب (wrote), ذهب (went) |
| `Adj` | Adjectives | جميل (beautiful), كبير (big) |
| `Adv` | Adverbs | دايم (always), هسه (now) |
| `Phrase` | Multi-word phrases | خوش سالفة (nice conversation) |
| `Interj` | Interjections | يا الله (oh God), واه (wow) |

### 2.4 Register Classification

Classify the formality and context of word usage:

| Register | Description | Usage |
|----------|-------------|-------|
| `Colloquial` | Everyday spoken Iraqi Arabic | شلونك (how are you) |
| `Slang` | Informal, trendy language | كشّاخة (a trick) |
| `Informal` | Non-standard but not slang | ما حصل (didn't happen) |
| `Formal` | Standard/literary register | كان (was - literary form) |

### 2.5 Geographic Scope

Specify where the word/phrase is used:

| Scope | Description |
|-------|-------------|
| `All_Regions` | Used across all Iraqi regions |
| `Central_Iraq` | Baghdad, Wasit, Anbar |
| `Southern_Iraq` | Basra, Dhi Qar, Maysan |
| `Northern_Iraq` | Mosul, Nineveh region |
| `Western_Iraq` | Anbar, Western areas |
| `Wasit` | Specific to Wasit governorate |
| `Baghdad` | Specific to Baghdad |
| `Basra` | Specific to Basra |
| `Mosul` | Specific to Mosul area |
| `Central_and_South` | Central and Southern regions |

### 2.6 Lexicon Entry Examples

**Example 1: Colloquial Word**
```
id: LEX_001
word: شلونك
msa_equivalent: كيف حالك
english_translation: How are you?
pos: Phrase
governorate: All_Regions
register: Colloquial
source: corpus
example: شلونك انت الحمد لله
```

**Example 2: Regional Slang**
```
id: LEX_002
word: كشّاخة
msa_equivalent: خدعة
english_translation: A trick, deception
pos: Noun
governorate: Baghdad
register: Slang
source: speech
example: الكشاخة ما تنجح مع الأذكياء
```

**Example 3: Collocation Phrase**
```
id: LEX_003
word: خوش سالفة
msa_equivalent: قصة جميلة
english_translation: Nice conversation/story
pos: Phrase
governorate: All_Regions
register: Colloquial
source: corpus
example: خوش سالفة قصدت أحكيها لك
```

---

## Part 3: Quality Assurance

### 3.1 Inter-Annotator Agreement

- Minimum 2 annotators per post for corpus entries
- Resolve disagreements through discussion
- Document reasons for conflicting annotations

### 3.2 Consistency Checks

- **Domain consistency**: Same domain terms should be labeled similarly
- **Register consistency**: Verify register assignments match typical usage
- **Governorate consistency**: Geographic tags should reflect documented usage

### 3.3 Common Annotation Errors to Avoid

1. ❌ **Over-labeling** — Adding unnecessary domain labels
2. ❌ **Under-labeling** — Missing valid domain labels
3. ❌ **Inconsistent MSA equivalents** — Different variants of same word
4. ❌ **Incomplete examples** — Examples that don't illustrate usage
5. ❌ **Incorrect register assignment** — Formal words marked as slang

---

## Part 4: Special Cases

### 4.1 Code-Switched Text

When text mixes Arabic and English:

1. Annotate **primarily for Arabic content**
2. Include code-switched words in lexicon if they commonly appear
3. Mark register as "Colloquial" or "Slang"

**Example:**
```
Text: "الشغل أصعب من حقني في هذا الوقت"
(The job is harder than what I deserve right now - mixed)
Labels: employment
```

### 4.2 Ambiguous Governorate Origins

If a post could be from multiple regions:

1. Choose the **most explicitly mentioned** governorate
2. Note ambiguity in the `notes` field
3. Use "Unknown" if no geographic markers

### 4.3 Offensive or Sensitive Content

- Include in dataset (anonymized)
- Add note in `notes` field: "Contains sensitive language"
- Classify according to domain, not by tone

---

## Part 5: Annotation Workflow

1. **Read the text carefully** (2-3 times minimum)
2. **Identify domains** — Mark all applicable labels
3. **Assign confidence** — Based on clarity of classification
4. **Identify governorate** — From explicit or contextual clues
5. **Set source** — Note where post came from
6. **Add notes** — Document any uncertainties or special cases
7. **Review** — Double-check before submission

---

## Contact & Support

For questions about these guidelines, please contact:
- **Hussein Hadeh** (Project Lead)
- Email: hussainhade12345@gmail.com

---

**Last Updated**: June 2025  
**Version**: 1.0
