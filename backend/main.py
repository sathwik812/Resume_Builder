import os
import re
from typing import Optional, Union
from pydantic import BaseModel, field_validator, ConfigDict

# LangChain imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

class ResumeData(BaseModel):
    """Resume data model with validation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str 
    email: str 
    phone: str
    summary: str 
    skills: str
    experience: str
    education: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError('Name is required')
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not re.match(r'^[a-zA-Z\s\'-]+$', v):
            raise ValueError('Name should only contain letters, spaces, hyphens, and apostrophes')
        return v
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v or '@' not in v:
            raise ValueError('Email must contain @')
        parts = v.split('@')
        if len(parts) != 2 or '.' not in parts[1]:
            raise ValueError('Invalid email format')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) != 10:
            raise ValueError('Phone must have exactly 10 digits')
        return v
    
    @field_validator('summary')
    @classmethod
    def validate_summary(cls, v: str) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError('Summary is required')
        if len(v) < 20:
            raise ValueError('Summary must be at least 20 characters')
        return v
    
    @field_validator('skills')
    @classmethod
    def validate_skills(cls, v: str) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError('Skills are required')
        if len(v) < 10:
            raise ValueError('Please provide more detailed skills')
        return v
    
    @field_validator('experience')
    @classmethod
    def validate_experience(cls, v: str) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError('Experience is required')
        if len(v) < 20:
            raise ValueError('Experience must be at least 20 characters')
        return v
    
    @field_validator('education')
    @classmethod
    def validate_education(cls, v: str, info) -> str:
        if not isinstance(v, str):
            v = str(v)
        v = v.strip()
        if not v:
            raise ValueError('Education is required')
        if len(v) < 10:
            raise ValueError('Education must be at least 10 characters')
        if 'experience' in info.data and v == info.data['experience']:
            raise ValueError('Education and Experience cannot be identical')
        if 'experience' in info.data:
            exp_lower = str(info.data['experience']).lower().strip()
            edu_lower = v.lower().strip()
            if exp_lower and edu_lower and len(exp_lower) > 20 and len(edu_lower) > 20:
                shorter = edu_lower if len(edu_lower) < len(exp_lower) else exp_lower
                longer = exp_lower if len(exp_lower) >= len(edu_lower) else edu_lower
                if shorter in longer or longer in shorter:
                    raise ValueError('Education and Experience cannot be the same content')
        return v


def get_llm():
    """Get LangChain ChatGoogleGenerativeAI instance with multiple fallback models"""
    try:
        from backend.config import settings
        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")  
        if not api_key:
            print("❌ No GOOGLE_API_KEY found")
            return None
        
        # Try multiple model names in order of preference
        models_to_try = [ 
            "gemini-2.5-flash"   # Very stable fallback
        ]
        
        for model_name in models_to_try:
            try:
                print(f"🔄 Trying model: {model_name}...")
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=api_key,
                    temperature=0.7,
                    max_tokens=2048,
                    timeout=30
                )
                
                # Test the model with a simple query
                test_response = llm.invoke([HumanMessage(content="Say OK")])
                
                # Successfully initialized and tested
                print(f"✅ Successfully initialized with model: {model_name}")
                return llm
                
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️  Model {model_name} failed: {error_msg[:100]}")
                continue
        
        # If all models fail
        print("❌ All models failed. Please check your API key.")
        return None
        
    except ImportError as e:
        print("❌ LangChain not installed. Run: pip install langchain-google-genai langchain-core")
        return None
    except Exception as e:
        print(f"❌ LLM initialization failed: {e}")
        return None


def extract_text_from_response(response: Union[AIMessage, str]) -> str:
    """Safely extract text from LangChain response"""
    try:
        # If it's already a string, return it
        if isinstance(response, str):
            return response
        
        # If it's an AIMessage object, extract content
        if hasattr(response, 'content'):
            content = response.content
            # Content might be a string or list
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # Join list items
                return '\n'.join(str(item) for item in content)
            else:
                return str(content)
        
        # Fallback: convert to string
        return str(response)
    except Exception as e:
        print(f"⚠️  Error extracting text: {e}")
        return ""


def get_skill_suggestions(query: str) -> dict:
    """Get accurate skill suggestions from LLM using LangChain"""
    llm = get_llm()
    if not llm:
        return {
            "skills": [], 
            "text": "LLM not configured. Please set GOOGLE_API_KEY in .env file", 
            "formatted": ""
        }
    
    prompt = f"""You are a professional career advisor. Based on the query: "{query}"

Generate a comprehensive list of relevant technical and professional skills.

Requirements:
- List 8-10 highly relevant skills
- Include both technical skills and soft skills where applicable
- Be specific and industry-relevant
- Format each skill on a new line
- No bullet points, just skill names
- One skill per line
         
Example format:
Python
Data Analysis
Machine Learning
SQL
Problem Solving"""
    
    try:
        # LangChain invoke method
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Safely extract text
        skills_text = extract_text_from_response(response)
        
        if not skills_text:
            return {"skills": [], "text": "Failed to get response", "formatted": ""}
        
        skills_text = skills_text.strip()
        
        # Parse skills into a list (one per line)
        skills_list = [skill.strip() for skill in skills_text.split('\n') if skill.strip()]
        # Remove any bullet points or numbering
        skills_list = [re.sub(r'^[\d\.\-\*\•]+\s*', '', skill) for skill in skills_list]
        
        return {
            "skills": skills_list,
            "text": skills_text,
            "formatted": ", ".join(skills_list)
        }
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Skill suggestion error: {error_msg}")
        return {"skills": [], "text": f"Error: {error_msg}", "formatted": ""}


def generate_resume(data: ResumeData, jd: Optional[str] = None) -> str:
    """Generate resume text from data using LangChain + Gemini with RAG"""
    llm = get_llm()
    
    rag_context = ""
    if jd:
        try:
            from backend.rag import rag_service
            relevant_skills = rag_service.get_relevant_skills(jd)
            if relevant_skills:
                rag_context = f"\n\nRelevant Skills/Keywords to emphasize:\n{relevant_skills}"
        except Exception as e:
            print(f"⚠️  RAG service error: {e}")
            pass
    
    if llm and jd:
        prompt = f"""Create an ATS-friendly resume optimized for this job:

Job Description: {jd}{rag_context}

Candidate Info:
Name: {data.name}
Email: {data.email}
Phone: {data.phone}
Summary: {data.summary}
Skills: {data.skills}
Experience: {data.experience}
Education: {data.education}

Format professionally with clear sections. Keep contact info on separate lines. Output only the resume content."""
        
        try:
            # LangChain invoke method
            response = llm.invoke([HumanMessage(content=prompt)])
            
            # Safely extract text
            resume_text = extract_text_from_response(response)
            
            if resume_text:
                return resume_text
            else:
                print("⚠️  Empty response from LLM, using template")
                
        except Exception as e:
            print(f"❌ LLM generation failed: {e}")
    
    # Template fallback - contact info on separate lines
    return f"""{data.name}


Phone: {data.phone}
Email: {data.email}

PROFESSIONAL SUMMARY
{data.summary}

SKILLS
{data.skills}

EXPERIENCE
{data.experience}

EDUCATION
{data.education}
"""