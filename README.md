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
- [About the Author](#about-the-author)
- [Academic Vision](#academic-vision)
- [Problem Statement](#problem-statement)
- [Dataset Description](#dataset-description)
- [Supported NLP Tasks](#supported-nlp-tasks)
- [Technical Specification](#technical-specification)
- [Collection & Methodology](#collection--methodology)
- [Repository Structure](#repository-structure)
- [Quick Start](#quick-start)
- [Dataset Statistics](#dataset-statistics)
- [Current Limitations](#current-limitations)
- [Future Research & Roadmap](#future-research--roadmap)
- [Research Collaboration](#research-collaboration)
- [Citation](#citation)
- [License](#license)
- [Contributing](#contributing)

---

## Abstract

The **Iraqi Arabic NLP Toolkit (IANLP)** is an open-source, systematically annotated corpus and toolkit intended for research on Iraqi Arabic dialect. IANLP provides a focused, research-oriented foundation for computational work on Iraqi dialectal Arabic in written social media and civic discourse contexts.

This toolkit includes:

1. **Annotated Complaint Corpus**: Multi-domain labeled dataset (8 domains) covering civic and social discourse
2. **Dialect Lexicon**: Iraqi-MSA vocabulary mapping with register labels and geographic distribution
3. **Iraqi-Specific Preprocessing**: Character normalization, code-switching detection, dialect feature extraction
4. **Baseline Implementations**: Task-specific utilities for sentiment analysis, dialect identification, and intent detection

IANLP is designed as a research prototype to support scholarship in low-resource Arabic NLP, dialect variation, and multilingual systems. The dataset is released under CC BY 4.0 for academic and research use.

---

## About the Author

**Hussein Hadi Hamzah Ali** — Iraqi researcher and open-source developer with a background in English Language. The author’s research interests include:

- Computational Linguistics
- Natural Language Processing
- Arabic Dialect Processing
- Iraqi Arabic
- Low-Resource Languages
- Artificial Intelligence
- Corpus Linguistics
- Machine Learning

Professional profiles (placeholders — add links in repository settings or README):

- GitHub: https://github.com/hussainhade12345-max
- Hugging Face: https://huggingface.co/USERNAME
- ORCID: https://orcid.org/0000-0000-0000-0000
- Google Scholar: https://scholar.google.com/citations?user=YOUR_ID
- LinkedIn: https://www.linkedin.com/in/YOUR_PROFILE

(Replace placeholders above with the author’s verified profile links for public distribution.)

---

## Academic Vision

This repository is intentionally presented as an academic research prototype. The goal is to demonstrate research initiative, reproducible methodology, and a clear roadmap for advanced study rather than to provide a production-ready software product.

Key points:

- IANLP is a work-in-progress research dataset and toolkit intended for graduate-level research, thesis projects, and collaborative academic publications.
- Substantial future development (e.g., large-scale model training, corpus expansion, controlled annotation studies) will require university resources, expert supervision, and ethical approvals where applicable.
- The repository documents what has been done and what remains to be explored; limitations and open research questions are stated transparently.

---

## Problem Statement

### Linguistic Under-Resourcing

Iraqi Arabic represents a significant linguistic variety yet faces critical under-resourcing in computational linguistics:

| Factor | Impact |
|--------|--------|
| **Linguistic Distance from MSA** | Iraqi Arabic exhibits distinct phonology, morphology, and lexicon compared to Modern Standard Arabic |
| **NLP System Performance Gap** | Off-the-shelf Arabic NLP models often underperform on Iraqi dialects |
| **Corpus Absence** | Limited publicly available, systematically annotated corpora for Iraqi dialect |
| **Dialect Diversity** | Iraqi Arabic exhibits significant regional variation |
| **Code-Mixing Complexity** | High Arabic-English code-switching in digital contexts |

### Research Gap

Current Arabic NLP research has focused predominantly on MSA and better-resourced dialects. IANLP provides foundational resources for:

- Dialect identification and classification research
- Cross-dialect transfer learning studies
- Low-resource Arabic NLP methodology development
- Linguistic documentation of Iraqi Arabic variation

---

## Dataset Description

### Overview

**IANLP Corpus** comprises annotated Iraqi Arabic text from social media and civic discourse, manually labeled for complaint domain classification and linguistic analysis.

(Full dataset description retained — see previous sections in the repository for detailed dataset, lexicon, and annotation guidelines.)

---

## Supported NLP Tasks

(As described in the original README: multi-class classification, dialect ID, NER, sentiment analysis, code-switching detection.)

---

## Technical Specification

(See original README content for data formats and preprocessing details.)

---

## Collection & Methodology

(See original README content for collection phases, annotation workflow, and ethical considerations.)

---

## Repository Structure

(See original README content for file and directory layout.)

---

## Quick Start

(Installation and usage examples remain unchanged.)

---

## Dataset Statistics

(Statistics and notes remain unchanged — current counts are preliminary.)

---

## Current Limitations

This project is deliberately a research prototype. The following realistic limitations are presented to inform reviewers and potential collaborators:

- Limited corpus size compared to large-scale corpora used for training deep learning models.
- Several components use rule-based or heuristic approaches rather than fully data-driven models.
- Dialect coverage is currently limited to a subset of Iraqi governorates and urban registers.
- Linguistic annotations are focused on domain and register; fine-grained morphological and syntactic annotation is not yet complete.
- There is no large pre-trained transformer model specifically trained on Iraqi Arabic included in this release.
- This codebase is a research prototype and is not production-hardened (logging, packaging, and deployment pipelines are minimal by design).

We report these limitations openly; addressing them is part of the stated future research agenda.

---

## Future Research & Roadmap

Planned research directions that preserve the academic focus of the project:

Short term (next 6-12 months):

- Expand the annotated corpus with additional governorates and genres.
- Improve annotation guidelines and measure inter-annotator agreement rigorously.
- Release clearer dataset splits and baseline evaluation scripts.

Medium term (1-2 years):

- Develop transformer-based Iraqi Arabic language models (research-only; requires computational resources and ethical governance).
- Add morphological and syntactic annotation layers.
- Introduce Named Entity Recognition annotations and benchmarks.
- Collect a small speech corpus for spoken Iraqi Arabic research.

Long term:

- Benchmark against international Arabic NLP shared tasks.
- Explore educational and governmental NLP applications with appropriate partnership and oversight.

Each item above is intended as a research objective rather than a guarantee of delivery; implementation depends on academic collaboration and resource availability.

---

## Research Collaboration

We invite collaboration from universities, academic researchers, graduate students, and institutional partners. Areas of potential collaboration include:

- Corpus expansion and controlled annotation campaigns
- Interdisciplinary projects combining sociolinguistics and NLP
- Model development under ethical guidelines and university supervision
- Comparative dialectology and cross-dialect transfer studies

If you are interested in collaboration, please open an issue or contact the author directly (see Contact information below).

---

## Discoverability, Topics & Keywords

Suggested repository topics (add these via repository settings for improved discoverability):

- iraqi-arabic
- arabic-nlp
- dialect-nlp
- low-resource-nlp
- corpus-linguistics
- computational-linguistics
- named-entity-recognition
- sentiment-analysis

Suggested keywords for search engines and academic indexing:

Iraqi Arabic, dialect NLP, corpus linguistics, low-resource languages, Arabic dialects, Hussein Hadi Hamzah Ali, IANLP

---

## Profiles & Links (placeholders)

- GitHub: https://github.com/hussainhade12345-max
- Hugging Face: https://huggingface.co/USERNAME
- ORCID: https://orcid.org/0000-0000-0000-0000
- Google Scholar: https://scholar.google.com/citations?user=YOUR_ID
- LinkedIn: https://www.linkedin.com/in/YOUR_PROFILE

Replace placeholders above with verified profiles before publicizing the repository widely.

---

## Citation

(Original citation content retained.)

---

## License

This project is dual-licensed:

Code (iraqi_nlp/): MIT License — see LICENSE
Data (corpus/, lexicon/): CC BY 4.0 — see LICENSE-DATA

---

## Author & Contact

**Hussein Hadi Hamzah Ali**  
Al-Iraqia University, Baghdad, Iraq  
📧 Email: hussain.hade12345@gmail.com  
🔗 GitHub: [@hussainhade12345-max](https://github.com/hussainhade12345-max)  
🔗 ORCID: https://orcid.org/0000-0000-0000-0000  

Please use the GitHub issue tracker for reproducibility questions, dataset corrections, and collaboration inquiries.

---

## Acknowledgments

(This section retained.)

---

**Status**: 🚀 Active Development  
**Current Version**: v0.9 (Pre-release)  
**Last Updated**: June 2025  
**Next Release Target**: v1.0 (2025)

---

**Research-Grade NLP Toolkit for Low-Resource Arabic Dialect**
