"""
Agent Performance Analyzer
Analyzes test results and provides prompt refinement suggestions
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, Counter
import statistics

@dataclass
class PromptImprovement:
    category: str
    issue: str
    suggestion: str
    priority: str  # high, medium, low
    affected_scenarios: List[str]
    confidence: float  # 0-1 score

@dataclass
class PerformanceInsight:
    metric: str
    current_value: float
    target_value: float
    gap: float
    improvement_areas: List[str]

class AgentPerformanceAnalyzer:
    def __init__(self, results_file: str):
        self.results_file = results_file
        self.results = self._load_results()
        self.improvements: List[PromptImprovement] = []
        self.insights: List[PerformanceInsight] = []
        
    def _load_results(self) -> Dict[str, Any]:
        """Load test results from JSON file"""
        with open(self.results_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def analyze_all(self) -> Dict[str, Any]:
        """Run complete analysis"""
        print("🔍 Analyzing agent performance...")
        
        # Core analyses
        stage_analysis = self._analyze_stage_progression()
        response_analysis = self._analyze_response_quality()
        lead_scoring_analysis = self._analyze_lead_scoring()
        persona_analysis = self._analyze_persona_effectiveness()
        engagement_analysis = self._analyze_engagement_patterns()
        
        # Generate improvements
        self._generate_prompt_improvements()
        
        # Create comprehensive report
        report = {
            "analysis_summary": {
                "total_scenarios": len(self.results["results"]),
                "overall_success_rate": self._calculate_overall_success_rate(),
                "analysis_timestamp": datetime.now().isoformat()
            },
            "stage_analysis": stage_analysis,
            "response_analysis": response_analysis,
            "lead_scoring_analysis": lead_scoring_analysis,
            "persona_analysis": persona_analysis,
            "engagement_analysis": engagement_analysis,
            "prompt_improvements": [
                {
                    "category": imp.category,
                    "issue": imp.issue,
                    "suggestion": imp.suggestion,
                    "priority": imp.priority,
                    "affected_scenarios": imp.affected_scenarios,
                    "confidence": imp.confidence
                } for imp in self.improvements
            ],
            "performance_insights": [
                {
                    "metric": insight.metric,
                    "current_value": insight.current_value,
                    "target_value": insight.target_value,
                    "gap": insight.gap,
                    "improvement_areas": insight.improvement_areas
                } for insight in self.insights
            ]
        }
        
        return report
    
    def _calculate_overall_success_rate(self) -> float:
        """Calculate overall success rate across all scenarios"""
        if not self.results["results"]:
            return 0.0
        
        total_success = sum(
            result["success_metrics"]["overall_success_rate"] 
            for result in self.results["results"]
        )
        return total_success / len(self.results["results"])
    
    def _analyze_stage_progression(self) -> Dict[str, Any]:
        """Analyze how well the agent progresses through conversation stages"""
        stage_transitions = defaultdict(list)
        stage_accuracy = {}
        problematic_scenarios = []
        
        for result in self.results["results"]:
            scenario_name = result["scenario_name"]
            stages = result["stages"]
            
            # Track stage transitions
            for i in range(len(stages) - 1):
                transition = f"{stages[i]} -> {stages[i+1]}"
                stage_transitions[transition].append(scenario_name)
            
            # Check stage progression accuracy
            stage_score = result["success_metrics"]["stage_progression_score"]
            stage_accuracy[scenario_name] = stage_score
            
            if stage_score < 70:  # Below 70% accuracy
                problematic_scenarios.append({
                    "scenario": scenario_name,
                    "score": stage_score,
                    "stages": stages
                })
        
        # Identify most common transitions
        common_transitions = dict(Counter(
            {k: len(v) for k, v in stage_transitions.items()}
        ).most_common(10))
        
        return {
            "average_stage_accuracy": statistics.mean(stage_accuracy.values()) if stage_accuracy else 0,
            "common_transitions": common_transitions,
            "problematic_scenarios": problematic_scenarios,
            "total_unique_transitions": len(stage_transitions)
        }
    
    def _analyze_response_quality(self) -> Dict[str, Any]:
        """Analyze response quality metrics"""
        response_lengths = []
        response_quality_scores = []
        quality_issues = []
        
        for result in self.results["results"]:
            scenario_name = result["scenario_name"]
            messages = result["messages"]
            
            for msg in messages:
                if "assistant" in msg:
                    response = msg["assistant"]
                    response_lengths.append(len(response))
                    
                    # Check for quality issues
                    issues = self._check_response_quality(response, scenario_name)
                    if issues:
                        quality_issues.extend(issues)
            
            response_quality_scores.append(
                result["success_metrics"]["response_quality_score"]
            )
        
        return {
            "average_response_length": statistics.mean(response_lengths) if response_lengths else 0,
            "median_response_length": statistics.median(response_lengths) if response_lengths else 0,
            "average_quality_score": statistics.mean(response_quality_scores) if response_quality_scores else 0,
            "quality_issues": quality_issues,
            "response_length_distribution": {
                "min": min(response_lengths) if response_lengths else 0,
                "max": max(response_lengths) if response_lengths else 0,
                "std_dev": statistics.stdev(response_lengths) if len(response_lengths) > 1 else 0
            }
        }
    
    def _check_response_quality(self, response: str, scenario: str) -> List[Dict[str, str]]:
        """Check individual response for quality issues"""
        issues = []
        
        # Check for repetitive responses
        if response.count('.') > 10:  # Too many sentences
            issues.append({
                "type": "too_verbose",
                "scenario": scenario,
                "description": "Response may be too long/verbose"
            })
        
        # Check for too short responses to business inquiries
        if len(response) < 30 and "business" in scenario.lower():
            issues.append({
                "type": "too_brief",
                "scenario": scenario,
                "description": "Response too brief for business inquiry"
            })
        
        # Check for generic responses
        generic_phrases = [
            "I can help with that",
            "That's a great question",
            "Let me help you",
            "I understand"
        ]
        if any(phrase in response for phrase in generic_phrases):
            issues.append({
                "type": "generic_response",
                "scenario": scenario,
                "description": "Response contains generic phrases"
            })
        
        # Check for missing empathy in personal scenarios
        if "personal" in scenario.lower() or "casual" in scenario.lower():
            empathy_words = ["understand", "sounds", "feel", "challenging"]
            if not any(word in response.lower() for word in empathy_words):
                issues.append({
                    "type": "missing_empathy",
                    "scenario": scenario,
                    "description": "Personal scenario lacks empathetic language"
                })
        
        return issues
    
    def _analyze_lead_scoring(self) -> Dict[str, Any]:
        """Analyze lead scoring effectiveness"""
        lead_score_progression = {}
        final_scores_by_persona = defaultdict(list)
        scoring_accuracy = []
        
        for result in self.results["results"]:
            scenario_name = result["scenario_name"]
            lead_scores = result["lead_scores"]
            
            if lead_scores:
                # Track progression
                initial_score = lead_scores[0] if len(lead_scores) > 0 else 0
                final_score = lead_scores[-1]
                progression = final_score - initial_score
                
                lead_score_progression[scenario_name] = {
                    "initial": initial_score,
                    "final": final_score,
                    "progression": progression
                }
                
                # Group by persona (extract from scenario name)
                persona = self._extract_persona_from_scenario(scenario_name)
                final_scores_by_persona[persona].append(final_score)
                
                # Check if scoring matches expected range
                expected_range = self._get_expected_lead_score_range(scenario_name)
                if expected_range:
                    in_range = expected_range[0] <= final_score <= expected_range[1]
                    scoring_accuracy.append(in_range)
        
        return {
            "average_final_score": statistics.mean([
                prog["final"] for prog in lead_score_progression.values()
            ]) if lead_score_progression else 0,
            "score_progression_by_scenario": lead_score_progression,
            "scores_by_persona": dict(final_scores_by_persona),
            "scoring_accuracy": (sum(scoring_accuracy) / len(scoring_accuracy) * 100) if scoring_accuracy else 0
        }
    
    def _analyze_persona_effectiveness(self) -> Dict[str, Any]:
        """Analyze how well the agent handles different user personas"""
        persona_performance = defaultdict(list)
        
        for result in self.results["results"]:
            scenario_name = result["scenario_name"]
            success_rate = result["success_metrics"]["overall_success_rate"]
            
            persona = self._extract_persona_from_scenario(scenario_name)
            persona_performance[persona].append({
                "scenario": scenario_name,
                "success_rate": success_rate
            })
        
        # Calculate average performance per persona
        persona_averages = {}
        for persona, performances in persona_performance.items():
            avg_success = statistics.mean([p["success_rate"] for p in performances])
            persona_averages[persona] = {
                "average_success_rate": avg_success,
                "scenario_count": len(performances),
                "scenarios": [p["scenario"] for p in performances]
            }
        
        # Identify best and worst performing personas
        sorted_personas = sorted(
            persona_averages.items(), 
            key=lambda x: x[1]["average_success_rate"], 
            reverse=True
        )
        
        return {
            "persona_performance": persona_averages,
            "best_performing_persona": sorted_personas[0] if sorted_personas else None,
            "worst_performing_persona": sorted_personas[-1] if sorted_personas else None,
            "performance_variance": statistics.stdev([
                p["average_success_rate"] for p in persona_averages.values()
            ]) if len(persona_averages) > 1 else 0
        }
    
    def _analyze_engagement_patterns(self) -> Dict[str, Any]:
        """Analyze engagement conversion patterns"""
        engagement_scenarios = []
        conversion_success = []
        
        for result in self.results["results"]:
            stages = result["stages"]
            scenario_name = result["scenario_name"]
            final_lead_score = result["lead_scores"][-1] if result["lead_scores"] else 0
            
            # Check if scenario reached engagement stage
            has_engagement = "engagement_conversion" in stages
            if has_engagement:
                engagement_scenarios.append({
                    "scenario": scenario_name,
                    "final_score": final_lead_score,
                    "engagement_turns": stages.count("engagement_conversion")
                })
                
                # Consider conversion successful if final score > 60
                conversion_success.append(final_lead_score > 60)
        
        return {
            "engagement_scenario_count": len(engagement_scenarios),
            "conversion_success_rate": (sum(conversion_success) / len(conversion_success) * 100) if conversion_success else 0,
            "average_engagement_score": statistics.mean([
                s["final_score"] for s in engagement_scenarios
            ]) if engagement_scenarios else 0,
            "engagement_scenarios": engagement_scenarios
        }
    
    def _generate_prompt_improvements(self):
        """Generate specific prompt improvement suggestions"""
        
        # Analyze stage progression issues
        stage_analysis = self._analyze_stage_progression()
        if stage_analysis["average_stage_accuracy"] < 80:
            self.improvements.append(PromptImprovement(
                category="Stage Detection",
                issue="Low stage progression accuracy",
                suggestion="Refine stage detection criteria. Add more specific keywords for each stage and improve the logic in _determine_engagement_stage().",
                priority="high",
                affected_scenarios=[s["scenario"] for s in stage_analysis["problematic_scenarios"]],
                confidence=0.9
            ))
        
        # Analyze response quality issues
        response_analysis = self._analyze_response_quality()
        quality_issues = response_analysis["quality_issues"]
        
        if any(issue["type"] == "too_verbose" for issue in quality_issues):
            self.improvements.append(PromptImprovement(
                category="Response Length",
                issue="Responses sometimes too verbose",
                suggestion="Add explicit length guidance: 'Keep responses concise - 1-2 sentences for simple questions, longer only when detailed expertise is requested.'",
                priority="medium",
                affected_scenarios=list(set(issue["scenario"] for issue in quality_issues if issue["type"] == "too_verbose")),
                confidence=0.8
            ))
        
        if any(issue["type"] == "missing_empathy" for issue in quality_issues):
            self.improvements.append(PromptImprovement(
                category="Empathy",
                issue="Missing empathetic responses in personal scenarios",
                suggestion="Strengthen empathy instructions: 'Always acknowledge the user's emotional state before redirecting. Use phrases like \"That sounds challenging\" or \"I understand that can be frustrating.\"'",
                priority="high",
                affected_scenarios=list(set(issue["scenario"] for issue in quality_issues if issue["type"] == "missing_empathy")),
                confidence=0.85
            ))
        
        # Analyze lead scoring issues
        lead_analysis = self._analyze_lead_scoring()
        if lead_analysis["scoring_accuracy"] < 75:
            self.improvements.append(PromptImprovement(
                category="Lead Scoring",
                issue="Lead scoring not aligned with user intent",
                suggestion="Revise lead scoring criteria. Add more weight to specific business terminology and reduce scores for off-topic conversations.",
                priority="medium",
                affected_scenarios=["all_scenarios"],
                confidence=0.7
            ))
        
        # Analyze persona handling
        persona_analysis = self._analyze_persona_effectiveness()
        worst_persona = persona_analysis.get("worst_performing_persona")
        if worst_persona and worst_persona[1]["average_success_rate"] < 60:
            persona_name = worst_persona[0]
            self.improvements.append(PromptImprovement(
                category="Persona Handling",
                issue=f"Poor performance with {persona_name} persona",
                suggestion=f"Add specific guidance for handling {persona_name} users. Consider their unique motivations and communication style.",
                priority="medium",
                affected_scenarios=worst_persona[1]["scenarios"],
                confidence=0.75
            ))
        
        # Analyze engagement conversion
        engagement_analysis = self._analyze_engagement_patterns()
        if engagement_analysis["conversion_success_rate"] < 70:
            self.improvements.append(PromptImprovement(
                category="Engagement Conversion",
                issue="Low conversion rate for engaged users",
                suggestion="Improve engagement conversion prompts. Add more specific calls-to-action and clearer value propositions when users show interest.",
                priority="high",
                affected_scenarios=[s["scenario"] for s in engagement_analysis["engagement_scenarios"]],
                confidence=0.8
            ))
        
        # Sort improvements by priority and confidence
        self.improvements.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}[x.priority],
            x.confidence
        ), reverse=True)
    
    def _extract_persona_from_scenario(self, scenario_name: str) -> str:
        """Extract persona type from scenario name"""
        persona_map = {
            "greeting": "casual_browser",
            "business": "qualified_prospect", 
            "skeptical": "skeptical_buyer",
            "intent": "high_value_prospect",
            "personal": "off_topic_user",
            "technical": "technical_evaluator",
            "budget": "cost_conscious_buyer",
            "public": "public_sector_buyer",
            "stakeholders": "corporate_buyer",
            "competitor": "comparative_buyer",
            "crisis": "crisis_buyer",
            "extended": "exploratory_buyer",
            "english": "limited_english",
            "referral": "referred_prospect",
            "academic": "academic",
            "startup": "startup",
            "international": "international",
            "vendor": "formal_buyer",
            "follow": "returning_prospect",
            "difficult": "hostile",
            "implementation": "implementation_buyer"
        }
        
        for key, persona in persona_map.items():
            if key in scenario_name.lower():
                return persona
        
        return "unknown"
    
    def _get_expected_lead_score_range(self, scenario_name: str) -> Optional[Tuple[int, int]]:
        """Get expected lead score range for a scenario"""
        # This would typically come from the test scenario definitions
        # For now, provide general ranges based on scenario type
        if "high_intent" in scenario_name or "crisis" in scenario_name:
            return (70, 100)
        elif "business" in scenario_name or "technical" in scenario_name:
            return (30, 70)
        elif "personal" in scenario_name or "casual" in scenario_name:
            return (0, 30)
        else:
            return (20, 60)
    
    def generate_refined_prompt(self) -> str:
        """Generate a refined prompt based on analysis"""
        base_prompt = """You are Ram Senthil-Maree, an experienced digital transformation consultant. You have a proven track record, but you approach conversations naturally and let users guide the discussion.

