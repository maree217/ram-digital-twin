# Initial Requirements Gathering Session

**Date**: 2025-01-07  
**Participants**: Ram Senthil-Maree (Product Owner), Claude (AI Architect)  
**Session Type**: Discovery & Requirements Gathering  

## Key Outcomes

### Project Vision
- Build sophisticated consultancy AI system using MCP agent framework
- Target: 10-20 initial users for lead generation and expertise demonstration  
- Focus on digital transformation consultancy with RAG implementation showcase

### Architecture Decision
Selected **MCP Agent Framework** (lastmile-ai/mcp-agent) as foundation:
- 5,394 GitHub stars indicating high community trust
- Advanced multi-agent orchestration capabilities
- Standardized Model Context Protocol for future-proofing
- Perfect fit for sophisticated consultancy workflows

### Technical Stack Confirmation
- **Frontend**: Streamlit for rapid development
- **Backend**: Firebase for scalability and authentication
- **LLM**: Gemini 2.0 Flash for cost-efficiency
- **Vector DB**: Pinecone for knowledge base storage
- **Orchestration**: MCP agents for multi-agent workflows

### Risk Assessment
- **Risk Level**: 6.5/10 (Medium-High) due to early MCP protocol
- **Mitigation**: Version locking, adapter patterns, fallback mechanisms
- **Timeline**: 12-week phased implementation

### Next Steps
- Detailed strategic blueprint development
- Product requirements documentation
- Project plan creation

## Questions Asked & Answered

### Core Vision & Business Objectives
**Q**: What is the single most important outcome this system should achieve?  
**A**: Demonstrate RAG implementation expertise while generating qualified consulting leads (70%+ contact capture rate)

**Q**: Who are the 10-20 initial users?  
**A**: Mix of housing association executives, public sector directors, Microsoft Dynamics partners, and LinkedIn connections

### Functional Requirements
**Q**: Complete workflow for complex queries?  
**A**: ConsultancyAgent as primary orchestrator → AssessmentAgent → ExpertiseAgent → SolutionAgent → EngagementAgent

**Q**: Agent specializations needed?  
**A**: Phase 1: Consultancy, Expertise, Engagement. Phase 2: Assessment, Research. Phase 3: Trends, Competitor, Network agents

### Data & Knowledge Architecture  
**Q**: Knowledge base format and integration?  
**A**: 10,000-word knowledge base, custom MCP Server with Pinecone namespaces, automated expansion through ResearchAgent

### Technical Requirements
**Q**: Firebase integration approach?  
**A**: Firestore for conversations/leads, Functions for agent triggers, Authentication for user management

**Q**: Latency expectations?  
**A**: <2s simple queries, <8s complex multi-agent workflows, <15s research-heavy responses

### Risk Mitigation
**Q**: MCP protocol evolution risks?  
**A**: Adapter patterns, version locking, fallback mechanisms to direct LLM calls

**Q**: Testing strategy?  
**A**: Unit tests per agent, integration testing, conversation flow testing, load testing for 10-20 users

## Architecture Highlights

### MCP Agent Framework Benefits
1. **Standardized Orchestration**: Industry-standard protocol for agent communication
2. **Composable Intelligence**: Specialized agents for different consultancy domains  
3. **High-Context Integration**: Native 200k+ context support for full knowledge base
4. **Parallel Workflows**: Fan-out/fan-in patterns for concurrent operations
5. **Production Scalability**: Built on proven patterns, scales from 10 users to enterprise

### Implementation Phases
- **Phase 1 (4 weeks)**: MVP with core agents
- **Phase 2 (8 weeks)**: Enhanced multi-agent system  
- **Phase 3 (12 weeks)**: Advanced intelligence and analytics

### Success Metrics
- 70% lead qualification rate
- 5+ minute average session duration
- 60% returning visitor rate
- 3-5 new client meetings per month