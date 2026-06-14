# IANLP Annotation Guidelines

## Table of Contents
1. [Introduction](#introduction)
2. [Domain Definitions](#domain-definitions)
3. [Annotation Workflow](#annotation-workflow)
4. [Quality Control](#quality-control)
5. [Edge Cases and Disputes](#edge-cases-and-disputes)
6. [Register Classification](#register-classification)

---

## Introduction

This document provides comprehensive guidelines for annotating Iraqi Arabic complaint texts in the IANLP dataset. Annotators should read this document completely before beginning annotation work.

### Key Principles

- **Clarity**: Each complaint should be assigned to the most appropriate domain
- **Consistency**: Follow guidelines uniformly across all annotations
- **Transparency**: Document difficult decisions and rationales
- **Quality**: Maintain high inter-annotator agreement (target: κ ≥ 0.75)

---

## Domain Definitions

### 1. Infrastructure & Services (INFRA)

**Definition**: Complaints about public infrastructure, utilities, and essential services.

**Includes**:
- Electricity/power (outages, quality, billing)
- Water supply (availability, quality, contamination)
- Sewage and sanitation
- Roads and transportation infrastructure
- Internet and telecommunications
- Waste management and garbage collection
- Gas supply

**Examples**:
- "الكهربا قطعت من 20 ساعة متتالية" (Electricity cut for 20 consecutive hours)
- "الماء ما يصير أمس وأليوم" (No water yesterday and today)
- "الشارع مخرب والحفر كثيرة" (The street is damaged with many potholes)

**Does NOT Include**:
- Individual household repairs (→ Housing)
- Public transportation service complaints (→ Transportation, separate subcategory if available)
- Business internet/services (→ Employment if work-related)

---

### 2. Healthcare (HEALTH)

**Definition**: Complaints about medical services, hospitals, clinics, and health system issues.

**Includes**:
- Hospital capacity and waiting times
- Medication availability
- Doctor or specialist access
- Healthcare facility conditions
- Medical billing or insurance
- Public health concerns (disease, pandemic response)
- Medical emergency response times

**Examples**:
- "المستشفى ما فيها أطباء وكل الناس واقفة" (Hospital has no doctors, people waiting)
- "الدواء ما موجود من شهرين" (Medication unavailable for two months)
- "سعر الجراحة غالي كتير" (Surgery cost is very expensive)

**Does NOT Include**:
- Individual health advice (too vague without institutional context)
- School health services (→ Education)
- Workplace health and safety (→ Employment)

---

### 3. Education (EDUC)

**Definition**: Complaints about schools, universities, educational systems, and learning environments.

**Includes**:
- School infrastructure (buildings, classrooms, facilities)
- Teacher availability or quality
- Curriculum issues
- Student discipline or harassment
- Educational delays or closures
- University administration
- Educational resources (textbooks, lab equipment)

**Examples**:
- "المدرسة ما فيها تدفية والحر كتير" (School has no heating, very hot)
- "التعليم الاونلاين من أسوأ حاجة" (Online education is the worst thing)
- "الجامعة أغلقت الفصل الدراسي" (University closed the semester)

**Does NOT Include**:
- Individual student grades or academic performance
- Scholarship/funding complaints (→ Employment if work-study-related, otherwise Administrative)
- School transportation (→ Infrastructure)

---

### 4. Employment (EMPLOY)

**Definition**: Complaints about labor, jobs, wages, and workplace conditions.

**Includes**:
- Wage or salary disputes
- Working conditions (safety, hours, benefits)
- Job availability or discrimination
- Workplace harassment or abuse
- Labor rights violations
- Unemployment
- Contract disputes

**Examples**:
- "الراتب ما يكفي العيش" (Salary doesn't cover living costs)
- "الشغل 12 ساعة بدون فترات استراحة" (Work 12 hours without breaks)
- "قالولي ما في وظايف الآن" (They told me no jobs available now)

**Does NOT Include**:
- Individual business service complaints (→ Administrative Services)
- Complaints about school-related work/study programs if focus is educational (→ Education)

---

### 5. Security (SECURITY)

**Definition**: Complaints about safety, crime, policing, and security concerns.

**Includes**:
- Crime (theft, robbery, assault)
- Police response or behavior
- Neighborhood safety
- Traffic violations or enforcement
- Personal security concerns
- Gang or militia activity
- Curfews and movement restrictions

**Examples**:
- "هسة السرقة كثيرة بالحي" (Theft is common in the neighborhood now)
- "الشرطة ما تجي لما نستنجد" (Police don't come when we call for help)
- "ما يصير نطلع بالليل من الخوف" (Can't go out at night from fear)

**Does NOT Include**:
- General political instability (too broad; classify as Mixed/Other)
- Military or war-related complaints (→ Mixed/Other)

---

### 6. Housing (HOUSING)

**Definition**: Complaints about residential housing, real estate, and housing-related services.

**Includes**:
- Rent disputes or increases
- Housing quality or maintenance issues
- Eviction or tenancy disputes
- Housing construction delays
- Property damage or repairs
- Housing programs or government services
- Neighborhood living conditions (non-security)

**Examples**:
- "صاحب البيت زاد الأجار" (Landlord raised the rent)
- "السقف يرش والحيط رطب" (Roof leaks and walls are damp)
- "بناء البيت توقف من 3 سنين" (House construction stopped 3 years ago)

**Does NOT Include**:
- Commercial property (→ Employment/Administrative)
- School/hospital building conditions (→ Education/Healthcare)
- Public infrastructure (→ Infrastructure)

---

### 7. Administrative Services (ADMIN)

**Definition**: Complaints about government bureaucracy, documentation, permits, and administrative processes.

**Includes**:
- Document processing (passports, IDs, certificates)
- Licensing and permits
- Government office delays
- Bureaucratic procedures
- Registration and enrollment
- Civil service complaints
- Tax or fee disputes
- Public benefits or assistance

**Examples**:
- "تجديد الجواز يأخذ وقت طويل" (Passport renewal takes a long time)
- "رفضوا طلبي بدون سبب واضح" (They rejected my application without clear reason)
- "المكتب الحكومي يفتح ساعة واحدة بالأسبوع" (Government office opens one hour per week)

**Does NOT Include**:
- Health-related documentation (→ Healthcare)
- Educational certifications (→ Education)
- Employment-related documentation (→ Employment)

---

### 8. Mixed / Other (MIXED)

**Definition**: Complaints spanning multiple domains or not fitting clearly into single categories.

**When to Use**:
- Multi-domain complaints (use secondary labels when possible)
- Systemic issues affecting multiple sectors
- Complaints too vague for single classification
- Political or governance-level complaints
- General social issues

**Examples**:
- "المناطق المحررة ما فيها كهربا ولا مدارس" (Liberated areas have no electricity or schools)
- "الحكومة ما تسوي حاجة صحيحة" (Government doesn't do anything right) [too vague; use Mixed]

**Try to Avoid**: Use Mixed as a last resort; always attempt primary domain assignment first.

---

## Annotation Workflow

### Step 1: Read and Understand

1. Read the complaint text completely
2. Note any ambiguities or unclear elements
3. Consider context and implicit information

### Step 2: Identify Primary Domain

1. Ask: "What is the main subject of this complaint?"
2. Match against domain definitions above
3. Assign most appropriate single domain
4. Record confidence: High (H), Medium (M), or Low (L)

### Step 3: Identify Secondary Domain (if applicable)

1. Ask: "Are there other significant complaint domains here?"
2. If yes, assign secondary domain
3. If equally weighted, mark both as primary/secondary equally

### Step 4: Record Register

Classify formality level:
- **Colloquial**: Informal, street language, slang
- **Formal**: Official or careful speech
- **Mixed**: Both registers present

### Step 5: Verify and Review

1. Re-read annotation
2. Check consistency with other similar examples
3. Flag for review if uncertain (confidence = L)

---

## Quality Control

### Inter-Annotator Agreement

- **Target**: Cohen's kappa ≥ 0.75 for primary domain labels
- **Measurement**: Calculate κ on ~15% of corpus (overlap set)
- **Resolution**: When κ < 0.75, review guidelines and retrain

### Review Process

1. **Spot Checks**: Supervisor reviews 5-10% of all annotations
2. **Dispute Resolution**: 
   - If disagreement, discuss with annotator
   - Document rationale for final decision
   - Update guidelines if clarification needed
3. **Periodic Retraining**: Monthly calibration meetings between annotators

### Confidence Scoring

Record confidence level for each annotation:

| Level | Definition | When to Use |
|-------|-----------|------------|
| **High** | Clear complaint type; obvious domain | Straightforward examples |
| **Medium** | Reasonably clear; minor ambiguity | Some context needed |
| **Low** | Ambiguous or multi-domain; difficult | Flag for adjudication |

---

## Edge Cases and Disputes

### Ambiguous Cases

**Case 1**: "ما في خدمات حكومية"
- Complaint: "No government services" [too vague]
- Decision: Use Mixed; ask for clarification

**Case 2**: "المدرسة ما في طاقة كهربائية"
- Complaint: School without electricity
- Primary: Education (school infrastructure)
- Secondary: Infrastructure (utilities)

**Case 3**: "ما لقيت دواء في المستشفى والدواخيل ما تجيب"
- Complaint: Can't find medicine; pharmacy not stocked
- Primary: Healthcare
- Secondary: Optional (not Infrastructure unless specific utility failure implied)

### Multi-Domain Prioritization

**Rule of Thumb**: When multiple domains equally present, choose in this priority order:

1. **Most specific** domain (Healthcare > Mixed)
2. **Most actionable** domain (Employment wage dispute > Housing neighborhood)
3. **Most immediate** issue (Security threat > Administrative delay)

---

## Register Classification

### Formality Levels in Iraqi Arabic

**Colloquial (Ammiyya - العامية)**
- Markers: Relaxed grammar, local slang, dialect-specific words
- Example: "شنو هالجوّ قاسي كتير"

**Formal (Fusha-influenced)**
- Markers: Careful grammar, MSA vocabulary, bureaucratic language
- Example: "الأوضاع الأمنية متدهورة جداً"

**Mixed**
- Uses both registers in single text
- Example: "الدكتور ما شخص المرض بشكل صحيح والحالة critical جداً"

---

## Contact and Questions

For annotation clarifications or disputes, contact:
- **Coordinator**: Hussein Hadeh
- **Email**: hussainhade12345@gmail.com

---

**Annotation Guidelines Version**: 1.0  
**Last Updated**: June 2025
