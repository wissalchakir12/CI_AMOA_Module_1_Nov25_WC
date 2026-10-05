# CIMR Claims Automation v1

AI-powered claims processing system for CIMR (Caisse Interprofessionnelle Marocaine de Retraite).

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp env.template .env

# Edit .env with your credentials
# - AIRTABLE_API_KEY
# - AIRTABLE_BASE_ID
# - OPENAI_API_KEY
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python run.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs (development only)

## 📁 Project Structure

```
src/
├── config/          # Configuration settings
├── api/             # FastAPI backend with all routes
├── agents/          # AI agents (6 agents + workflow)
├── utils/           # Utility functions (Airtable client)
└── test_structured_outputs.py  # Complete workflow test
```

## 🔧 Environment Variables

See `env.template` for all required environment variables.

## 📊 Airtable Setup

Create a table called "claims" with these fields:
- Ticket ID (Auto number)
- Member Name (Single line text)
- CIN / Adhérent ID (Single line text)
- Channel (Single select: Web) - *Web only for v1*
- Message (Long text)
- Attachment URL (URL)
- Category (Single select: Payment, Affiliation, Contribution, Death, Technical)
- Confidence (Number, decimal 0-1)
- Priority (Number, integer 1-5)
- Status (Single select: New, In progress, Resolved)
- Assigned Agent (Collaborator)
- DraftResponse (Long text)
- Created At (Created time)
- Last Updated (Last modified time)

## 🧪 Testing

```bash
# Test complete workflow
python test_structured_outputs.py

# Test Airtable connection
curl http://localhost:8000/test-airtable

# Health check
curl http://localhost:8000/health
```

## 📝 Development Status

### ✅ COMPLETED - CIMR Claims Automation v1
- ✅ **Complete AI Workflow**: All 7 agents working with structured outputs
- ✅ **100% Data Persistence**: All agent outputs saved to Airtable
- ✅ **End-to-End Automation**: From claim intake to resolution draft
- ✅ **Production Ready**: Clean, optimized codebase
- ✅ **Web Channel**: Fully functional web-based claims processing

### 🚀 Ready for Production
The system is now fully operational and ready for deployment!

## 🎯 V1 Scope

**Current Version (v1) includes:**
- ✅ Web-based claim submission
- ✅ AI-powered classification and prioritization
- ✅ Automated response generation
- ✅ Internal agent dashboard

**Future versions will add:**
- WhatsApp integration
- Email notifications
- SMS alerts
- Advanced analytics
