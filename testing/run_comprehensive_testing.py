"""
Comprehensive Testing Runner
Orchestrates the full testing and analysis pipeline
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from comprehensive_user_journey_test import UserJourneyTester
from agent_performance_analyzer import AgentPerformanceAnalyzer

async def run_complete_testing_pipeline():
    """Run the complete testing and analysis pipeline"""
    print("🚀 COMPREHENSIVE AGENT TESTING PIPELINE")
    print("="*50)
    
    # Step 1: Run user journey tests
    print("\n📋 STEP 1: Running User Journey Tests")
    print("-" * 30)
    
    tester = UserJourneyTester()
    
    print(f"🎭 Testing {len(tester.scenarios)} different user scenarios")
    print("⏱️  This may take 5-10 minutes...")
    
    start_time = datetime.now()
    results = await tester.run_all_scenarios()
    end_time = datetime.now()
    
    execution_time = (end_time - start_time).total_seconds()
    
    print(f"✅ Testing completed in {execution_time:.1f} seconds")
    print(f"📊 {len(results)} scenarios executed")
    
    # Save results
    results_file = tester.save_results()
    
    # Step 2: Analyze performance
    print(f"\n🔍 STEP 2: Analyzing Performance")
    print("-" * 30)
    
    analyzer = AgentPerformanceAnalyzer(results_file)
    
    # Print summary
    analyzer.print_summary()
    
    # Save detailed analysis
    analysis_file = analyzer.save_analysis_report()
    
    # Generate refined prompt
    refined_prompt = analyzer.generate_refined_prompt()
    prompt_file = os.path.join(os.path.dirname(results_file), "refined_prompt.txt")
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(refined_prompt)
    
    print(f"\n📝 Refined prompt saved to: {prompt_file}")
    
    # Step 3: Generate executive summary
    print(f"\n📈 STEP 3: Generating Executive Summary")
    print("-" * 30)
    
    exec_summary = generate_executive_summary(results, analyzer)
    summary_file = os.path.join(os.path.dirname(results_file), "executive_summary.md")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(exec_summary)
    
    print(f"📊 Executive summary saved to: {summary_file}")
    
    # Final summary
    print(f"\n🎉 TESTING PIPELINE COMPLETE")
    print("="*50)
    print(f"📁 Results file: {results_file}")
    print(f"📈 Analysis file: {analysis_file}")
    print(f"📝 Refined prompt: {prompt_file}")
    print(f"📊 Executive summary: {summary_file}")
    print(f"⏱️  Total execution time: {execution_time:.1f} seconds")
    
    return {
        "results_file": results_file,
        "analysis_file": analysis_file,
        "prompt_file": prompt_file,
        "summary_file": summary_file,
        "execution_time": execution_time
    }

def generate_executive_summary(results, analyzer) -> str:
    """Generate an executive summary of the testing results"""
    report = analyzer.analyze_all()
    
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    summary = f"""# Agent Performance Testing - Executive Summary

**Generated:** {timestamp}
**Total Scenarios Tested:** {len(results)}

## 🎯 Key Performance Metrics

| Metric | Current Performance | Target | Status |
|--------|-------------------|--------|---------|
| Overall Success Rate | {report['analysis_summary']['overall_success_rate']:.1f}% | 85% | {'✅ Good' if report['analysis_summary']['overall_success_rate'] >= 80 else '⚠️ Needs Improvement'} |
| Stage Progression Accuracy | {report['stage_analysis']['average_stage_accuracy']:.1f}% | 80% | {'✅ Good' if report['stage_analysis']['average_stage_accuracy'] >= 80 else '⚠️ Needs Improvement'} |
| Lead Scoring Accuracy | {report['lead_scoring_analysis']['scoring_accuracy']:.1f}% | 75% | {'✅ Good' if report['lead_scoring_analysis']['scoring_accuracy'] >= 75 else '⚠️ Needs Improvement'} |
| Engagement Conversion Rate | {report['engagement_analysis']['conversion_success_rate']:.1f}% | 70% | {'✅ Good' if report['engagement_analysis']['conversion_success_rate'] >= 70 else '⚠️ Needs Improvement'} |

