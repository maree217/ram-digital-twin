# Ram Digital Twin - Consultancy Platform

A sophisticated digital twin representing Ram Senthil-Maree's expertise in digital transformation, PMO setup, and Microsoft Dynamics 365 implementation.

## 🚀 Quick Start

### Phase 1: Local Development Setup

1. **Clone and Setup**
```bash
cd "Digital Twin 2"
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your API keys:
# - GOOGLE_API_KEY (for Gemini AI)
# - Other keys as needed
```

3. **Run the Application**
```bash
streamlit run streamlit_app.py
```

4. **Access the Demo**
Open your browser to `http://localhost:8501`

## 🏗️ Architecture

### Phase 1: MVP (Current)
```
User Input → Streamlit → ConsultancyAgent → Gemini + Knowledge Search → Response
```

**Components:**
- **ConsultancyAgent**: Core MCP agent handling conversation flow
- **Knowledge Search**: Text-based search through Ram's experience documents  
- **Streamlit Interface**: Professional chat interface with metrics
- **Context Management**: Conversation state and lead scoring

### Phase 2: Enhanced (Planned)
```
User → Streamlit → Agent Orchestrator → Multiple MCP Agents → External APIs → Response
                                     ↓
                                 Pinecone + Firebase
```

## 📁 Project Structure

```
Digital Twin 2/
├── streamlit_app.py              # Main Streamlit application
├── requirements.txt              # Python dependencies
├── src/
│   ├── agents/
│   │   └── consultancy_agent.py  # Core MCP agent implementation
│   ├── knowledge/
│   │   └── knowledge_search.py   # Text-based knowledge search
│   ├── config.py                 # Configuration management
│   └── utils/                    # Utility functions
├── knowledge_base/               # Ram's experience documents
│   ├── ram_experience.txt        # Core expertise and experience
│   ├── case_studies.txt          # Anonymized client case studies
│   └── methodologies.txt         # Frameworks and approaches
├── tests/                        # Test suite
└── project_docs/                 # Planning documentation
```

## 🧠 Knowledge Base

The knowledge base contains Ram's expertise across:

- **PMO Setup**: Governance, methodology, resource optimization
- **Dynamics 365**: Implementation, customization, integration
- **Digital Transformation**: Strategy, change management, ROI
- **Public Sector**: Housing associations, councils, compliance
- **Case Studies**: Real project outcomes and methodologies

## 🎯 Features

### Current (Phase 1)
- ✅ Professional chat interface with Ram's expertise
- ✅ Conversation flow management (discovery → expertise → solution → engagement)
- ✅ Knowledge base search and context injection
- ✅ Lead scoring and engagement tracking
- ✅ Multi-stage conversation handling
- ✅ Professional UI with metrics sidebar

### Planned (Phase 2)
- 🔄 Vector-based semantic search (Pinecone)
- 🔄 Firebase conversation storage
- 🔄 Calendar integration for meeting booking
- 🔄 Multi-agent orchestration
- 🔄 Cloud deployment (Google Cloud Run)

## 🚦 Usage Examples

### Discovery Questions
- "We need to set up a PMO for our digital transformation"
- "What's your experience with housing association modernization?"
- "How do you approach change management resistance?"

### Technical Inquiries  
- "What's involved in a Dynamics 365 implementation?"
- "How do you handle legacy system integration?"
- "What's your PMO governance framework?"

### Engagement Conversion
- "Can we schedule a consultation?"
- "What would you recommend for our situation?"
- "How can you help with our transformation?"

## 🔧 Development

### Adding Knowledge
1. Create new `.txt` files in `knowledge_base/`
2. Use clear headings and structured content
3. The system automatically indexes new documents

### Customizing Agent Behavior
Edit `src/agents/consultancy_agent.py`:
- Update `_load_consultancy_persona()` for different expertise
- Modify engagement stages in `_determine_engagement_stage()`
- Adjust lead scoring in `_update_lead_score()`

### Testing
```bash
pytest tests/
```

## 📊 Success Metrics

### Technical Performance
- Response time: <3 seconds for typical queries
- Knowledge retrieval accuracy: 80%+ relevant context
- Conversation flow: Maintains context over 10+ exchanges

### Business Value
- Lead scoring: Identifies high-value prospects (60+ score)
- Engagement conversion: Guides toward consultation requests
- Expertise demonstration: References specific experience and case studies

## 🔑 API Keys Required

### Phase 1 (Minimum)
- `GOOGLE_API_KEY`: Gemini AI for conversation generation

### Phase 2 (Advanced)
- `PINECONE_API_KEY`: Vector database for semantic search
- `FIREBASE_PROJECT_ID`: Conversation storage and analytics
- Additional integrations as needed

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Cloud Deployment (Phase 2)
```bash
# Deploy to Google Cloud Run
gcloud run deploy ram-digital-twin --source . --region us-central1
```

## 📈 Roadmap

### Week 1-2: Foundation ✅
- [x] Basic agent implementation
- [x] Knowledge base preparation  
- [x] Streamlit interface
- [x] Local testing and refinement

### Week 3-4: Enhancement
- [ ] Vector database integration (Pinecone)
- [ ] Firebase conversation storage
- [ ] Cloud deployment
- [ ] Advanced analytics

### Week 5-8: Optimization
- [ ] Multi-agent orchestration
- [ ] Calendar integration
- [ ] Performance optimization
- [ ] Advanced lead management

## 🤝 Contributing

This is a demonstration project showcasing Ram's technical capabilities. For business inquiries or collaboration:

📧 **Email**: ram@senthilmaree.com  
🔗 **LinkedIn**: [Ram Senthil-Maree](https://linkedin.com/in/ramsenthilmaree)  
📅 **Schedule**: [Calendly](https://calendly.com/ram-senthil-maree)

## 📄 License

This project is for demonstration purposes. All rights reserved by Ram Senthil-Maree.