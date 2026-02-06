import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from google import genai  

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
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip()
        if not v or '@' not in v:
            raise ValueError('Email must contain @')
        parts = v.split('@')
        if len(parts) != 2 or '.' not in parts[1]:
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        digits = ''.join(filter(str.isdigit, v))
        if len(digits) < 10:
            raise ValueError('Phone must have at least 10 digits')
        return v

def get_llm():
    """Get Google Gemini LLM instance or None if not configured"""
    try:
        from config import settings
        api_key = settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY")  # Changed variable name
        if not api_key:
            return None
        
        # Initialize Google Gemini client
        client = genai.Client(api_key=api_key)
        
        # Return the client and model name
        return {
            'client': client,
            'model': settings.EMBEDDING_MODEL_NAME if hasattr(settings, 'EMBEDDING_MODEL_NAME') else 'gemini-pro'
        }
    except ImportError:
        print("Google Gemini SDK not installed. Install with: pip install google-generativeai")
        return None
    except Exception as e:
        print(f"LLM initialization failed: {e}")
        return None

def generate_resume(data: ResumeData, jd: Optional[str] = None) -> str:
    """Generate resume text from data using Google Gemini"""
    llm_config = get_llm()
    
    if llm_config and jd:
        prompt = f"""Create an ATS-friendly resume optimized for this job:

Job Description: {jd}

Candidate Info:
Name: {data.name}
email: {data.email}
Phone: {data.phone}
Summary: {data.summary}
Skills: {data.skills}
Experience: {data.experience}
Education: {data.education}

Format professionally with clear sections. Keep contact info on separate lines. Output only the resume content."""
        
        try:
            client = llm_config['client']
            model = llm_config['model']
            
            # Call Gemini API
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                }
            )
            
            # Extract the text from response
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                return str(response)
                
        except Exception as e:
            print(f"LLM generation failed: {e}")
    
    # Template fallback - contact info on separate lines
    return f"""{data.name}


Phone: {data.phone}
email: {data.email}

PROFESSIONAL SUMMARY
{data.summary}

SKILLS
{data.skills}

EXPERIENCE
{data.experience}

EDUCATION
{data.education}
"""