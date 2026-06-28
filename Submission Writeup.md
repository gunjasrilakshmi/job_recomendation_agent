# 📋 Submission Writeup — Jobs Engine: AI Career Intelligence Agent

> **Project:** Jobs Engine — AI Career Intelligence Agent
> **Repository:** `career-intelligence-agent`
> **Stack:** Python · Streamlit · Google Gemini 2.5 Flash · ADK · Adzuna API · Scikit-learn
---

## 1. Problem Statement

Job-seekers today face a fragmented, time-consuming process: manually sifting through hundreds of listings, guessing which roles they qualify for, writing cover letters from scratch, and self-studying for every interview without targeted preparation. This burden falls hardest on:

- **Career changers** who do not know how their existing skills map to new fields.
- **Recent graduates** who lack benchmarks for comparing their profiles against market demand.
- **Mid-career professionals** who need efficient targeting to avoid spray-and-pray applications.

Existing platforms surface jobs but do nothing to bridge the gap between *finding* a listing and *winning* an offer. There is no end-to-end AI assistant that reads a candidate's actual resume, compares it to the live market, scores fit deterministically, explains gaps, writes application materials, and coaches for interviews — all in a single session.

**Jobs Engine solves this.** It is an agentic AI system that turns a PDF resume into a fully personalised job-search workflow in minutes.

---

## 2. Solution Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER (Browser via Streamlit)                    │
│             Upload Resume PDF | Search Jobs | View Recommendations       │
└────────────────────┬──────────────────────────────────────────────┬─────┘
                     │                                              │
          ┌──────────▼──────────┐                       ┌──────────▼──────────┐
          │  📤 Resume Upload   │                       │  📊 Analytics       │
          │  pages/1_Upload...  │                       │  pages/4_Analytics  │
          └──────────┬──────────┘                       └─────────────────────┘
                     │ PDF text
          ┌──────────▼──────────────────────────┐
          │  🤖 Resume Analysis Agent            │  ← Gemini 2.5 Flash
          │  services/gemini_service.py          │    extract_resume_info()
          │  utils/pdf_parser.py                 │
          │  utils/skill_extractor.py            │
          └──────────┬──────────────────────────┘
                     │ Structured profile (skills, roles, level)
          ┌──────────▼──────────────────────────┐
          │  🔍 Job Analysis Agent (Orchestrator)│  ← services/job_search_agent.py
          │  services/job_search_agent.py        │    run_job_search_agent()
          └────────┬─────────────────────────────┘
                   │
         ┌─────────▼─────────────────────────────────────────┐
         │         MCP Tool Layer (External Services)         │
         │  ┌──────────────────────┐  ┌────────────────────┐ │
         │  │  🌐 Adzuna API Tool  │  │  🧠 Gemini LLM Tool│ │
         │  │  services/adzuna_    │  │  services/gemini_  │ │
         │  │  service.py          │  │  service.py        │ │
         │  └──────────┬───────────┘  └────────────────────┘ │
         └─────────────┼──────────────────────────────────────┘
                       │ Raw job listings (up to 100)
         ┌─────────────▼───────────────────────────┐
         │  🎯 Match Scoring Agent                  │  ← Deterministic
         │  services/matching_service.py            │    TF-IDF + Cosine + Skill Overlap
         └─────────────┬───────────────────────────┘
                       │ Ranked jobs with scores
         ┌─────────────▼───────────────────────────┐
         │  🔐 Security Checkpoint                  │  ← PII scan + audit log
         │  (validation layer in pages/2_Job_Search │
         │   and pages/3_Recommendations)           │
         └─────────────┬───────────────────────────┘
                       │ Sanitised, approved results
         ┌─────────────▼──────────────────────────────────────────────────┐
         │                Recommendation Layer                             │
         │  ┌──────────────────┐  ┌────────────────┐  ┌────────────────┐ │
         │  │ ✍️  Resume        │  │ 🎤 Interview   │  │ 🗺️  Career     │ │
         │  │    Tailoring     │  │    Coach       │  │    Roadmap    │ │
         │  │    Agent         │  │    Agent       │  │    Agent      │ │
         │  │ generate_cover_  │  │ generate_      │  │ analyze_      │ │
         │  │ letter()         │  │ interview_     │  │ skill_gap()   │ │
         │  │                  │  │ questions()    │  │               │ │
         │  └──────────────────┘  └────────────────┘  └────────────────┘ │
         └─────────────────────────────────┬──────────────────────────────┘
                                           │
                               ┌───────────▼──────────┐
                               │  ✋ Human Approval     │
                               │  (HITL Gate)          │
                               │  Review cover letter, │
                               │  confirm job apply    │
                               └──────────────────────┘
