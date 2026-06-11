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
        "Flask",
        "Django",
        "FastAPI",
        "OOP",
        "Design Patterns",
        "Clean Code",
        "Code Reviews",
    ],
    "Scripting & Automation": ["Bash", "PowerShell", "Ansible", "Fabric", "Invoke"],
    "Version Control": ["Git", "GitHub", "GitLab", "Bitbucket"],
    "Databases": ["SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite"],
    "APIs & Microservices": ["REST", "GraphQL", "gRPC", "OpenAPI", "Swagger"],
    "Other": [
        "Python",
        "OOP",
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
