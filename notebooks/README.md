# IANLP Analysis Notebooks

This directory contains Jupyter notebooks for exploratory data analysis, visualization, and baseline model development on the Iraqi Arabic NLP Toolkit dataset.

## Notebooks

### 1. `exploratory_analysis.ipynb`

**Purpose**: Initial dataset exploration and statistical analysis

**Contents**:
- Dataset size and composition
- Domain distribution visualizations
- Text length distributions
- Vocabulary statistics
- Dialect region coverage
- Code-switching analysis
- Register distribution

**To Run**:
```bash
jupyter notebook exploratory_analysis.ipynb
```

### 2. `preprocessing_demo.ipynb` [Upcoming]

**Purpose**: Demonstrate preprocessing pipeline and normalization

**Planned Contents**:
- Character normalization examples
- Before/after comparisons
- Code-switching detection demo
- Preprocessing impact on text statistics

### 3. `baseline_classification.ipynb` [Upcoming]

**Purpose**: Baseline models for domain classification

**Planned Contents**:
- TF-IDF + Logistic Regression baseline
- Vocabulary analysis by domain
- Cross-validation results
- Error analysis

---

## Requirements

Install dependencies:
```bash
pip install -r ../requirements.txt
jupyter
```

## Data Access

Notebooks expect data in:
```
../corpus/train.csv
../corpus/validation.csv
../corpus/test.csv
../lexicon/iraqi_lexicon.csv
```

---

**Last Updated**: June 2025