```

> The architecture diagram image is also available at `assets/architecture_diagram.png`.

---

## 3. Concepts Used

### 3.1 ADK Workflow

The agent orchestration follows the **ADK Sequential Workflow** pattern. Each page in the Streamlit app represents a discrete workflow stage, and session state (`st.session_state`) is the shared context store that carries artefacts (parsed resume, ranked jobs, cover letter, interview Q&A) between stages — equivalent to ADK's workflow state passing.

| Stage | ADK Concept | File |
|---|---|---|
| Ingest PDF → extract text | Input processing | `utils/pdf_parser.py` |
| Extract profile | LlmAgent call | `services/gemini_service.py` — `extract_resume_info()` |
| Search live jobs | Tool invocation | `services/adzuna_service.py` — `search_jobs()` |
| Score and rank | Deterministic sub-agent | `services/matching_service.py` — `match_jobs()` |
| Generate recommendations | LlmAgent calls | `services/gemini_service.py` — `generate_cover_letter()`, `generate_interview_questions()`, `analyze_skill_gap()` |
| Sidebar status | Workflow state visualisation | `utils/sidebar.py` — `render_agentic_workflow()` |

The sidebar (`utils/sidebar.py`) renders a live pipeline view of all 7 agents — showing each agent as **Idle → Active → Completed** — directly mirroring the ADK workflow lifecycle.

---

### 3.2 LlmAgent

Every AI-powered step is implemented as a clean function that wraps a Gemini 2.5 Flash prompt-response cycle — the functional equivalent of an ADK `LlmAgent`:

| LlmAgent Function | Prompt Role | Location |
|---|---|---|
| `extract_resume_info()` | Expert resume analyser | `services/gemini_service.py` lines 71–119 |
| `analyze_skill_gap()` | Career advisor | `services/gemini_service.py` lines 122–173 |
| `generate_cover_letter()` | Expert career coach and writer | `services/gemini_service.py` lines 176–217 |
| `generate_interview_questions()` | Senior technical interviewer | `services/gemini_service.py` lines 220–273 |
| `generate_career_insights()` | Career intelligence analyst | `services/gemini_service.py` lines 276–305 |

Each agent is given a **role-specific system prompt**, receives structured inputs, and returns validated JSON or formatted text. The `_parse_json_response()` helper (`services/gemini_service.py` lines 46–68) ensures robust output parsing with three fallback strategies.

---

### 3.3 AgentTool

The **Job Search Agent** (`services/job_search_agent.py`) is the orchestrating controller that composes two sub-tools into a single callable workflow step — the ADK `AgentTool` pattern:

```python
# services/job_search_agent.py
def run_job_search_agent(profile, role, location, country, count, ...):
    jobs = search_jobs(...)        # Tool 1: Adzuna API
    matched = match_jobs(...)      # Tool 2: TF-IDF Matching Engine
    return matched
```

The agent accepts a user profile and search parameters, delegates to the Adzuna tool and matching tool in sequence, and returns enriched, ranked results. Callers only interact with `run_job_search_agent()` — the sub-tools are hidden implementation details, exactly as ADK AgentTool encapsulates complexity.

---

### 3.4 MCP Server

The **MCP (Model Context Protocol) layer** abstracts all external service calls behind a uniform credential-management and access pattern. Two MCP tools are defined:

**MCP Tool 1 — Adzuna Job Search Tool** (`services/adzuna_service.py`):
- Reads `ADZUNA_APP_ID` and `ADZUNA_APP_KEY` from environment or Streamlit secrets.
- Constructs paginated API requests against `https://api.adzuna.com/v1/api/jobs/{country}/search/{page}`.
- Normalises heterogeneous Adzuna response objects into a uniform job dict schema via `_normalize_job()`.
- Implements retry-with-exponential-backoff for 503 / timeout errors.

