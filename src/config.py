# ------------------ 1.Configuration and Skill Taxonomy ------------------
# A curated skill taxonomy based on common Python job requirements and Pyladies event topics
SKILL_TAXONOMY = {
    "Web Frameworks": ["Django", "Flask", "FastAPI", "Tornado", "Sanic", "Streamlit"],
    "Data & ML": [
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "Keras",
        "XGBoost",
        "Polars",
        "Jupyter",
        "Matplotlib",
        "Seaborn",
        "Plotly",
    ],
    "AI & Agentic Systems": [  # 🌟 Added to match modern Boston topics
        "Agentic Coding",
        "AI Agents",
        "LLM",
        "LangChain",
        "RAG",
    ],
    "Cloud & DevOps": [
        "AWS",
        "Azure",
        "GCP",
        "Docker",
        "Kubernetes",
        "Terraform",
        "CI/CD",
    ],
    "Testing & QA": ["PyTest", "UnitTest", "Selenium", "Cypress", "Test Automation"],
    "Data Engineering": [
        "Airflow",
        "Luigi",
        "Kafka",
        "Spark",
        "Hadoop",
        "ETL",
        "Data Pipelines",
    ],
    "Software Engineering": [
        "OOP",
        "Design Patterns",
        "Clean Code",
        "Code Reviews",
    ],
    "Scripting & Automation": ["Bash", "PowerShell", "Ansible", "Fabric", "Invoke"],
    "Version Control": ["Git", "GitHub", "GitLab", "Bitbucket"],
    "Databases": ["SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"],
    "APIs & Microservices": ["REST", "GraphQL", "gRPC", "OpenAPI", "Swagger"],
    "Tools & R Ecosystem": [  # 🌟 Added to catch Event #4 from Boston
        "R",
        "Positron",
        "Posit",
    ],
    "Other": [
        "Python",
        "Functional Programming",
        "Asyncio",
        "Multithreading",
        "Multiprocessing",
        "Regular Expressions",
        "Logging",
        "Debugging",
        "Performance Optimization",
    ],
}


ALL_SKILLS = [skill for sublist in SKILL_TAXONOMY.values() for skill in sublist]

# ------------------ 1.b Default Chapter Configuration ------------------
PERSISTED_CHAPTERS_FILE = ".pyladies_chapters.json"
