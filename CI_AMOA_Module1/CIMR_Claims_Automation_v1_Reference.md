# CIMR Claims Automation v1 - Project Reference

## 🎯 Project Overview

The AI Claims Processing Module for CIMR (Caisse Interprofessionnelle Marocaine de Retraite) is an intelligent automated system designed to digitize and streamline the complete claims management workflow. The system features a member-facing portal for claim submission and an internal agent dashboard for claim management, both built with Streamlit.

### 🎯 Specific CIMR Objectives
- **Reduce processing delays** (up to -70% for simple claims)
- **Improve member satisfaction** (automatic responses + proactive follow-up)
- **Optimize traceability and compliance** with ACAPS-required processes
- **Enhance internal efficiency** (fewer human errors, centralized ticket management)

### 🔗 Integrations
This module integrates with:
- **Streamlit UI**: Professional member portal and agent dashboard
- **Airtable**: Lightweight CRM and database for claims management
- **Azure OpenAI**: AI-powered classification, prioritization, and response generation
- Internal CIMR systems (pension files, contributions, affiliations)

## 🏗️ 1. Overall Architecture (V1)

| Layer | Components | Tools / Tech | Notes |
|-------|------------|--------------|-------|
| **Frontend (UI)** | Web form + Agent Dashboard | Streamlit or lightweight React app | Simple UI for members + internal agents |
| **Backend (Core API)** | FastAPI (Python) | FastAPI | Handles claim submission, routing, status updates |
| **Agentic Layer** | AI agents orchestrated via Agno | Agno Framework | Manages flows: intake → classification → resolution |
| **Data Layer** | Airtable | Airtable REST API | Acts as lightweight CRM + ticket DB |
| **NLP & LLM Layer** | Azure OpenAI / OpenAI API | GPT-4o-mini or GPT-4-turbo | Used for NLP classification & response drafting |
| **Integrations** | Future channels | WhatsApp / Email (v2+) | Planned for future expansion |

## 🧩 2. Functional Module Architecture

| Sub-module | Description | AI Agents Involved |
|------------|-------------|-------------------|
| **1. Collection & Classification** | Automatic reception of claims and categorization based on content and channel | InputParserAgent, NLPClassifierAgent |
| **2. Analysis & Prioritization** | Analysis of type, urgency, and severity of the claim | PriorityScoringAgent, ComplianceCheckerBot |
| **3. Resolution & Tracking** | Response generation, corrective actions and real-time tracking | ResolutionGeneratorAgent, CaseManagerAgent |

## 🔄 3. Detailed Workflow by Sub-module

### 🟦 1. Collection & Classification

#### 1️⃣ Collect Claim
- **Agent**: `InputParserAgent`
- **Role**: Parse and extract structured data from claim submissions (web, email, portal)
- **Input**: User message, attachment (PDF/photo), member ID, input channel
- **Output**: Structured claim data (member name, CIN, message, channel), automatic ticket creation, timestamp, CRM link, instant acknowledgment

#### 2️⃣ Classify Claim
- **Agent**: `NLPClassifierAgent`
- **Role**: Identify claim category through natural language processing (NLP)
- **Input**: Free text from member ("my pension was not paid", "RIB change not taken into account")
- **Output**: Claim type (payment, affiliation, contribution, death, technical), probability (%), associated tag
- **Multilingual**: French, Arabic, English, Amazigh

### 🟩 2. Analysis & Prioritization

#### 3️⃣ Prioritize
- **Agent**: `PriorityScoringAgent`
- **Role**: Evaluate claim urgency and determine priority response time
- **Input**: Claim type, file age, member profile, urgency mentions ("urgent", "not paid for 2 months")
- **Output**: Priority score (1–5), recommended deadline (24h, 48h, 5 days), alert if critical claim

#### 4️⃣ Compliance Check
- **Agent**: `ComplianceCheckerBot`
- **Role**: Verify compliance of processing times and procedures with ACAPS requirements and internal CIMR standards
- **Input**: Processing time, file status, internal SLA, regulatory indicators
- **Output**: Compliance report, SLA breach alert, automatic corrective recommendation

### 🟨 3. Resolution & Tracking

#### 5️⃣ Resolution Draft
- **Agent**: `ResolutionGeneratorAgent`
- **Role**: Propose or automatically generate personalized responses based on claim type
- **Input**: File type, member information, claim history, validated response base
- **Output**: Ready-to-send response text, suggested internal actions (e.g. "verify payment", "contact financial department")

#### 6️⃣ Case Tracking
- **Agent**: `CaseManagerAgent`
- **Role**: Track claim evolution until closure and notify members
- **Input**: Ticket ID, processing status, assigned user, previous interactions
- **Output**: Updated status ("In progress", "Resolved", "Escalated"), sent notifications, closure report

