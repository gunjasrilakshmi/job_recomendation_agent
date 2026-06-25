"""
Skill Extractor Utility
Extracts technical and professional skills from text using keyword matching.
Used as a fallback and supplement to Gemini-based extraction.
"""

import re

# Comprehensive skill taxonomy organized by category
SKILL_TAXONOMY = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
        "Perl", "Haskell", "Dart", "Lua", "Shell", "Bash", "PowerShell",
        "Objective-C", "Assembly", "COBOL", "Fortran", "Julia", "Elixir",
        "Clojure", "Groovy", "Visual Basic", "VB.NET", "F#",
    ],
    "Web Frameworks": [
        "React", "Angular", "Vue.js", "Vue", "Next.js", "Nuxt.js", "Svelte",
        "Django", "Flask", "FastAPI", "Express.js", "Express", "Spring Boot",
        "Spring", "Ruby on Rails", "Rails", "Laravel", "ASP.NET", ".NET",
        "Node.js", "Deno", "Gatsby", "Remix", "Astro", "SvelteKit",
        "NestJS", "Gin", "Echo", "Fiber", "Actix",
    ],
    "Data & ML": [
        "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
        "Computer Vision", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
        "Pandas", "NumPy", "SciPy", "Matplotlib", "Seaborn", "Plotly",
        "OpenCV", "Hugging Face", "Transformers", "BERT", "GPT",
        "LLM", "Large Language Models", "RAG", "Retrieval Augmented Generation",
        "XGBoost", "LightGBM", "CatBoost", "Random Forest",
        "Neural Networks", "CNN", "RNN", "LSTM", "GAN",
        "Reinforcement Learning", "Transfer Learning", "Feature Engineering",
        "Data Mining", "Statistical Analysis", "A/B Testing",
        "Time Series", "Recommendation Systems", "MLOps",
        "Apache Spark", "PySpark", "Hadoop", "Hive", "Pig",
        "Apache Kafka", "Apache Flink", "Apache Airflow", "Airflow",
        "dbt", "Databricks", "Snowflake", "BigQuery",
        "Data Warehousing", "ETL", "Data Pipeline", "Data Engineering",
        "Power BI", "Tableau", "Looker", "Metabase", "Grafana",
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Azure", "Google Cloud", "GCP",
        "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Puppet", "Chef",
        "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "Travis CI",
        "CI/CD", "Continuous Integration", "Continuous Deployment",
        "Linux", "Unix", "Ubuntu", "CentOS", "Red Hat",
        "Nginx", "Apache", "Load Balancing", "CDN",
        "Serverless", "Lambda", "Cloud Functions", "Azure Functions",
        "EC2", "S3", "RDS", "DynamoDB", "CloudFormation",
        "ECS", "EKS", "Fargate", "CloudWatch",
        "Helm", "Istio", "Prometheus", "Grafana",
        "VMware", "Vagrant", "Packer",
        "Infrastructure as Code", "IaC", "Site Reliability Engineering", "SRE",
        "Microservices", "Service Mesh", "API Gateway",
    ],
    "Databases": [
        "SQL", "MySQL", "PostgreSQL", "SQLite", "Oracle", "SQL Server",
        "MongoDB", "Redis", "Cassandra", "Elasticsearch",
        "Neo4j", "CouchDB", "DynamoDB", "Firebase", "Firestore",
        "InfluxDB", "TimescaleDB", "CockroachDB", "MariaDB",
        "Memcached", "RabbitMQ", "ActiveMQ",
        "Database Design", "Database Administration", "NoSQL",
    ],
    "Security": [
        "Cybersecurity", "Information Security", "Network Security",
        "Penetration Testing", "Ethical Hacking", "OWASP",
        "Encryption", "SSL/TLS", "OAuth", "JWT", "SAML", "SSO",
        "Firewall", "IDS/IPS", "SIEM", "SOC",
        "Vulnerability Assessment", "Security Audit",
        "Compliance", "GDPR", "HIPAA", "SOC 2", "ISO 27001",
        "Identity Management", "IAM", "Zero Trust",
    ],
    "Mobile": [
        "iOS", "Android", "React Native", "Flutter", "Xamarin",
        "SwiftUI", "UIKit", "Jetpack Compose", "Kotlin Multiplatform",
        "Mobile Development", "App Development",
        "Expo", "Ionic", "Cordova", "Progressive Web App", "PWA",
    ],
    "Tools & Practices": [
        "Git", "GitHub", "GitLab", "Bitbucket", "SVN",
        "Jira", "Confluence", "Trello", "Asana", "Monday.com",
        "Agile", "Scrum", "Kanban", "Lean", "SAFe",
        "TDD", "BDD", "Unit Testing", "Integration Testing",
        "Selenium", "Cypress", "Jest", "Pytest", "JUnit", "Mocha",
        "REST", "REST API", "RESTful", "GraphQL", "gRPC", "WebSocket",
        "Swagger", "OpenAPI", "Postman",
        "VS Code", "IntelliJ", "Eclipse", "Vim",
        "Figma", "Sketch", "Adobe XD", "Photoshop", "Illustrator",
        "Webpack", "Vite", "Babel", "ESLint", "Prettier",
        "npm", "yarn", "pip", "Maven", "Gradle",
        "Design Patterns", "SOLID", "Clean Architecture",
        "System Design", "Distributed Systems",
        "Technical Writing", "Documentation",
    ],
    "Soft Skills": [
        "Leadership", "Team Management", "Project Management",
        "Communication", "Problem Solving", "Critical Thinking",
        "Collaboration", "Mentoring", "Coaching",
        "Stakeholder Management", "Client Relations",
        "Strategic Planning", "Decision Making",
        "Time Management", "Presentation Skills",
        "Cross-functional", "Remote Work",
    ],
}

# Flatten all skills into a lookup set (lowercased)
ALL_SKILLS = {}
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        ALL_SKILLS[skill.lower()] = {"name": skill, "category": category}


def extract_skills_from_text(text: str) -> list[str]:
    """
    Extract skills from text using keyword matching against the skill taxonomy.
    
    Args:
        text: The text to extract skills from (resume or job description)
        
    Returns:
        List of matched skill names (properly cased)
    """
    if not text:
        return []
    
    text_lower = text.lower()
    found_skills = set()
    
    # Sort skills by length (longest first) to match multi-word skills before single words
    sorted_skills = sorted(ALL_SKILLS.keys(), key=len, reverse=True)
    
    for skill_lower in sorted_skills:
        skill_info = ALL_SKILLS[skill_lower]
        
        # Use word boundary matching for short skills to avoid false positives
        if len(skill_lower) <= 3:
            pattern = r'\b' + re.escape(skill_lower) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill_info["name"])
        else:
            if skill_lower in text_lower:
                found_skills.add(skill_info["name"])
    
    return sorted(found_skills)


def categorize_skills(skills: list[str]) -> dict[str, list[str]]:
    """
    Categorize a list of skills by their taxonomy category.
    
    Args:
        skills: List of skill names
        
    Returns:
        Dictionary mapping category names to lists of skills
    """
    categorized = {}
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower in ALL_SKILLS:
            category = ALL_SKILLS[skill_lower]["category"]
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(skill)
    
    return categorized


def get_skill_categories() -> list[str]:
    """Return all available skill categories."""
    return list(SKILL_TAXONOMY.keys())
