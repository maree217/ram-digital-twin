#!/usr/bin/env python3
"""
Analytics Dashboard for Ram Digital Twin - Business Conversion Metrics
"""
import streamlit as st
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys

# Add src to path
sys.path.append('src')
from src.analytics.conversation_tracker import ConversationTracker

st.set_page_config(
    page_title="Ram Digital Twin - Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    margin: 0.5rem 0;
}

.conversion-metric {
    background: linear-gradient(90deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
}

.warning-metric {
    background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
}

.danger-metric {
    background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.title("📊 Ram Digital Twin - Business Analytics Dashboard")
    
    # Initialize tracker
    tracker = ConversationTracker()
    
    if not tracker.db:
        st.error("❌ Firebase not available - Analytics dashboard requires Firebase connection")
        st.info("💡 This dashboard tracks conversation metrics to optimize conversion rates")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.header("📅 Analytics Period")
        
        # Date selection
        today = datetime.now().date()
        start_date = st.date_input(
            "Start Date",
            value=today - timedelta(days=7),
            max_value=today
        )
        end_date = st.date_input(
            "End Date",
            value=today,
            max_value=today
        )
        
        if start_date > end_date:
            st.error("Start date must be before end date")
            return
        
        st.header("🎯 Target Metrics")
        st.metric("Target Conversion Rate", "25%", help="Goal: 1 in 4 visitors schedule a meeting")
        st.metric("Target Interactions", "5+", help="Goal: Average 5+ messages per conversation")
        st.metric("Target Quality Rate", "60%", help="Goal: 60% have 3+ interactions")
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    # Mock data for demonstration (replace with real data when Firebase is connected)
    if st.button("🔄 Generate Demo Analytics"):
        demo_analytics = generate_demo_analytics()
        display_analytics(demo_analytics)
    else:
        st.info("👆 Click 'Generate Demo Analytics' to see the dashboard in action")
        st.markdown("""
        ### 📊 This Dashboard Tracks:
        
        **🎯 Conversion Metrics:**
        - Visitors who schedule meetings/calls
        - Conversion rate by conversation stage
        - Time to conversion analysis
        
        **💬 Engagement Quality:**
        - Interaction count per conversation
        - Session duration analysis
        - Drop-off point identification
        
        **🧠 AI Performance:**
        - Response quality scores
        - Knowledge source utilization
        - User satisfaction indicators
        
        **📈 Business Intelligence:**
        - Daily/weekly trends
        - Peak engagement times
        - Most effective conversation paths
        """)

def generate_demo_analytics():
    """Generate demo analytics data to show dashboard capabilities"""
    return {
        'total_conversations': 23,
        'conversions_achieved': 6,
        'conversion_rate': 26.1,
        'avg_interactions_per_conversation': 4.2,
        'avg_session_duration_minutes': 8.5,
        'quality_conversations': 14,
        'avg_final_lead_score': 67,
        'stage_distribution': {
            'discovery': 3,
            'expertise_demonstration': 8,
            'solution_presentation': 7,
            'engagement_conversion': 5
        },
        'daily_trends': [
            {'date': '2025-12-01', 'conversations': 3, 'conversions': 1},
            {'date': '2025-12-02', 'conversations': 5, 'conversions': 1},
            {'date': '2025-12-03', 'conversations': 4, 'conversions': 2},
            {'date': '2025-12-04', 'conversations': 6, 'conversions': 1},
            {'date': '2025-12-05', 'conversations': 3, 'conversions': 0},
            {'date': '2025-12-06', 'conversations': 2, 'conversions': 1},
        ],
        'interaction_distribution': {
            '1-2 interactions': 9,
            '3-4 interactions': 8,
            '5+ interactions': 6
        },
        'engagement_quality_scores': [7.2, 8.1, 6.8, 9.2, 7.9, 8.5, 6.3, 8.8, 7.5, 8.2]
    }

def display_analytics(analytics):
    """Display the analytics dashboard"""
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        conversion_rate = analytics['conversion_rate']
        if conversion_rate >= 25:
            st.markdown(f"""
            <div class="conversion-metric">
                <h3>🎯 Conversion Rate</h3>
                <h2>{conversion_rate:.1f}%</h2>
                <p>✅ Above target (25%)</p>
            </div>
            """, unsafe_allow_html=True)
        elif conversion_rate >= 15:
            st.markdown(f"""
            <div class="warning-metric">
                <h3>⚠️ Conversion Rate</h3>
                <h2>{conversion_rate:.1f}%</h2>
                <p>Approaching target</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="danger-metric">
                <h3>❌ Conversion Rate</h3>
                <h2>{conversion_rate:.1f}%</h2>
                <p>Below target (25%)</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.metric(
            label="💬 Total Conversations",
            value=analytics['total_conversations'],
            delta=f"+{analytics.get('delta_conversations', 5)} vs last period"
        )
    
    with col3:
        st.metric(
            label="📞 Meetings Scheduled",
            value=analytics['conversions_achieved'],
            delta=f"+{analytics.get('delta_conversions', 2)} vs last period"
        )
    
    with col4:
        avg_interactions = analytics['avg_interactions_per_conversation']
        st.metric(
            label="📊 Avg Interactions",
            value=f"{avg_interactions:.1f}",
            delta="Target: 5+" if avg_interactions < 5 else "✅ Above target"
        )
    
    # Detailed Analytics
    st.markdown("---")
    
    # Row 2: Conversion Funnel and Engagement Quality
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Conversation Stage Distribution")
        
        stage_data = analytics['stage_distribution']
        fig_stages = px.pie(
            values=list(stage_data.values()),
            names=list(stage_data.keys()),
            title="Where do conversations end up?",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_stages, use_container_width=True)
        
        # Analysis
        if stage_data.get('engagement_conversion', 0) >= stage_data.get('discovery', 1):
            st.success("✅ Good conversion funnel - many reach final stage")
        else:
            st.warning("⚠️ Most conversations stop at early stages - review engagement strategy")
    
    with col2:
        st.subheader("💬 Interaction Quality Distribution")
        
        interaction_data = analytics['interaction_distribution']
        fig_interactions = px.bar(
            x=list(interaction_data.keys()),
            y=list(interaction_data.values()),
            title="How many interactions per conversation?",
            color=list(interaction_data.values()),
            color_continuous_scale="viridis"
        )
        fig_interactions.update_layout(showlegend=False)
        st.plotly_chart(fig_interactions, use_container_width=True)
        
        quality_rate = (analytics['quality_conversations'] / analytics['total_conversations']) * 100
        if quality_rate >= 60:
            st.success(f"✅ Quality Rate: {quality_rate:.1f}% (Target: 60%)")
        else:
            st.warning(f"⚠️ Quality Rate: {quality_rate:.1f}% - Need more engaging conversations")
    
    # Row 3: Trends and Performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Conversation Trends")
        
        daily_data = analytics['daily_trends']
        df_daily = pd.DataFrame(daily_data)
        
        fig_trends = go.Figure()
        fig_trends.add_trace(go.Scatter(
            x=df_daily['date'],
            y=df_daily['conversations'],
            mode='lines+markers',
            name='Conversations',
            line=dict(color='blue')
        ))
        fig_trends.add_trace(go.Scatter(
            x=df_daily['date'],
            y=df_daily['conversions'],
            mode='lines+markers',
            name='Conversions',
            line=dict(color='green'),
            yaxis='y2'
        ))
        
        fig_trends.update_layout(
            title="Daily Performance Tracking",
            xaxis_title="Date",
            yaxis_title="Conversations",
            yaxis2=dict(title="Conversions", overlaying='y', side='right'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trends, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Lead Score Distribution")
        
        # Simulate lead score distribution
        lead_scores = analytics.get('engagement_quality_scores', [7.2, 8.1, 6.8, 9.2, 7.9])
        
        fig_scores = px.histogram(
            x=lead_scores,
            nbins=10,
            title="Engagement Quality Scores",
            labels={'x': 'Quality Score (1-10)', 'y': 'Frequency'}
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        
        avg_score = sum(lead_scores) / len(lead_scores)
        if avg_score >= 8:
            st.success(f"✅ High Quality: {avg_score:.1f}/10 average score")
        elif avg_score >= 6:
            st.info(f"📊 Good Quality: {avg_score:.1f}/10 average score")
        else:
            st.warning(f"⚠️ Low Quality: {avg_score:.1f}/10 - Review response strategy")
    
    # Business Insights
    st.markdown("---")
    st.subheader("💡 Business Insights & Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🎯 Conversion Optimization:**
        - Current rate: {:.1f}%
        - Monthly projection: {} meetings
        - Revenue potential: £{}K
        """.format(
            analytics['conversion_rate'],
            int(analytics['conversions_achieved'] * 4.3),  # Monthly estimate
            int(analytics['conversions_achieved'] * 4.3 * 15)  # £15K avg project value
        ))
    
    with col2:
        st.markdown("""
        **💬 Engagement Quality:**
        - Quality conversations: {}%
        - Avg session: {:.1f} minutes
        - Drop-off reduction potential: 25%
        """.format(
            int((analytics['quality_conversations'] / analytics['total_conversations']) * 100),
            analytics['avg_session_duration_minutes']
        ))
    
    with col3:
        st.markdown("""
        **🚀 Optimization Opportunities:**
        - Improve early engagement hooks
        - Reduce 1-2 interaction drop-offs
        - Enhance conversion calls-to-action
        """)
    
    # Action Items
    st.markdown("---")
    st.subheader("✅ Recommended Actions")
    
    if analytics['conversion_rate'] < 25:
        st.warning("📞 **PRIORITY**: Conversion rate below target - Review engagement conversion stage responses")
    
    if (analytics['quality_conversations'] / analytics['total_conversations']) < 0.6:
        st.warning("💬 **PRIORITY**: Too many short conversations - Enhance engagement hooks in early responses")
    
    if analytics['avg_interactions_per_conversation'] < 4:
        st.info("🎯 **OPTIMIZE**: Add more engaging follow-up questions to extend conversations")
    
    st.success("📊 **SUCCESS**: Analytics tracking is working - Continue monitoring for optimization opportunities")

if __name__ == "__main__":
    main()