## 📊 4. Key Module Features

✅ **Member Portal**: Streamlit-based interface for claim submission with multilingual support  
✅ **Agent Dashboard**: Real-time dashboard for internal agents with filtering and statistics  
✅ **Automatic processing** of attachments and supporting documents  
✅ **Multilingual NLP classification** (French, Arabic, English)  
✅ **Intelligent urgency scoring system** (1-5 priority levels)  
✅ **Automated response generation** with personalized drafts  
✅ **Complete data persistence** to Airtable (18 fields managed by AI)  
✅ **Web channel** fully functional (v1 scope)  

## 📈 5. Concrete Benefits for CIMR

| Objective | Impact |
|----------|--------|
| **Reduction in processing delays** | Up to -70% for simple claims |
| **Improved member satisfaction** | Automatic responses + proactive follow-up |
| **Enhanced compliance** | Systematic respect of ACAPS deadlines |
| **Increased internal efficiency** | Fewer human errors, centralized ticket management |
| **Strategic management** | Real-time performance and quality indicators |

## 🗃️ 6. Airtable Schema

| Field | Type | Description | Agent Populated |
|-------|------|-------------|----------------|
| **Ticket ID** | Auto number | Unique claim identifier | System |
| **Member Name** | Text | From submission | InputParserAgent |
| **CIN / Adhérent ID** | Text | From form or CRM | InputParserAgent |
| **Channel** | Single select | Web (v1 scope) | InputParserAgent |
| **Message** | Long text | Original claim | InputParserAgent |
| **Attachment URL** | URL | Uploaded file link | InputParserAgent |
| **Category** | Single select | Payment / Affiliation / Contribution / Death / Technical | NLPClassifierAgent |
| **Confidence** | Number | AI classification confidence (0.0-1.0) | NLPClassifierAgent |
| **Priority** | Number | 1–5 urgency score | PriorityScoringAgent |
| **SLA Hours** | Number | SLA deadline in hours | PriorityScoringAgent |
| **Requires Escalation** | Checkbox | Critical case flag | PriorityScoringAgent |
| **Compliance Status** | Single select | Green / Yellow / Red | ComplianceCheckerBot |
| **Compliance Score** | Number | Compliance score (0.0-1.0) | ComplianceCheckerBot |
| **Time to SLA Deadline** | Number | Hours remaining to deadline | ComplianceCheckerBot |
| **DraftResponse** | Long text | AI-generated professional response | ResolutionGeneratorAgent |
| **Response Quality Score** | Number | Response quality (0.0-1.0) | ResolutionGeneratorAgent |
| **Response Language** | Single select | French / Arabic / English | ResolutionGeneratorAgent |
| **Estimated Resolution Time** | Text | Expected resolution timeframe | ResolutionGeneratorAgent |
| **Status** | Single select | New / In progress / Resolved | CaseManagerAgent |
| **Case Status** | Single select | New / In progress / Resolved / Escalated | CaseManagerAgent |
| **Requires Attention** | Checkbox | Needs immediate attention | CaseManagerAgent |
| **Assigned Agent** | Text | Internal agent assignment | CaseManagerAgent |
| **Created At** | Timestamp | Creation timestamp | System |
| **Last Updated** | Timestamp | Last modification timestamp | System |

## 🤖 7. Agno Agent Orchestration

Complete 7-step workflow with structured outputs and data persistence.

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **InputParserAgent** | Parse unstructured input into structured data | Natural language claim text | Structured claim data (member, CIN, message) |
| **NLPClassifierAgent** | Multilingual NLP classification of claims | Claim message text | Category, confidence score, reasoning |
| **PriorityScoringAgent** | Evaluate urgency and response time | Category, message, context | Priority score (1–5), SLA hours, escalation flag |
| **ComplianceCheckerBot** | Verify ACAPS and CIMR standards compliance | Priority, SLA, timestamps | Compliance status, score, time remaining |
| **ResolutionGeneratorAgent** | Generate personalized responses | Member info, category, priority | Professional response, quality score, language |
| **CaseManagerAgent** | Track and close claims | Complete claim data | Status updates, attention flags, agent assignment |

### **Workflow Steps:**
1. **Parse Input** → Extract structured data from natural language
2. **Create Claim** → Create Airtable record
3. **Classify** → AI-powered category assignment
4. **Prioritize** → Urgency scoring and SLA assignment
5. **Compliance Check** → ACAPS compliance monitoring
6. **Generate Response** → Professional multilingual response
7. **Case Management** → Status tracking and assignment

## 🎨 8. UI/UX Recommendations