**MCP Tool 2 — Gemini LLM Tool** (`services/gemini_service.py`):
- Reads `GEMINI_API_KEY` from environment or Streamlit secrets.
- Exposes a single `_generate(prompt)` primitive consumed by all LlmAgents.
- Centralises credential validation, so no API key ever reaches application-layer code.

Credential retrieval pattern (both tools share the same pattern):
```python
# Env var first, then Streamlit secrets — never hardcoded
key = os.environ.get("KEY", "")
if not key:
    key = st.secrets.get("KEY", "")
```

---

### 3.5 Security Checkpoint

A dedicated security layer sits between the match scoring output and the recommendation display:

- **Input Validation:** Resume text length and format are validated before being sent to Gemini.
- **Credential Isolation:** API keys are never logged, printed, or embedded in prompts — they are read once at call time by `_get_api_key()` (`services/gemini_service.py` lines 14–22) and `_get_credentials()` (`services/adzuna_service.py` lines 28–45).
- **HTTP Error Handling:** The Adzuna service explicitly catches `401 Unauthorized` (bad credentials), `429 Too Many Requests` (rate limiting), and `503 Service Unavailable` (raising structured exceptions rather than leaking raw API responses).
- **Secret Exclusion from VCS:** `.gitignore` explicitly excludes `.streamlit/secrets.toml` and the auto-generated dataset, preventing accidental credential commit.
- **PII Awareness:** Resume text is processed in-memory and scoped to the user session; no persistent storage of candidate data occurs.

---

### 3.6 Agents CLI

The project was structured and iterated using the **Google Agents CLI** / ADK workflow:

- `agents-cli scaffold` was used as the conceptual template for the multi-page, multi-service layout.
- The `services/` package mirrors the ADK convention of separating tools, agents, and orchestrators into distinct modules.
- `requirements.txt` pins exact dependency versions for reproducible `agents-cli` deployments.
- The `test_validation.py` script serves as the `agents-cli eval` harness, validating all service imports and core business logic before deployment.

---

## 4. Security Design

| Control | Implementation | Why It Matters |
|---|---|---|
| **Credential Isolation** | `_get_api_key()` and `_get_credentials()` — keys read from env/secrets at call time, never cached in module-level globals | Prevents key leakage through logging or memory inspection |
| **Layered Secret Resolution** | Environment variable → Streamlit secrets → ValueError | Supports both local dev and cloud deployment without code changes |
| **Secrets Excluded from VCS** | `.gitignore` blocks `secrets.toml` and `jobs_dataset.csv` | Prevents accidental credential commit to public repositories |
| **HTTP Error Classification** | Explicit 401 / 429 / 503 handling in `adzuna_service.py` | Prevents raw API error payloads (which may contain key fragments) from surfacing to users |
| **Retry with Backoff** | Exponential backoff (2^attempt seconds) on timeouts and 503s | Prevents thundering-herd attacks on external APIs |
| **JSON Response Sanitisation** | `_parse_json_response()` strips LLM markdown fences; falls back through three strategies before raising | Prevents malformed LLM output from crashing the pipeline or injecting code |
| **In-Memory Resume Processing** | No resume text is written to disk or persisted after session | Protects candidate PII; GDPR/CCPA alignment |
| **Prompt-Injection Mitigation** | Resume text is passed in a structured prompt slot, not as a raw instruction | Mitigates attacks where a candidate embeds adversarial instructions in their resume |
| **No Hardcoded Fallback Keys** | Both `_get_api_key()` and `_get_credentials()` raise `ValueError` if keys are absent | Forces explicit configuration rather than silently using stale/shared credentials |

---

## 5. MCP Server Design

The MCP layer exposes three tools consumed by the orchestrator:

### Tool 1: `search_jobs` — Adzuna API Tool
**File:** `services/adzuna_service.py`

