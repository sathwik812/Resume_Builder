import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from fpdf import FPDF
from pydantic import ValidationError

try:
    from backend.main import ResumeData, generate_resume
    from backend.config import settings
except ImportError:
    from backend.main import ResumeData, generate_resume
    from backend.config import settings


def create_pdf_safe(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=10)
    
    # Define effective width to avoid margin calculation errors
    effective_page_width = pdf.w - 2 * pdf.l_margin

    for line_num, line in enumerate(text.split("\n"), 1):
        try:
            if not line.strip():
                pdf.ln(5)
                continue
            
            # CRITICAL FIX: Always reset X to the left margin for a new block
            pdf.set_x(pdf.l_margin) 
            
            safe = line.encode('latin-1', 'replace').decode('latin-1')
            
            # Use multi_cell with a fixed width instead of 0 to prevent crashes
            pdf.multi_cell(effective_page_width, 5, safe)
            
        except Exception as e:
            return None, line_num, f"{str(e)}: {line[:50]}"
            
    return  bytes(pdf.output()), None, None


st.set_page_config(page_title="AI Resume Builder", layout="centered", page_icon="📄")
st.title("📄 AI Resume Builder")

if 'resume_pdf' not in st.session_state:
    st.session_state.resume_pdf = None

option = st.radio("Type:", ["📝 Standard", "🎯 JD-Optimized"], horizontal=True)
jd = st.text_area("📋 Job Description", height=100) if "JD" in option else None

st.subheader("Personal Information")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name*")
    email = st.text_input("Email*")
with col2:
    phone = st.text_input("Phone*")

summary = st.text_area("Summary*", height=80)
skills = st.text_area("Skills*", height=60)

st.subheader("Experience")
exp_count = st.number_input("Number of experiences", 0, 5, 1)
experiences, exp_errors = [], []

for i in range(exp_count):
    with st.expander(f"Experience {i+1}", expanded=(i==0)):
        col1, col2 = st.columns(2)
        with col1:
            company = st.text_input("Company", key=f"co_{i}")
            role = st.text_input("Role", key=f"role_{i}")
        with col2:
            duration = st.text_input("Duration", key=f"dur_{i}")
        details = st.text_area("Details", key=f"det_{i}", height=60)
        
        if any([company, role, duration, details]):
            missing = []
            if not company: missing.append("Company")
            if not role: missing.append("Role")
            if not duration: missing.append("Duration")
            
            if missing:
                st.error(f"🔴 Experience {i+1}: Missing {', '.join(missing)}")
                exp_errors.append(i+1)
            else:
                if details:
                    long_lines = [j+1 for j, ln in enumerate(details.split('\n')) if len(ln) > 1000]
                    if long_lines:
                        st.warning(f"⚠️ Experience {i+1}: Lines {long_lines} too long (>1000 chars)")
                experiences.append(f"{role} at {company} ({duration})\n{details}")

st.subheader("Education")
edu_count = st.number_input("Number of education entries", 0, 5, 1)
educations, edu_errors = [], []

for i in range(edu_count):
    with st.expander(f"Education {i+1}", expanded=(i==0)):
        col1, col2 = st.columns(2)
        with col1:
            degree = st.text_input("Degree", key=f"deg_{i}")
            institution = st.text_input("Institution", key=f"inst_{i}")
        with col2:
            year = st.text_input("Year", key=f"yr_{i}")
        
        if any([degree, institution, year]):
            missing = []
            if not degree: missing.append("Degree")
            if not institution: missing.append("Institution")
            if not year: missing.append("Year")
            
            if missing:
                st.error(f"🔴 Education {i+1}: Missing {', '.join(missing)}")
                edu_errors.append(i+1)
            else:
                if len(degree) > 1000:
                    st.warning(f"⚠️ Education {i+1}, Degree: {len(degree)} chars. Keep under 1000")
                if len(institution) > 1000:
                    st.warning(f"⚠️ Education {i+1}, Institution: {len(institution)} chars. Keep under 1000")
                educations.append(f"{degree} - {institution} ({year})")

if st.button("🚀 Generate Resume", type="primary", use_container_width=True):
    if not all([name, email, phone, summary, skills]):
        st.error("❌ Fill all required fields marked with *")
    elif exp_errors or edu_errors:
        st.error(f"❌ Fix errors in: Experience {exp_errors}, Education {edu_errors}")
    else:
        try:
            data = ResumeData(name=name, email=email, phone=phone, summary=summary, 
                            skills=skills, experience="\n\n".join(experiences) if experiences else "No experience",
                            education="\n".join(educations) if educations else "No education")
            
            with st.spinner("Generating..."):
                resume_text = generate_resume(data, jd=jd)
                print(resume_text)
                pdf_output, error_line, error_text = create_pdf_safe(resume_text)
                print(f"PDF Output: {pdf_output}, Error Line: {error_line}, Error Text: {error_text}")

                
                if pdf_output:
                    st.session_state.resume_pdf = pdf_output
                    st.session_state.resume_name = f"{name.replace(' ', '_')}_resume.pdf"
                    st.success("✅ Resume generated!")
                    st.download_button("📥 Download PDF", pdf_output, file_name=st.session_state.resume_name,
                                     mime="application/pdf", use_container_width=True)
                    with st.expander("👁️ Preview"):
                        st.text(resume_text)
                else:
                    st.error(f"🔴 PDF Error at Line {error_line}: {error_text[:60] if error_text else 'Unknown'}...")
                    if error_text and "EXPERIENCE" in resume_text[:resume_text.find(error_text)]:
                        st.warning("⚠️ Issue is in **Experience Section**")
                    elif error_text and "EDUCATION" in resume_text[:resume_text.find(error_text)]:
                        st.warning("⚠️ Issue is in **Education Section**")
                    st.info("💡 Fix: Break this line into multiple shorter lines (under 1000 characters)")
                    
        except ValidationError as ve:
            for error in ve.errors():
                st.error(f"❌ {error['loc'][0]}: {error['msg']}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

if st.session_state.resume_pdf:
    st.divider()
    st.subheader("📧 Email Resume")
    recipient = st.text_input("Recipient Email")
    
    if st.button("📨 Send Email", use_container_width=True):
        if not recipient:
            st.error("❌ Enter email")
        elif not settings.SENDER_EMAIL or not settings.SENDER_PASSWORD:
            st.error("❌ Add SENDER_EMAIL & SENDER_PASSWORD to .env")
        else:
            try:
                msg = MIMEMultipart()
                msg['From'] = settings.SENDER_EMAIL
                msg['To'] = recipient
                msg['Subject'] = f"Resume - {name}"
                msg.attach(MIMEText(f"Resume for {name}", 'plain'))
                
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(st.session_state.resume_pdf)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={st.session_state.resume_name}')
                msg.attach(part)
                
                server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
                server.starttls()
                server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
                server.send_message(msg)
                server.quit()
                st.success(f"✅ Sent to {recipient}!")
            except Exception as e:
                st.error(f"❌ {str(e)}")
