import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF


try:
    from backend.main import ResumeData, generate_resume, get_skill_suggestions
    from backend.config import settings
    from backend.rag import rag_service
except ImportError:
    from backend.main import ResumeData, generate_resume, get_skill_suggestions
    from backend.config import settings
    from backend.rag import rag_service

def create_pdf_safe(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    for line in text.split("\n"):
        if not line.strip():
            pdf.ln(5)
            continue
        pdf.set_x(pdf.l_margin)
        safe = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(effective_page_width, 5, safe)
    return bytes(pdf.output())

def send_email(recipient, pdf_data, filename, name):
    msg = MIMEMultipart()
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = recipient
    msg['Subject'] = f"Resume - {name}"
    msg.attach(MIMEText(f"Resume for {name}", 'plain'))
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(pdf_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    msg.attach(part)
    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()

st.set_page_config(page_title="📄 Resume Builder", layout="wide", page_icon="📄")

def apply_suggested_skills() -> None:
    """Copy the latest AI-suggested skills into the resume form."""
    suggestion_data = st.session_state.get("skill_suggestions_data") or {}
    formatted_skills = suggestion_data.get("formatted", "")
    if formatted_skills:
        st.session_state.f1_skills = formatted_skills
        st.session_state.skills_used = True

# Initialize session state for skills tracking
if 'skills_used' not in st.session_state:
    st.session_state.skills_used = False
if 'skill_suggestions_data' not in st.session_state:
    st.session_state.skill_suggestions_data = None
if 'last_search_query' not in st.session_state:
    st.session_state.last_search_query = ""
if 'f1_skills' not in st.session_state:
    st.session_state.f1_skills = ""

# Initialize RAG
if 'rag_initialized' not in st.session_state:
    with st.spinner("Initializing AI..."):
        st.session_state.rag_initialized = rag_service.initialize()

# Home Page with Search
st.title("🚀 RAG-Powered Resume Builder")

# Skill Search with Use Button
col_search, col_button = st.columns([4, 1])
with col_search:
    search_query = st.text_input(
        "🔍 Search skills, keywords, or get suggestions...", 
        placeholder="e.g., Python developer, Data Scientist, Frontend Engineer",
        key="search_input"
    )

# Search and display suggestions
if search_query and search_query != st.session_state.last_search_query:
st.session_state.skill_suggestions_data = get_skill_suggestions(search_query)
        st.session_state.last_search_query = search_query

if not search_query:
    st.session_state.skill_suggestions_data = None
    st.session_state.last_search_query = ""

result = st.session_state.skill_suggestions_data or {}
if search_query and result:
    if result.get("skills"):
        st.success("💡 **AI-Generated Skills:**")

        # Display skills in a nice format
        col1, col2 = st.columns([3, 1])
        with col1:
            # Display skills as tags
            skills_html = ""
            for skill in result["skills"]:
                skills_html += f'<span style="background-color: #e0e7ff; color: #3730a3; padding: 5px 10px; margin: 3px; border-radius: 15px; display: inline-block; font-size: 14px;">{skill}</span> '
            st.markdown(skills_html, unsafe_allow_html=True)

        with col2:
            st.button(
                "✨ Use These Skills",
                type="primary",
                use_container_width=True,
                on_click=apply_suggested_skills,
            )
    else:
        st.error(result.get("text", "Could not generate suggestions"))

st.divider()

# Feature Selection
tab1, tab2, tab3 = st.tabs(["📝 Build Resume", "🎯 ATS Checker", "⚡ Quick Optimize"])

# Feature 1: Standard Resume Builder (NO JD FIELD)
with tab1:
    st.subheader("Build Resume from Scratch")
    
    # Show success message if skills were just added
    if st.session_state.skills_used:
        st.success("✅ Skills have been auto-filled in the Skills field below! You can edit them if needed.")
        st.session_state.skills_used = False  # Reset after showing
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name*", key="f1_name", placeholder="John Doe")
        email = st.text_input("Email*", key="f1_email", placeholder="john.doe@example.com")
        phone = st.text_input("Phone* (10 digits)", key="f1_phone", placeholder="1234567890")
    with col2:
        summary = st.text_area(
            "Professional Summary*", 
            height=100, 
            key="f1_summary",
            placeholder="Brief summary of your professional background and career objectives..."
        )
    
    # Skills field - controlled by session state key only (NO value parameter)
    skills = st.text_area(
        "Skills*", 
        height=80, 
        key="f1_skills",  # This key directly controls the content
        placeholder="e.g., Python, JavaScript, React, AWS, Machine Learning, Data Analysis..."
    )
    
    experience = st.text_area(
        "Work Experience*", 
        height=120, 
        key="f1_exp", 
        placeholder="Software Engineer at ABC Company (Jan 2020 - Present)\n• Developed and maintained web applications\n• Led a team of 3 developers\n• Improved system performance by 40%"
    )
    
    education = st.text_area(
        "Education*", 
        height=80, 
        key="f1_edu", 
        placeholder="Bachelor of Science in Computer Science\nXYZ University (2016 - 2020)\nGPA: 3.8/4.0"
    )
    
    st.info("ℹ️ All fields are required. Education and Experience must be different.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Generate Resume", type="primary", use_container_width=True):
            # Validate all required fields are filled
            if not all([name, email, phone, summary, skills, experience, education]):
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    # Create ResumeData object - validation happens here
                    data = ResumeData(
                        name=name, 
                        email=email, 
                        phone=phone, 
                        summary=summary, 
                        skills=skills, 
                        experience=experience, 
                        education=education
                    )
                    
                    with st.spinner("Generating your professional resume..."):
                        resume_text = generate_resume(data, jd=None)
                        pdf_output = create_pdf_safe(resume_text)
                        st.session_state.resume_pdf = pdf_output
                        st.session_state.resume_filename = f"{name.replace(' ', '_')}_resume.pdf"
                        st.success("✅ Resume generated successfully!")
                        st.download_button(
                            "📥 Download Resume", 
                            pdf_output, 
                            file_name=st.session_state.resume_filename, 
                            mime="application/pdf",
                            use_container_width=True
                        )
                except ValueError as e:
                    st.error(f"❌ Validation Error: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with col2:
        if 'resume_pdf' in st.session_state:
            st.write("**📧 Email Your Resume**")
            recipient = st.text_input("Recipient Email:", key="f1_recipient", placeholder="recruiter@company.com")
            if st.button("📨 Send Email", use_container_width=True):
                if recipient:
                    try:
                        send_email(recipient, st.session_state.resume_pdf, st.session_state.resume_filename, name)
                        st.success(f"✅ Resume sent to {recipient}!")
                    except Exception as e:
                        st.error(f"❌ Email Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter recipient email")

# Feature 2: ATS Checker
with tab2:
    st.subheader("Check ATS Score & Get Suggestions")
    resume_text = st.text_area("Paste your resume text here", height=300, key="f2_resume")
    jd_text = st.text_area("Job Description (optional)", height=100, key="f2_jd")
    
    if st.button("🎯 Analyze ATS Score", type="primary", use_container_width=True):
        if resume_text:
            with st.spinner("Analyzing..."):
                score = rag_service.calculate_ats_score(resume_text, jd_text if jd_text else None)
                suggestions = rag_service.get_ats_suggestions(resume_text)
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("ATS Score", f"{score}/100")
                    if score >= 80:
                        st.success("Excellent!")
                    elif score >= 60:
                        st.warning("Good, can improve")
                    else:
                        st.error("Needs improvement")
                
                with col2:
                    st.write("**💡 Suggestions:**")
                    for suggestion in suggestions:
                        st.write(f"• {suggestion}")
        else:
            st.error("❌ Paste resume text")

# Feature 3: Quick Optimize (Resume + JD → PDF)
with tab3:
    st.subheader("Optimize Existing Resume with Job Description")
    existing_resume = st.text_area("Paste your existing resume", height=200, key="f3_resume")
    target_jd = st.text_area("Paste Job Description*", height=150, key="f3_jd")
    
    if st.button("⚡ Optimize & Download", type="primary", use_container_width=True):
        if existing_resume and target_jd:
            try:
                with st.spinner("Optimizing with RAG..."):
                    # Extract basic info (simplified)
                    lines = existing_resume.split('\n')
                    name = lines[0] if lines else "Candidate"
                    
                    # Get RAG-enhanced suggestions
                    relevant_context = rag_service.get_relevant_skills(target_jd)
                    
                    # Create optimized resume
                    data = ResumeData(
                        name=name, email="email@example.com", phone="1234567890",
                        summary=existing_resume[:200], skills=relevant_context[:200],
                        experience=existing_resume, education="See resume"
                    )
                    optimized_text = generate_resume(data, jd=target_jd)
                    pdf_output = create_pdf_safe(optimized_text)
                    
                    st.success("✅ Optimized!")
                    st.download_button("📥 Download Optimized Resume", pdf_output, 
                                     file_name="optimized_resume.pdf", mime="application/pdf")
                    
                    with st.expander("👁️ Preview"):
                        st.text(optimized_text[:500] + "...")
            except Exception as e:
                st.error(f"❌ {str(e)}")
        else:
            st.error("❌ Provide both resume and JD")