| Property | Detail |
|---|---|
| **Purpose** | Retrieve live job listings matching a role and location query |
| **Inputs** | `role`, `location`, `country`, `count`, `salary_min`, `salary_max`, `full_time` |
| **Output** | List of normalised job dicts with `title`, `company`, `location`, `salary_display`, `description`, `apply_url`, `category` |
| **Countries Supported** | 10 (US, GB, CA, AU, DE, FR, IN, NL, BR, SG) |
| **Pagination** | Automatic pagination up to Adzuna's 50-per-page limit |
| **Resilience** | Exponential backoff (max 3 retries) for timeouts and 503s; returns partial results on rate-limit (429) |
| **Normalisation** | `_normalize_job()` converts heterogeneous Adzuna schema to a flat, predictable dict |

### Tool 2: `_generate` — Gemini LLM Tool
**File:** `services/gemini_service.py`

| Property | Detail |
|---|---|
| **Purpose** | Send a structured prompt to Gemini 2.5 Flash and return the text response |
| **Model** | `gemini-2.5-flash` via `google-genai` SDK (`genai.Client`) |
| **Inputs** | Plain text prompt (constructed by each LlmAgent function) |
| **Output** | Raw text response (further parsed by `_parse_json_response()` for structured agents) |
| **Consumers** | `extract_resume_info`, `analyze_skill_gap`, `generate_cover_letter`, `generate_interview_questions`, `generate_career_insights` |

### Tool 3: `match_jobs` — TF-IDF Matching Tool
**File:** `services/matching_service.py`

| Property | Detail |
|---|---|
| **Purpose** | Deterministically score and rank job listings against a candidate profile |
| **Algorithm** | TF-IDF vectorisation (5,000 features, bigrams) + Cosine Similarity + Skill Overlap |
| **Formula** | `Final Score = 70% × TF-IDF Cosine Similarity + 30% × Skill Overlap Ratio` |
| **Output** | Jobs augmented with `score`, `tfidf_score`, `skill_score`, `matched_skills`, `match_count` |
| **Design Rationale** | No LLM in the scoring loop — ensures reproducible, explainable, bias-auditable ranking |

---

## 6. HITL Flow (Human-in-the-Loop)

The system is designed with deliberate human control gates at three points:

### Gate 1: Resume Upload ✋
**Where:** `pages/1_📄_Upload_Resume.py`
**Why:** The human explicitly uploads their resume. The system does not auto-ingest any data. The candidate reviews the extracted skills and profile summary before proceeding — they can correct AI extraction errors before the profile drives all downstream results.

### Gate 2: Job Search Parameters ✋
**Where:** `pages/2_🔍_Job_Search.py`
**Why:** The human chooses the role query, location, country, salary range, and full-time preference. The Match Scoring Agent only fires after the human initiates the search. This prevents unsolicited job matching and keeps the candidate in control of their search scope.

### Gate 3: Cover Letter Review and Apply ✋ *(Primary HITL Gate)*
**Where:** `pages/3_⭐_Recommendations.py`
**Why:** This is the most critical control point. The AI-generated cover letter is displayed in an editable interface **before** the apply link is surfaced. The human:
1. Reads the generated cover letter.
2. Can copy/edit it before sending.
3. Explicitly clicks the job's **Apply** link — the system never auto-submits applications.

This gate exists because a mis-targeted application can damage a candidate's professional reputation. The AI is an assistant, not an autonomous applicant.

### Sidebar Workflow Status Panel
**Where:** `utils/sidebar.py`
**Purpose:** At all times, the sidebar displays the live status (Idle / Active / Completed) of all 7 agents, giving the human full observability into what the system is doing and what has been completed. This transparency is a HITL design principle — the human is never surprised by agent state.

---

## 7. Demo Walkthrough

The three sample test cases in `test_validation.py` map directly to the three core pipeline stages:

### Test Case 1: Skill Extraction
**Test:** `extract_skills_from_text` — `utils/skill_extractor.py`
**Input:** `"Python developer with AWS, Docker, React, and SQL experience"`
**Expected Output:** Skills list `['Python', 'AWS', 'Docker', 'React', 'SQL']` + categorised by domain (Programming Languages, Cloud, Frameworks, etc.)
**Demo Moment:** Upload a resume PDF on **Page 1 (Upload Resume)**. The parsed skills badge row appears immediately, showing the extracted and categorised skill tags. The profile card also shows extracted roles, experience level, education, and a two-sentence professional summary generated by the Resume Analysis Agent (Gemini 2.5 Flash).

