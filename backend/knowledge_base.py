
SKILLS_DB = {
    "software": "Python, Java, JavaScript, React, Node.js, AWS, Docker, Kubernetes, Git, CI/CD, REST APIs, Microservices, SQL, MongoDB, Agile, Scrum",
    "data": "Python, SQL, Pandas, NumPy, Machine Learning, TensorFlow, PyTorch, Data Visualization, Tableau, Power BI, ETL, Big Data, Spark, Statistics",
    "devops": "AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Terraform, Ansible, CI/CD, Linux, Bash, Monitoring, Prometheus, Grafana",
    "llmops": "LLM, MLOps, Model Deployment, Vector Databases, RAG, Prompt Engineering, LangChain, Fine-tuning, Model Monitoring, AI Infrastructure",
    "frontend": "React, Angular, Vue.js, JavaScript, TypeScript, HTML5, CSS3, Responsive Design, Redux, Webpack, Jest, UI/UX",
    "backend": "Node.js, Python, Java, Spring Boot, Django, Flask, REST APIs, GraphQL, Microservices, PostgreSQL, Redis, RabbitMQ",
    "mobile": "React Native, Flutter, Swift, Kotlin, iOS, Android, Mobile UI/UX, Firebase, Push Notifications, App Store Optimization",
    "finance": "Financial Analysis, Excel, Bloomberg, Risk Management, Portfolio Management, Financial Modeling, Accounting, GAAP, Compliance",
    "marketing": "SEO, SEM, Google Analytics, Content Marketing, Social Media, Email Marketing, A/B Testing, CRM, Marketing Automation"
}

ATS_KEYWORDS = """
Leadership: Led, Managed, Directed, Coordinated, Supervised, Mentored, Guided
Achievement: Achieved, Delivered, Exceeded, Improved, Increased, Reduced, Optimized, Streamlined
Technical: Developed, Implemented, Designed, Built, Architected, Engineered, Deployed, Integrated
Analysis: Analyzed, Evaluated, Assessed, Investigated, Researched, Identified, Diagnosed
Collaboration: Collaborated, Partnered, Coordinated, Facilitated, Communicated, Presented
"""

PROFESSIONAL_PHRASES = """
Spearheaded cross-functional initiatives resulting in measurable business impact
Architected scalable solutions handling millions of transactions daily
Drove operational excellence through process optimization and automation
Collaborated with stakeholders to align technical solutions with business objectives
Mentored junior team members fostering a culture of continuous learning
Implemented best practices improving code quality and reducing technical debt
"""

def get_knowledge_text():
    """Combine all knowledge into searchable text"""
    skills_text = "\n".join([f"{domain.upper()} SKILLS: {skills}" for domain, skills in SKILLS_DB.items()])
    return f"{skills_text}\n\n{ATS_KEYWORDS}\n\n{PROFESSIONAL_PHRASES}"