**CORE PRINCIPLES:**
1. BE NATURAL: Respond like meeting someone on the street - match their energy and tone
2. BE EMPATHETIC: Acknowledge their feelings and situation with understanding
3. LET THEM LEAD: Don't overwhelm with expertise unless they ask for it
4. MATCH THEIR ENERGY: Short responses to short messages, detailed responses when they engage deeply

**CONVERSATION APPROACH:**
- For greetings (hi, hello, how are you): Respond naturally and briefly introduce your purpose
- For off-topic chat (weather, personal): Be empathetic but gently redirect to how you can help
- For business topics: Share relevant experience proportionally to their level of detail
- For direct questions: Answer directly and appropriately to their knowledge level

**RESPONSE GUIDELINES:**
- If they give one line, respond with 1-2 sentences maximum
- If they ask basic questions, give basic answers
- Only share detailed expertise when they show genuine interest or ask specific questions
- Always be helpful but not pushy"""
        
        # Add improvements based on analysis
        improvements_text = "\n\n**PERFORMANCE IMPROVEMENTS BASED ON ANALYSIS:**\n"
        
        high_priority_improvements = [imp for imp in self.improvements if imp.priority == "high"]
        for imp in high_priority_improvements[:3]:  # Top 3 high-priority improvements
            improvements_text += f"- {imp.category}: {imp.suggestion}\n"
        
        return base_prompt + improvements_text
    
    def save_analysis_report(self, filename: str = None) -> str:
        """Save complete analysis report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_performance_analysis_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(self.results_file), filename)
        
        report = self.analyze_all()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Analysis report saved to: {filepath}")
        return filepath
    
    def print_summary(self):
        """Print a summary of key findings"""
        report = self.analyze_all()
        
        print("\n" + "="*60)
        print("🎯 AGENT PERFORMANCE ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📈 Overall Success Rate: {report['analysis_summary']['overall_success_rate']:.1f}%")
        
        print(f"\n🎭 Stage Progression:")
        print(f"   Average Accuracy: {report['stage_analysis']['average_stage_accuracy']:.1f}%")
        print(f"   Problematic Scenarios: {len(report['stage_analysis']['problematic_scenarios'])}")
        
        print(f"\n💬 Response Quality:")
        print(f"   Average Length: {report['response_analysis']['average_response_length']:.0f} chars")
        print(f"   Quality Score: {report['response_analysis']['average_quality_score']:.1f}/100")
        
        print(f"\n🎯 Lead Scoring:")
        print(f"   Average Final Score: {report['lead_scoring_analysis']['average_final_score']:.1f}")
        print(f"   Scoring Accuracy: {report['lead_scoring_analysis']['scoring_accuracy']:.1f}%")
        
        print(f"\n🤝 Engagement:")
        print(f"   Conversion Rate: {report['engagement_analysis']['conversion_success_rate']:.1f}%")
        print(f"   Engagement Scenarios: {report['engagement_analysis']['engagement_scenario_count']}")
        
        print(f"\n🔧 TOP IMPROVEMENT RECOMMENDATIONS:")
        for i, imp in enumerate(report['prompt_improvements'][:5], 1):
            print(f"   {i}. [{imp['priority'].upper()}] {imp['category']}: {imp['issue']}")
        
        print("\n" + "="*60)

def main():
    """Main execution function for analysis"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent_performance_analyzer.py <results_file.json>")
        sys.exit(1)
    
    results_file = sys.argv[1]
    
    if not os.path.exists(results_file):
        print(f"Error: Results file '{results_file}' not found")
        sys.exit(1)
    
    analyzer = AgentPerformanceAnalyzer(results_file)
    
    # Run analysis and print summary
    analyzer.print_summary()
    
    # Save detailed report
    report_file = analyzer.save_analysis_report()
    
    # Generate refined prompt
    refined_prompt = analyzer.generate_refined_prompt()
    
    prompt_file = os.path.join(os.path.dirname(results_file), "refined_prompt.txt")
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(refined_prompt)
    
    print(f"📝 Refined prompt saved to: {prompt_file}")

if __name__ == "__main__":
    main()