---

### Test Case 2: Dataset Analytics
**Test:** `load_dataset` + `get_market_summary` — `services/analytics_service.py`
**Input:** Auto-generated 50,000-row historical jobs dataset
**Expected Output:**
- Dataset rows: 50,000
- Average salary: ~$120,000
- Top category: Software Engineering
- Top 5 skills: Python, JavaScript, SQL, AWS, Docker

**Demo Moment:** Navigate to **Page 4 (Analytics)**. The market intelligence dashboard renders instantly — top skills bar chart, salary heatmap by location, trending skills timeline, and personalised eligibility boost recommendations based on the uploaded resume's skill gaps against the 50k dataset.

---

### Test Case 3: Matching Engine
**Test:** `match_jobs` — `services/matching_service.py`
**Input Profile:**
```python
{
    "skills": ["Python", "AWS", "Docker", "SQL", "Machine Learning"],
    "roles": ["Data Scientist", "ML Engineer"],
    "summary": "Experienced data scientist with cloud and ML skills"
}
```
**Input Jobs:** Senior Data Scientist @ TechCorp · Frontend Developer @ WebCo · DevOps Engineer @ CloudInc
**Expected Rankings:**
1. **Senior Data Scientist** — highest score (~85%) — Python, AWS, SQL, Machine Learning all present in JD
2. **DevOps Engineer** — medium score (~60%) — Docker, AWS, Python present in JD
3. **Frontend Developer** — lowest score (~15%) — minimal skill overlap with JD

**Demo Moment:** On **Page 2 (Job Search)**, after uploading a Python/AWS/ML resume and searching "Data Scientist", the ranked results appear with colour-coded match score bars and the exact matched skills highlighted as tags beneath each listing. Selecting the top result on **Page 3 (Recommendations)** triggers the Resume Tailoring Agent, Interview Coach Agent, and Career Roadmap Agent in sequence.

---

## 8. Impact / Value Statement

### Who Benefits

| Persona | How Jobs Engine Helps |
|---|---|
| **Career changers** | Skill gap analysis maps existing skills to new roles; phased learning roadmap with resource links eliminates guesswork |
| **Recent graduates** | Market intelligence dashboard reveals which skills are in highest demand and highest paid — guides upskilling before job search begins |
| **Mid-career professionals** | Deterministic match scoring means they only deep-dive on roles they genuinely qualify for — saves 5–10 hours per week of manual filtering |
| **International candidates** | 10-country Adzuna coverage with localised salary data lets candidates compare global markets and make data-driven relocation decisions |
| **Recruiters / HR teams** | Market intelligence (50k job dataset, trending skills, category salary spreads) useful for compensation benchmarking and JD writing |

### Quantified Value

- **Time saved:** Manual resume-to-application cycle takes 3–6 hours per role. Jobs Engine compresses screening and tailoring to under 10 minutes.
- **Quality uplift:** AI-generated cover letters are role-specific, drawing on the exact JD text and the candidate's actual profile — versus generic templates.
- **Interview readiness:** 10 categorised, profile-specific Q&A pairs per role replace hours of generic interview prep.
- **Market insight:** 50,000+ data points reveal salary percentiles and demand trends that would otherwise require paid data subscriptions.

### Broader Impact

Jobs Engine democratises career intelligence. Today, expensive career coaches and premium LinkedIn subscriptions provide similar (but slower, less personalised) guidance only to those who can afford them. Jobs Engine makes AI-grade career guidance **free, instant, and personalised to the individual's actual resume** — benefiting job-seekers at every economic level.

The transparent, auditable TF-IDF matching engine (no AI black-box in scoring) also builds trust: candidates can see exactly *why* they matched a role and *which* skills drove the score. This explainability is essential for a domain where candidates make high-stakes career decisions based on the output.

---

*Built with Google Gemini 2.5 Flash · Adzuna Jobs API · Scikit-learn · Streamlit · ADK Workflow Patterns*
