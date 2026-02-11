from typing import List, Optional
from backend.knowledge_base import get_knowledge_text, SKILLS_DB, ATS_KEYWORDS

class RAGService:
    def __init__(self):
        self.knowledge = get_knowledge_text()
        self.initialized = True
        
    def initialize(self) -> bool:
        """Initialize RAG service"""
        return True
    
    def semantic_search(self, query: str, k: int = 3) -> List[str]:
        """Simple keyword-based search in knowledge base"""
        query_lower = query.lower()
        results = []
        
        # Search in skills database
        for domain, skills in SKILLS_DB.items():
            if any(word in skills.lower() for word in query_lower.split()):
                results.append(f"{domain.upper()} SKILLS: {skills}")
        
        # Search in ATS keywords
        for line in ATS_KEYWORDS.strip().split('\n'):
            if any(word in line.lower() for word in query_lower.split()):
                results.append(line.strip())
        
        return results[:k] if results else ["Try: Python, Java, DevOps, Data Science, Frontend, Backend"]
    
    def get_relevant_skills(self, jd: str) -> str:
        """Extract relevant skills from JD"""
        results = self.semantic_search(jd, k=5)
        return "\n".join(results) if results else ""
    
    def get_ats_suggestions(self, resume_text: str) -> List[str]:
        """Get ATS improvement suggestions"""
        suggestions = []
        resume_lower = resume_text.lower()
        
        action_verbs = ["led", "managed", "developed", "implemented", "achieved", "improved"]
        if not any(verb in resume_lower for verb in action_verbs):
            suggestions.append("Add strong action verbs (Led, Managed, Developed, Achieved)")
        
        if not any(char.isdigit() for char in resume_text):
            suggestions.append("Include quantifiable achievements (e.g., 'Improved performance by 40%')")
        
        if len(resume_text) < 300:
            suggestions.append("Resume is too short. Add more details about your experience")
        
        return suggestions if suggestions else ["Resume looks ATS-friendly!"]
    
    def calculate_ats_score(self, resume_text: str, jd: Optional[str] = None) -> int:
        """Calculate ATS compatibility score (0-100)"""
        score = 50
        resume_lower = resume_text.lower()
        
        action_verbs = ["led", "managed", "developed", "implemented", "achieved", "improved", "designed"]
        score += min(15, sum(3 for verb in action_verbs if verb in resume_lower))
        
        if any(char.isdigit() for char in resume_text):
            score += 15
        
        if 300 < len(resume_text) < 2000:
            score += 10
        
        if jd:
            jd_words = set(jd.lower().split())
            resume_words = set(resume_lower.split())
            match_ratio = len(jd_words & resume_words) / len(jd_words) if jd_words else 0
            score += int(match_ratio * 10)
        
        return min(100, score)

rag_service = RAGService()