## 🎭 Persona Performance Analysis

"""
    
    # Add persona performance details
    persona_data = report['persona_analysis']['persona_performance']
    for persona, data in sorted(persona_data.items(), key=lambda x: x[1]['average_success_rate'], reverse=True):
        status = "🟢 Excellent" if data['average_success_rate'] >= 80 else "🟡 Good" if data['average_success_rate'] >= 60 else "🔴 Needs Work"
        summary += f"- **{persona.replace('_', ' ').title()}**: {data['average_success_rate']:.1f}% {status}\n"
    
    summary += f"""
## 🔧 Top 5 Improvement Recommendations

"""
    
    # Add top improvements
    for i, imp in enumerate(report['prompt_improvements'][:5], 1):
        priority_emoji = "🔴" if imp['priority'] == "high" else "🟡" if imp['priority'] == "medium" else "🟢"
        summary += f"{i}. **{imp['category']}** {priority_emoji}\n"
        summary += f"   - *Issue:* {imp['issue']}\n"
        summary += f"   - *Suggestion:* {imp['suggestion']}\n"
        summary += f"   - *Confidence:* {imp['confidence']*100:.0f}%\n\n"
    
    summary += f"""
## 📊 Detailed Findings

### Stage Progression
- **Average Accuracy:** {report['stage_analysis']['average_stage_accuracy']:.1f}%
- **Problematic Scenarios:** {len(report['stage_analysis']['problematic_scenarios'])}
- **Most Common Transitions:** {list(report['stage_analysis']['common_transitions'].keys())[:3]}

### Response Quality
- **Average Response Length:** {report['response_analysis']['average_response_length']:.0f} characters
- **Quality Score:** {report['response_analysis']['average_quality_score']:.1f}/100
- **Main Issues:** {len(report['response_analysis']['quality_issues'])} quality issues identified

### Lead Scoring
- **Average Final Score:** {report['lead_scoring_analysis']['average_final_score']:.1f}/100
- **Scoring Accuracy:** {report['lead_scoring_analysis']['scoring_accuracy']:.1f}%

### Engagement Patterns
- **Scenarios Reaching Engagement:** {report['engagement_analysis']['engagement_scenario_count']}
- **Conversion Success Rate:** {report['engagement_analysis']['conversion_success_rate']:.1f}%
- **Average Engagement Score:** {report['engagement_analysis']['average_engagement_score']:.1f}

## 🎯 Next Steps

1. **Immediate Actions (High Priority)**
   - Address high-priority prompt improvements
   - Focus on worst-performing persona types
   - Refine stage detection logic

2. **Medium-term Improvements**
   - Enhance response quality for specific scenarios
   - Optimize lead scoring algorithm
   - Improve engagement conversion tactics

3. **Long-term Monitoring**
   - Re-run testing monthly to track improvements
   - A/B test prompt variations
   - Monitor real user feedback correlation

## 🎉 Conclusion

The agent demonstrates {f"strong performance with {report['analysis_summary']['overall_success_rate']:.1f}% overall success rate" if report['analysis_summary']['overall_success_rate'] >= 75 else f"room for improvement with {report['analysis_summary']['overall_success_rate']:.1f}% overall success rate"}. 

{f"Key strengths include effective stage progression and lead scoring. " if report['stage_analysis']['average_stage_accuracy'] >= 80 and report['lead_scoring_analysis']['scoring_accuracy'] >= 75 else ""}The testing revealed specific areas for optimization, particularly in {', '.join([imp['category'] for imp in report['prompt_improvements'][:3] if imp['priority'] == 'high'])}.

With the identified improvements implemented, we expect to achieve 85%+ overall success rate and improved user satisfaction across all persona types.
"""
    
    return summary

def main():
    """Main execution function"""
    print("Starting comprehensive agent testing pipeline...")
    
    try:
        results = asyncio.run(run_complete_testing_pipeline())
        print(f"\n🎉 All testing completed successfully!")
        
        # Optionally open results for review
        import platform
        if platform.system() == "Darwin":  # macOS
            os.system(f"open '{results['summary_file']}'")
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()