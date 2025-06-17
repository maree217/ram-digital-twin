"""
Comprehensive User Journey Testing Framework
Runs 20+ different user scenarios in headless mode to test agent performance
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
from dataclasses import dataclass, asdict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.consultancy_agent import ConsultancyAgent, ConversationContext

@dataclass
class TestScenario:
    name: str
    description: str
    user_messages: List[str]
    expected_stages: List[str]
    success_criteria: Dict[str, Any]
    persona_type: str = "unknown"

@dataclass
class ConversationResult:
    scenario_name: str
    conversation_id: str
    messages: List[Dict[str, Any]]
    stages: List[str]
    lead_scores: List[int]
    knowledge_sources: List[int]
    success_metrics: Dict[str, Any]
    execution_time: float
    timestamp: str

class UserJourneyTester:
    def __init__(self):
        self.agent = ConsultancyAgent()
        self.results: List[ConversationResult] = []
        self.scenarios = self._create_test_scenarios()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _create_test_scenarios(self) -> List[TestScenario]:
        """Create 20+ diverse user journey scenarios"""
        return [
            # 1. Simple greeting flow
            TestScenario(
                name="simple_greeting",
                description="Basic greeting and casual introduction",
                user_messages=["hi", "just browsing", "what can you help with"],
                expected_stages=["greeting", "casual_chat", "rapport_building"],
                success_criteria={"final_lead_score": {"min": 0, "max": 30}},
                persona_type="casual_browser"
            ),
            
            # 2. Direct business inquiry
            TestScenario(
                name="direct_business_inquiry",
                description="User immediately asks about business services",
                user_messages=[
                    "I need help with digital transformation",
                    "We're a housing association with 50,000 properties",
                    "What's your approach to PMO setup?"
                ],
                expected_stages=["solution_presentation", "expertise_demonstration", "expertise_demonstration"],
                success_criteria={"final_lead_score": {"min": 30, "max": 70}},
                persona_type="qualified_prospect"
            ),
            
            # 3. Skeptical user journey
            TestScenario(
                name="skeptical_user",
                description="User is skeptical and tests expertise",
                user_messages=[
                    "Another consultant...",
                    "Have you actually delivered any real results?",
                    "Prove you know Dynamics 365",
                    "What's the biggest transformation you've done?"
                ],
                expected_stages=["casual_chat", "expertise_demonstration", "expertise_demonstration", "expertise_demonstration"],
                success_criteria={"final_lead_score": {"min": 15, "max": 50}},
                persona_type="skeptical_buyer"
            ),
            
            # 4. High-intent engagement journey
            TestScenario(
                name="high_intent_engagement",
                description="User ready to engage and schedule consultation",
                user_messages=[
                    "Hello",
                    "We need urgent help with our Dynamics 365 implementation",
                    "Budget is not an issue, we need this done quickly",
                    "Can we schedule a call this week?",
                    "I'm the CTO and can make decisions immediately"
                ],
                expected_stages=["greeting", "solution_presentation", "solution_presentation", "engagement_conversion", "engagement_conversion"],
                success_criteria={"final_lead_score": {"min": 70, "max": 100}},
                persona_type="high_value_prospect"
            ),
            
            # 5. Personal problems deflection
            TestScenario(
                name="personal_problems",
                description="User shares personal issues, agent redirects professionally",
                user_messages=[
                    "hi",
                    "just bored with life",
                    "my boss hates me",
                    "how do I beat him up",
                    "yes"
                ],
                expected_stages=["greeting", "casual_chat", "casual_chat", "casual_chat", "rapport_building"],
                success_criteria={"final_lead_score": {"min": 0, "max": 20}},
                persona_type="off_topic_user"
            ),
            
            # 6. Technical deep-dive journey
            TestScenario(
                name="technical_deep_dive",
                description="Technical user asking detailed implementation questions",
                user_messages=[
                    "I'm a technical architect",
                    "Tell me about your Dynamics 365 Power Platform integrations",
                    "How do you handle data migration from legacy systems?",
                    "What about custom plugin development and security?",
                    "Can you review our current architecture?"
                ],
                expected_stages=["rapport_building", "expertise_demonstration", "expertise_demonstration", "expertise_demonstration", "solution_presentation"],
                success_criteria={"final_lead_score": {"min": 40, "max": 80}},
                persona_type="technical_evaluator"
            ),
            
            # 7. Budget-conscious inquiry
            TestScenario(
                name="budget_conscious",
                description="User very focused on cost and ROI",
                user_messages=[
                    "What are your rates?",
                    "That seems expensive",
                    "What ROI can you guarantee?",
                    "Do you have any case studies with actual numbers?",
                    "Can we do this in phases to spread the cost?"
                ],
                expected_stages=["rapport_building", "casual_chat", "expertise_demonstration", "expertise_demonstration", "solution_presentation"],
                success_criteria={"final_lead_score": {"min": 25, "max": 65}},
                persona_type="cost_conscious_buyer"
            ),
            
            # 8. Public sector specific inquiry
            TestScenario(
                name="public_sector_inquiry",
                description="Public sector organization with specific needs",
                user_messages=[
                    "We're a local council",
                    "Need help with our digital transformation strategy",
                    "We have strict procurement processes",
                    "Can you work within our framework agreements?",
                    "What's your experience with GDPR compliance?"
                ],
                expected_stages=["rapport_building", "solution_presentation", "expertise_demonstration", "expertise_demonstration", "expertise_demonstration"],
                success_criteria={"final_lead_score": {"min": 35, "max": 75}},
                persona_type="public_sector_buyer"
            ),
            
            # 9. Multiple decision makers journey
            TestScenario(
                name="multiple_stakeholders",
                description="User representing a team with multiple stakeholders",
                user_messages=[
                    "I need to present options to my board",
                    "What information do you need to provide a proposal?",
                    "Can you present to our executive team?",
                    "We need references from similar organizations",
                    "What's the typical timeline for implementation?"
                ],
                expected_stages=["rapport_building", "solution_presentation", "engagement_conversion", "expertise_demonstration", "solution_presentation"],
                success_criteria={"final_lead_score": {"min": 45, "max": 85}},
                persona_type="corporate_buyer"
            ),
            
            # 10. Competitor comparison journey
            TestScenario(
                name="competitor_comparison",
                description="User comparing against other consultants",
                user_messages=[
                    "We're evaluating several consultants",
                    "How do you differ from McKinsey or Deloitte?",
                    "What makes your approach unique?",
                    "Can you provide competitive pricing?",
                    "Why should we choose you over bigger firms?"
                ],
                expected_stages=["rapport_building", "expertise_demonstration", "expertise_demonstration", "solution_presentation", "expertise_demonstration"],
                success_criteria={"final_lead_score": {"min": 30, "max": 70}},
                persona_type="comparative_buyer"
            ),
            
            # 11. Urgent crisis scenario
            TestScenario(
                name="urgent_crisis",
                description="Organization in crisis needing immediate help",
                user_messages=[
                    "Our system has failed completely",
                    "We need emergency consulting support",
                    "Can you start immediately?",
                    "Money is no object, we just need it fixed",
                    "When can we have a crisis call?"
                ],
                expected_stages=["rapport_building", "solution_presentation", "engagement_conversion", "engagement_conversion", "engagement_conversion"],
                success_criteria={"final_lead_score": {"min": 60, "max": 100}},
                persona_type="crisis_buyer"
            ),
            
            # 12. Long conversation journey
            TestScenario(
                name="extended_conversation",
                description="Long conversation with multiple topics",
                user_messages=[
                    "Hello there",
                    "Tell me about your background",
                    "Interesting, what about PMO setup?",
                    "We've tried setting up a PMO before and failed",
                    "What would you do differently?",
                    "That sounds promising",
                    "What about change management?",
                    "Our staff resist change",
                    "How do you handle that?",
                    "Can we schedule a detailed discussion?"
                ],
                expected_stages=["greeting", "expertise_demonstration", "expertise_demonstration", "solution_presentation", "solution_presentation", "rapport_building", "expertise_demonstration", "solution_presentation", "solution_presentation", "engagement_conversion"],
                success_criteria={"final_lead_score": {"min": 50, "max": 90}},
                persona_type="exploratory_buyer"
            ),
            
            # 13. Non-English speaker simulation
            TestScenario(
                name="simple_english",
                description="User with limited English, simple responses",
                user_messages=[
                    "hello help business",
                    "yes need help system",
                    "how much cost?",
                    "ok good thank you"
                ],
                expected_stages=["greeting", "rapport_building", "solution_presentation", "rapport_building"],
                success_criteria={"final_lead_score": {"min": 10, "max": 40}},
                persona_type="limited_english"
            ),
            
            # 14. Previous client referral
            TestScenario(
                name="referral_inquiry",
                description="Someone referred by previous client",
                user_messages=[
                    "John from Riverside Housing recommended you",
                    "He said you transformed their operations",
                    "We have similar challenges",
                    "Can you replicate what you did for them?",
                    "What would be the first steps?"
                ],
                expected_stages=["rapport_building", "expertise_demonstration", "solution_presentation", "solution_presentation", "solution_presentation"],
                success_criteria={"final_lead_score": {"min": 40, "max": 80}},
                persona_type="referred_prospect"
            ),
            
            # 15. Academic/research inquiry
            TestScenario(
                name="academic_inquiry",
                description="Academic or researcher asking for insights",
                user_messages=[
                    "I'm researching digital transformation best practices",
                    "Can you share insights on PMO effectiveness?",
                    "What trends are you seeing in the industry?",
                    "Would you be willing to participate in a study?",
                    "Thank you for the insights"
                ],
                expected_stages=["rapport_building", "expertise_demonstration", "expertise_demonstration", "rapport_building", "rapport_building"],
                success_criteria={"final_lead_score": {"min": 0, "max": 30}},
                persona_type="academic"
            ),
            
            # 16. Startup inquiry
            TestScenario(
                name="startup_inquiry",
                description="Fast-growing startup needing scalable solutions",
                user_messages=[
                    "We're a fast-growing fintech startup",
                    "We need to scale our operations quickly",
                    "What's the most cost-effective approach?",
                    "We're looking at Dynamics 365 vs Salesforce",
                    "Can you help us make the right choice?"
                ],
                expected_stages=["rapport_building", "solution_presentation", "solution_presentation", "expertise_demonstration", "solution_presentation"],
                success_criteria={"final_lead_score": {"min": 35, "max": 75}},
                persona_type="startup"
            ),
            
            # 17. International client
            TestScenario(
                name="international_inquiry",
                description="International client with specific requirements",
                user_messages=[
                    "We're based in Dubai",
                    "Do you work with international clients?",
                    "We need MENA region compliance",
                    "Can you work with our local teams?",
                    "What about time zone differences for support?"
                ],
                expected_stages=["rapport_building", "expertise_demonstration", "expertise_demonstration", "solution_presentation", "solution_presentation"],
                success_criteria={"final_lead_score": {"min": 30, "max": 70}},
                persona_type="international"
            ),
            
            # 18. Vendor evaluation process
            TestScenario(
                name="formal_vendor_evaluation",
                description="Formal RFP/vendor evaluation process",
                user_messages=[
                    "We're running a formal tender process",
                    "Can you respond to our RFP?",
                    "We need detailed pricing and timelines",
                    "What certifications do you hold?",
                    "When can you submit your proposal?"
                ],
                expected_stages=["rapport_building", "engagement_conversion", "solution_presentation", "expertise_demonstration", "engagement_conversion"],
                success_criteria={"final_lead_score": {"min": 50, "max": 90}},
                persona_type="formal_buyer"
            ),
            
            # 19. Follow-up conversation
            TestScenario(
                name="follow_up_conversation",
                description="Returning user who spoke before",
                user_messages=[
                    "Hi, we spoke last month about PMO setup",
                    "We've gotten approval to move forward",
                    "Can we schedule that consultation now?",
                    "What information do you need from us?",
                    "Perfect, looking forward to working together"
                ],
                expected_stages=["rapport_building", "engagement_conversion", "engagement_conversion", "solution_presentation", "engagement_conversion"],
                success_criteria={"final_lead_score": {"min": 60, "max": 100}},
                persona_type="returning_prospect"
            ),
            
            # 20. Hostile/difficult user
            TestScenario(
                name="difficult_user",
                description="Hostile or difficult user testing limits",
                user_messages=[
                    "Consultants are all the same",
                    "You're probably just going to sell me something",
                    "I bet you've never actually done the work yourself",
                    "This is a waste of time",
                    "Fine, prove me wrong"
                ],
                expected_stages=["casual_chat", "casual_chat", "expertise_demonstration", "casual_chat", "expertise_demonstration"],
                success_criteria={"final_lead_score": {"min": 0, "max": 35}},
                persona_type="hostile"
            ),
            
            # 21. Technical implementation focus
            TestScenario(
                name="implementation_focused",
                description="User focused specifically on implementation details",
                user_messages=[
                    "We've already decided on Dynamics 365",
                    "We need implementation support",
                    "What's your methodology?",
                    "How do you handle data migration?",
                    "What about user training and change management?",
                    "When can we start?"
                ],
                expected_stages=["rapport_building", "solution_presentation", "expertise_demonstration", "expertise_demonstration", "expertise_demonstration", "engagement_conversion"],
                success_criteria={"final_lead_score": {"min": 55, "max": 95}},
                persona_type="implementation_buyer"
            )
        ]
    
    async def run_scenario(self, scenario: TestScenario) -> ConversationResult:
        """Run a single test scenario"""
        start_time = datetime.now()
        conversation_id = f"test_{scenario.name}_{uuid.uuid4().hex[:8]}"
        
        # Initialize conversation context
        context = ConversationContext(
            conversation_id=conversation_id,
            messages=[],
            engagement_stage="discovery",
            user_type=scenario.persona_type
        )
        
        messages = []
        stages = []
        lead_scores = []
        knowledge_sources = []
        
        self.logger.info(f"Running scenario: {scenario.name}")
        
        for i, user_message in enumerate(scenario.user_messages):
            try:
                # Add user message to context
                context.messages.append({"role": "user", "content": user_message})
                
                # Get agent response
                response = await self.agent.handle_interaction(user_message, context)
                
                # Record interaction
                messages.append({
                    "turn": i + 1,
                    "user": user_message,
                    "assistant": response["content"],
                    "stage": response["stage"],
                    "lead_score": response["lead_score"],
                    "knowledge_sources": response.get("knowledge_sources", 0)
                })
                
                # Add assistant response to context
                context.messages.append({"role": "assistant", "content": response["content"]})
                
                # Track metrics
                stages.append(response["stage"])
                lead_scores.append(response["lead_score"])
                knowledge_sources.append(response.get("knowledge_sources", 0))
                
                # Update context
                context.engagement_stage = response["stage"]
                context.lead_score = response["lead_score"]
                
                # Small delay to simulate human interaction
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in scenario {scenario.name}, message {i}: {str(e)}")
                messages.append({
                    "turn": i + 1,
                    "user": user_message,
                    "assistant": f"ERROR: {str(e)}",
                    "stage": "error",
                    "lead_score": context.lead_score,
                    "knowledge_sources": 0
                })
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Calculate success metrics
        success_metrics = self._calculate_success_metrics(
            scenario, stages, lead_scores, messages
        )
        
        return ConversationResult(
            scenario_name=scenario.name,
            conversation_id=conversation_id,
            messages=messages,
            stages=stages,
            lead_scores=lead_scores,
            knowledge_sources=knowledge_sources,
            success_metrics=success_metrics,
            execution_time=execution_time,
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_success_metrics(self, scenario: TestScenario, stages: List[str], 
                                 lead_scores: List[int], messages: List[Dict]) -> Dict[str, Any]:
        """Calculate success metrics for a scenario"""
        metrics = {
            "stage_progression_score": 0,
            "lead_score_progression": 0,
            "response_quality_score": 0,
            "criteria_met": {},
            "overall_success_rate": 0
        }
        
        # Check final lead score against criteria
        if lead_scores:
            final_score = lead_scores[-1]
            criteria = scenario.success_criteria.get("final_lead_score", {})
            min_score = criteria.get("min", 0)
            max_score = criteria.get("max", 100)
            
            metrics["criteria_met"]["lead_score_range"] = min_score <= final_score <= max_score
            metrics["lead_score_progression"] = final_score
        
        # Check stage progression
        expected_stages = scenario.expected_stages
        if len(stages) >= len(expected_stages):
            stage_matches = sum(1 for i, stage in enumerate(expected_stages) 
                              if i < len(stages) and stages[i] == stage)
            metrics["stage_progression_score"] = (stage_matches / len(expected_stages)) * 100
            metrics["criteria_met"]["stage_progression"] = stage_matches >= len(expected_stages) * 0.7
        
        # Response quality (length and content checks)
        if messages:
            total_response_length = sum(len(msg.get("assistant", "")) for msg in messages)
            avg_response_length = total_response_length / len(messages)
            
            # Score based on appropriate response length (not too short, not too long)
            if 50 <= avg_response_length <= 500:
                metrics["response_quality_score"] = 100
            elif 20 <= avg_response_length <= 800:
                metrics["response_quality_score"] = 80
            else:
                metrics["response_quality_score"] = 60
        
        # Overall success rate
        criteria_met_count = sum(1 for met in metrics["criteria_met"].values() if met)
        total_criteria = len(metrics["criteria_met"])
        if total_criteria > 0:
            metrics["overall_success_rate"] = (criteria_met_count / total_criteria) * 100
        
        return metrics
    
    async def run_all_scenarios(self) -> List[ConversationResult]:
        """Run all test scenarios"""
        self.logger.info(f"Starting comprehensive testing with {len(self.scenarios)} scenarios")
        
        results = []
        for scenario in self.scenarios:
            try:
                result = await self.run_scenario(scenario)
                results.append(result)
                self.logger.info(f"Completed scenario: {scenario.name} - Success rate: {result.success_metrics['overall_success_rate']:.1f}%")
            except Exception as e:
                self.logger.error(f"Failed to run scenario {scenario.name}: {str(e)}")
        
        self.results = results
        return results
    
    def save_results(self, filename: str = None) -> str:
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"user_journey_test_results_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Convert results to serializable format
        serializable_results = [asdict(result) for result in self.results]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "test_run": {
                    "timestamp": datetime.now().isoformat(),
                    "total_scenarios": len(self.scenarios),
                    "total_results": len(self.results)
                },
                "results": serializable_results
            }, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to: {filepath}")
        return filepath

async def main():
    """Main execution function"""
    tester = UserJourneyTester()
    
    print("🚀 Starting Comprehensive User Journey Testing")
    print(f"📊 Running {len(tester.scenarios)} different scenarios")
    print("⏱️  This may take several minutes...")
    
    # Run all scenarios
    results = await tester.run_all_scenarios()
    
    # Save results
    filepath = tester.save_results()
    
    # Print summary
    print(f"\n✅ Testing Complete!")
    print(f"📁 Results saved to: {filepath}")
    print(f"📈 Scenarios run: {len(results)}")
    
    # Calculate overall stats
    if results:
        avg_success_rate = sum(r.success_metrics['overall_success_rate'] for r in results) / len(results)
        avg_lead_score = sum(r.lead_scores[-1] if r.lead_scores else 0 for r in results) / len(results)
        avg_execution_time = sum(r.execution_time for r in results) / len(results)
        
        print(f"📊 Average Success Rate: {avg_success_rate:.1f}%")
        print(f"🎯 Average Final Lead Score: {avg_lead_score:.1f}")
        print(f"⚡ Average Execution Time: {avg_execution_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())