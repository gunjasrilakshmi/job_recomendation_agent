# 🚀 Jobs Engine — AI Career Intelligence Agent

An AI-powered career assistant that analyzes your resume, searches live jobs, matches you with the best opportunities, and provides personalized career intelligence.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5%20Flash-orange)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 📄 Smart Resume Parser
- Upload PDF resumes
- AI-powered skill extraction using Gemini 2.5 Flash
- Automatic experience level classification
- Role and education identification

### 🔍 Live Job Search
- Real-time job search via Adzuna API (10+ countries)
- Advanced filters: salary range, full-time, location
- Retrieves up to 100 jobs per search

### 🎯 AI Matching Engine
- **Deterministic scoring** — no AI in the matching loop
- TF-IDF vectorization with bigram support
- Cosine similarity for semantic matching
- Direct skill overlap calculation
- **Formula:** `Final Score = 70% × TF-IDF Similarity + 30% × Skill Overlap`

### ⭐ AI Recommendations
- **Skill Gap Analysis** — Strengths, missing skills, priorities
- **Cover Letter Generation** — Tailored to each job posting
- **Interview Preparation** — 10 categorized questions with suggested answers

### 📊 Market Intelligence
- 50,000+ historical job postings analyzed
- Top in-demand skills visualization
- Salary insights by skill, category, and location
- Trending skills with growth analysis
- Personalized eligibility boost recommendations

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| AI | Google Gemini 2.5 Flash |
| Jobs API | Adzuna |
| Matching | Scikit-learn (TF-IDF + Cosine Similarity) |
| Visualization | Plotly |
| Data Processing | Pandas, NumPy |
| PDF Parsing | pdfplumber |
| Database | SQLite (session state) |

---

## 📁 Project Structure

```
job-agent/
├── app.py                          # Main application & home page
├── pages/
│   ├── 1_📄_Upload_Resume.py      # Resume upload & parsing
│   ├── 2_🔍_Job_Search.py         # Live job search & matching
│   ├── 3_⭐_Recommendations.py    # AI recommendations & details
│   └── 4_📊_Analytics.py          # Market intelligence dashboard
├── services/
│   ├── gemini_service.py           # Gemini AI integration
│   ├── adzuna_service.py           # Adzuna Jobs API client
│   ├── matching_service.py         # TF-IDF matching engine
│   └── analytics_service.py       # Dataset analytics & generation
├── utils/
│   ├── pdf_parser.py               # PDF text extraction
│   └── skill_extractor.py          # Keyword-based skill matching
├── data/
│   └── jobs_dataset.csv            # 50k historical jobs (auto-generated)
├── .streamlit/
│   └── config.toml                 # Theme & server configuration
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- API Keys:
  - [Google Gemini API Key](https://aistudio.google.com/apikey)
  - [Adzuna API Credentials](https://developer.adzuna.com/)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd job-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

#### Option 1: Environment Variables
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:ADZUNA_APP_ID = "your-adzuna-app-id"
$env:ADZUNA_APP_KEY = "your-adzuna-app-key"

# macOS/Linux
export GEMINI_API_KEY="your-gemini-api-key"
export ADZUNA_APP_ID="your-adzuna-app-id"
export ADZUNA_APP_KEY="your-adzuna-app-key"
```

#### Option 2: Streamlit Secrets (for local development)
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
ADZUNA_APP_ID = "your-adzuna-app-id"
ADZUNA_APP_KEY = "your-adzuna-app-key"
```

> ⚠️ Never commit `secrets.toml` to version control!

### Run Locally

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## ☁️ Deploy to Streamlit Community Cloud

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/your-username/jobs-engine.git
git push -u origin main
```

### Step 2: Create `.gitignore`
```
venv/
__pycache__/
.streamlit/secrets.toml
*.pyc
data/jobs_dataset.csv
database/
```

### Step 3: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repository
4. Set **Main file path** to `app.py`
5. Click **"Deploy"**

### Step 4: Configure Secrets
1. In the Streamlit Cloud dashboard, go to your app
2. Click **"Settings"** → **"Secrets"**
3. Add your API keys:
```toml
GEMINI_API_KEY = "your-gemini-api-key"
ADZUNA_APP_ID = "your-adzuna-app-id"
ADZUNA_APP_KEY = "your-adzuna-app-key"
```

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ |
| `ADZUNA_APP_ID` | Adzuna application ID | ✅ |
| `ADZUNA_APP_KEY` | Adzuna application key | ✅ |

---

## 📊 How the Matching Engine Works

```
User Profile (skills + roles + summary)
            │
            ▼
    ┌───────────────┐
    │  TF-IDF       │  ── Vectorize user profile + all job descriptions
    │  Vectorizer   │     with bigrams, 5000 max features
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │   Cosine      │  ── Compute similarity between user vector
    │  Similarity   │     and each job vector
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │  Skill        │  ── Count exact skill matches between
    │  Overlap      │     user skills and job text
    └───────┬───────┘
            │
            ▼
    Final Score = 0.70 × Cosine Similarity + 0.30 × Skill Overlap
            │
            ▼
    Return Top 10 Jobs (sorted by score)
```

---

## 📝 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) — AI-powered analysis
- [Adzuna](https://developer.adzuna.com/) — Live job data
- [Streamlit](https://streamlit.io/) — Application framework
- [Scikit-learn](https://scikit-learn.org/) — Machine learning algorithms
- [Plotly](https://plotly.com/) — Interactive visualizations
