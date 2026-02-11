# 🚀 RAG-Powered Resume Builder

An AI-powered resume builder application that uses Google Gemini and RAG (Retrieval-Augmented Generation) to create ATS-friendly resumes.

## ✨ Features

- **AI Skill Suggestions**: Get intelligent skill recommendations based on job roles
- **Resume Builder**: Create professional resumes from scratch
- **ATS Checker**: Analyze resume compatibility with Applicant Tracking Systems
- **Quick Optimize**: Optimize existing resumes for specific job descriptions
- **Email Integration**: Send resumes directly via email
- **PDF Generation**: Export resumes as professional PDF documents

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: Google Gemini (via LangChain)
- **Backend**: Python, Pydantic
- **PDF Generation**: FPDF2
- **Email**: SMTP (Gmail)

## 📋 Prerequisites

- Python 3.8+
- Google API Key (for Gemini)
- Gmail account (for email functionality)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chatbot.git
cd chatbot
```

2. Create a virtual environment:
```bash
python -m venv myenv
myenv\Scripts\activate  # Windows
# source myenv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_api_key_here
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here
```

**Note**: For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833) instead of your regular password.

## 🎯 Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Choose from three main features:
   - **Build Resume**: Create a new resume from scratch
   - **ATS Checker**: Analyze your existing resume
   - **Quick Optimize**: Optimize resume for specific job descriptions

## 📁 Project Structure

```
chatbot/
├── backend/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── knowledge_base.py   # Skills database and ATS keywords
│   ├── main.py            # Core resume generation logic
│   └── rag.py             # RAG service implementation
├── app.py                 # Streamlit frontend
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔑 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `SENDER_EMAIL` | Gmail address for sending emails | Yes |
| `SENDER_PASSWORD` | Gmail app password | Yes |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## ⚠️ Important Notes

- Never commit your `.env` file to GitHub
- Use App Passwords for Gmail, not your regular password
- Keep your API keys secure
- The `.gitignore` file is configured to exclude sensitive files

## 🐛 Troubleshooting

**Issue**: "No GOOGLE_API_KEY found"
- Solution: Ensure your `.env` file exists and contains a valid `GOOGLE_API_KEY`

**Issue**: Email sending fails
- Solution: Enable 2-factor authentication on Gmail and generate an App Password

**Issue**: Module import errors
- Solution: Ensure all dependencies are installed: `pip install -r requirements.txt`

## 📧 Contact

For questions or support, please open an issue on GitHub.
