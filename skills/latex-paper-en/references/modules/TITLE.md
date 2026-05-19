# Module: Title Optimization

**Trigger**: title, 标题, title optimization, create title, improve title

**Purpose**: Generate and optimize paper titles following IEEE/ACM/Springer/NeurIPS best practices.

**Usage Examples**:

**Generate title from content**:
```bash
uv run python -B scripts/optimize_title.py main.tex --generate
# Analyzes abstract/introduction to propose 3-5 title candidates
```

**Optimize existing title**:
```bash
uv run python -B scripts/optimize_title.py main.tex --optimize
# Analyzes current title and provides improvement suggestions
```

**Check title quality**:
```bash
uv run python -B scripts/optimize_title.py main.tex --check
# Evaluates title against best practices (score 0-100)
```

**Title Quality Criteria** (Based on IEEE Author Center & Top Venues):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Conciseness** | 25% | Remove "A Study of", "Research on", "Novel", "New", "Improved" |
| **Searchability** | 30% | Key terms (Method + Problem) in first 65 characters |
| **Length** | 15% | Optimal: 10-15 words; Acceptable: 8-20 words |
| **Specificity** | 20% | Concrete method/problem names, not vague terms |
| **Jargon-Free** | 10% | Avoid obscure abbreviations (except AI, LSTM, DNA, etc.) |

**Title Generation Workflow**:

**Step 1: Content Analysis**
Extract from abstract/introduction:
- **Problem**: What challenge is addressed?
- **Method**: What approach is proposed?
- **Domain**: What application area?
- **Key Result**: What is the main achievement? (optional)

**Step 2: Keyword Extraction**
Identify 3-5 core keywords:
- Method keywords: "Transformer", "Graph Neural Network", "Reinforcement Learning"
- Problem keywords: "Time Series Forecasting", "Fault Detection", "Image Segmentation"
- Domain keywords: "Industrial Control", "Medical Imaging", "Autonomous Driving"

**Step 3: Title Template Selection**
Common patterns for top venues:

| Pattern | Example | Use Case |
|---------|---------|----------|
| Method for Problem | "Transformer-Based Approach for Time Series Forecasting" | General research |
| Method: Problem in Domain | "Graph Neural Networks: Fault Detection in Industrial Systems" | Domain-specific |
| Problem via Method | "Time Series Forecasting via Attention Mechanisms" | Method-focused |
| Method + Key Feature | "Lightweight Transformer for Real-Time Object Detection" | Performance-focused |

**Step 4: Title Candidates Generation**
Generate 3-5 candidates with different emphasis:
1. Method-focused
2. Problem-focused
3. Application-focused
4. Balanced (recommended)
5. Concise variant

**Step 5: Quality Scoring**
Each candidate receives:
- Overall score (0-100)
- Breakdown by criterion
- Specific improvement suggestions

**Title Optimization Rules**:

**Remove Ineffective Words**:
| Avoid | Reason |
|-------|--------|
| A Study of | Redundant (all papers are studies) |
| Research on | Redundant (all papers are research) |
| Novel / New | Implied by publication |
| Improved / Enhanced | Vague without specifics |
| Based on | Often unnecessary |
| Using / Utilizing | Can be replaced with prepositions |

**Preferred Structures**:
```
Good: "Transformer for Time Series Forecasting in Industrial Control"
Bad:  "A Novel Study on Improved Time Series Forecasting Using Transformers"

Good: "Graph Neural Networks for Fault Detection"
Bad:  "Research on Novel Fault Detection Based on GNNs"

Good: "Attention-Based LSTM for Multivariate Time Series Prediction"
Bad:  "An Improved LSTM Model Using Attention Mechanism for Prediction"
```

**Keyword Placement Strategy**:
- **First 65 characters**: Most important keywords (Method + Problem)
- **Avoid starting with**: Articles (A, An, The), prepositions (On, In, For)
- **Prioritize**: Nouns and technical terms over verbs and adjectives

**Abbreviation Guidelines**:
| Acceptable | Avoid in Title |
|------------|----------------|
| AI, ML, DL | Obscure domain-specific acronyms |
| LSTM, GRU, CNN | Chemical formulas (unless very common) |
| IoT, 5G, GPS | Lab-specific abbreviations |
| DNA, RNA, MRI | Non-standard method names |