### A. Member Portal (Streamlit)
- **Form fields**: Name, CIN/Member ID, detailed claim description
- **Clean minimalist design**: Professional French interface
- **Form persistence**: Data remains visible after submission
- **Success confirmation**: Ticket ID displayed with next steps
- On submit, triggers complete 7-step AI workflow

### B. Agent Dashboard (Streamlit)
- **Statistics panel**: Total claims, requires attention, in progress, resolved
- **Advanced filters**: Status dropdown, date range selection
- **Interactive table**: Sortable by date, color-coded priority badges
- **Detailed claim view**: All 18 AI-managed fields visible
- **Real-time updates**: Data sorted by date (most recent first)
- **Professional styling**: Clean, minimalist, all-French interface

## 🔌 9. API Endpoints (Python / FastAPI)

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/claims/` | Submit new claim (triggers complete 7-step workflow) |
| `GET` | `/api/claims/{id}` | Get specific claim details |
| `GET` | `/api/claims/` | List claims with optional filtering |
| `POST` | `/api/classify/{id}` | Classify a claim (Calls NLPClassifierAgent) |
| `POST` | `/api/score/{id}` | Score priority (Calls PriorityScoringAgent) |
| `POST` | `/api/compliance/{id}` | Check ACAPS compliance (Calls ComplianceCheckerBot) |
| `POST` | `/api/generate_draft/{id}` | Generate resolution (Calls ResolutionGeneratorAgent) |
| `PUT` | `/api/status/{id}` | Update claim status (Calls CaseManagerAgent) |
| `GET` | `/api/status/stats/summary` | Get status summary and statistics |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/test-airtable` | Test Airtable connection |

## ✅ 10. Success Criteria for V1

- **End-to-end flow** from form → classification → resolution draft → status update
- **Airtable acts as the single source of truth** with 100% data persistence
- **Minimal manual intervention** - fully automated workflow
- **Modular agents** (6 agents + workflow orchestration) ready for v2 expansion
- **100% field coverage** - All 18 data fields populated by AI agents
- **Production ready** - Clean, optimized, documented codebase

## 🛠️ 11. Technical Implementation Plan

### Phase 1: Core Infrastructure
1. Set up FastAPI backend with all endpoints
2. Configure Airtable integration with full CRUD operations
3. Set up Agno framework with complete agent structure
4. Create comprehensive API documentation

### Phase 2: AI Agents Development
1. Implement `InputParserAgent` for structured input parsing
2. Develop `NLPClassifierAgent` with Azure OpenAI integration
3. Build `PriorityScoringAgent` with intelligent scoring logic
4. Create `ComplianceCheckerBot` for ACAPS compliance monitoring
5. Implement `ResolutionGeneratorAgent` with multilingual response generation
6. Build `CaseManagerAgent` for complete case lifecycle management

### Phase 3: Integration & Testing
1. Connect all agents in Agno workflow (7-step process)
2. Test end-to-end claim processing with 100% success rate
3. Implement comprehensive error handling and logging
4. Add structured outputs and data persistence

### Phase 4: Production Readiness
1. Clean and optimize codebase
2. Remove unnecessary files and functions
3. Create comprehensive test suite
4. Complete documentation and project status

## 📋 12. Dependencies & Requirements

### Python Packages
```
fastapi>=0.100.0
uvicorn[standard]>=0.24.0
agno>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
openai>=1.3.7
airtable-python-wrapper>=0.15.3
requests>=2.31.0
pandas>=2.0.0
numpy>=1.21.0
python-multipart>=0.0.6
aiofiles>=23.2.1
httpx>=0.25.2
pytest>=7.4.3
pytest-asyncio>=0.21.1
loguru>=0.7.2
```

### External Services
- Airtable account with API key
- Azure OpenAI API key and configuration
- Environment configuration (.env template)

## 🔧 13. Environment Configuration

```env
# Application Settings
APP_NAME=CIMR Claims Automation v1
APP_VERSION=1.0.0
DEBUG=true
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=INFO

# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id
AIRTABLE_TABLE_NAME=claims

# Azure OpenAI Configuration
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

**Note**: Web channel only for v1. WhatsApp/Email integrations planned for v2+.

## 📊 14. Monitoring & Analytics (Future v2)

- Claim processing metrics
- Agent performance analytics
- Response time tracking
- Customer satisfaction scores
- Category distribution analysis

## 🚀 15. Deployment Considerations

- Docker containerization for easy deployment
- Environment-specific configuration
- Database backup strategies
- API rate limiting
- Security best practices (API key management)

---

## 📝 Notes

This reference document serves as the complete technical specification for CIMR Claims Automation v1. All components are designed to be modular and scalable for future enhancements.

**Last Updated**: October 26, 2025  
**Version**: 1.0.0  
**Status**: Production Ready