**Venue-Specific Adjustments**:

**IEEE Transactions**:
- Avoid formulas with subscripts (except simple ones like "Nd–Fe–B")
- Use title case (capitalize major words)
- Typical length: 10-15 words
- Example: "Deep Learning for Predictive Maintenance in Smart Manufacturing"

**ACM Conferences**:
- More flexible with creative titles
- Can use colons for subtitles
- Typical length: 8-12 words
- Example: "AttentionFlow: Visualizing Attention Mechanisms in Neural Networks"

**Springer Journals**:
- Prefer descriptive over creative
- Can be slightly longer (up to 20 words)
- Example: "A Comprehensive Framework for Real-Time Anomaly Detection in Industrial IoT Systems"

**NeurIPS/ICML**:
- Concise and impactful (8-12 words)
- Method name often prominent
- Example: "Transformers Learn In-Context by Gradient Descent"

**Output Format**:

```latex
% ============================================================
% TITLE OPTIMIZATION REPORT
% ============================================================
% Current Title: "A Novel Study on Time Series Forecasting Using Deep Learning"
% Quality Score: 45/100
%
% Issues Detected:
% 1. [Critical] Contains "Novel Study" (remove ineffective words)
% 2. [Major] Vague method description ("Deep Learning" too broad)
% 3. [Minor] Length acceptable (9 words) but could be more specific
%
% Recommended Titles (Ranked):
%
% 1. "Transformer-Based Time Series Forecasting for Industrial Control" [Score: 92/100]
%    - Concise: ✅ (8 words)
%    - Searchable: ✅ (Method + Problem in first 50 chars)
%    - Specific: ✅ (Transformer, not just "Deep Learning")
%    - Domain: ✅ (Industrial Control)
%
% 2. "Attention Mechanisms for Multivariate Time Series Prediction" [Score: 88/100]
%    - Concise: ✅ (7 words)
%    - Searchable: ✅ (Key terms upfront)
%    - Specific: ✅ (Attention, Multivariate)
%    - Note: Consider adding domain if space allows
%
% 3. "Deep Learning Approach to Time Series Forecasting in Smart Manufacturing" [Score: 78/100]
%    - Concise: ⚠️ (10 words, acceptable)
%    - Searchable: ✅
%    - Specific: ⚠️ ("Deep Learning" still broad)
%    - Domain: ✅ (Smart Manufacturing)
%
% Keyword Analysis:
% - Primary: Transformer, Time Series, Forecasting
% - Secondary: Industrial Control, Attention, LSTM
% - Searchability: "Transformer Time Series" appears in 1,234 papers (good balance)
%
% Suggested LaTeX Update:
% \title{Transformer-Based Time Series Forecasting for Industrial Control}
% ============================================================
```

**Interactive Mode** (Recommended):
```bash
uv run python -B scripts/optimize_title.py main.tex --interactive
# Step-by-step guided title creation with user input
```

**Batch Mode** (For multiple papers):
```bash
uv run python -B scripts/optimize_title.py "papers/*.tex" --batch --output title_report.json
```

**Title A/B Testing** (Optional):
```bash
uv run python -B scripts/optimize_title.py main.tex --compare "Title A" "Title B" "Title C"
# Compares multiple title candidates with detailed scoring
```

**Best Practices Summary**:
1. **Start with keywords**: Put Method + Problem in first 10 words
2. **Be specific**: "Transformer" > "Deep Learning" > "Machine Learning"
3. **Remove fluff**: Delete "Novel", "Study", "Research", "Based on"
4. **Check length**: Aim for 10-15 words (English)
5. **Test searchability**: Would you find this paper with these keywords?
6. **Avoid jargon**: Unless it's widely recognized (AI, LSTM, CNN)
7. **Match venue style**: IEEE (descriptive), ACM (creative), NeurIPS (concise)

Reference: [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/), [Royal Society Blog](https://royalsociety.org/blog/2025/01/title-abstract-and-keywords-a-practical-guide-to-maximizing-the-visibility-and-impact-of-your-papers/)

