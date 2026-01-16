"""
Test script for the Board Panel API with improved error handling
"""
import requests
import json
import time
from datetime import datetime

# API configuration
BASE_URL = "http://localhost:8002"

# Sample startup data for testing
test_startup = {
    "startup_data": {
        "product_technology": {
            "product_type": "SaaS",
            "current_features": ["User dashboard", "Analytics", "API access"],
            "tech_stack": ["React", "Node.js", "PostgreSQL", "AWS"],
            "data_strategy": "User Data",
            "ai_usage": "Planned",
            "tech_challenges": "Scaling database queries, need better caching"
        },
        "marketing_growth": {
            "current_marketing_channels": ["SEO", "Content Marketing", "LinkedIn"],
            "monthly_users": 1500,
            "customer_acquisition_cost": "$150",
            "retention_strategy": "Email nurture campaigns",
            "growth_problems": "High churn rate, need better onboarding"
        },
        "team_organization": {
            "team_size": 8,
            "founder_roles": ["CEO", "CTO", "VP Product"],
            "hiring_plan_next_3_months": "Hire 2 engineers, 1 sales rep",
            "org_challenges": "Need better communication between teams"
        },
        "competition_market": {
            "known_competitors": ["Competitor A", "Competitor B"],
            "unique_advantage": "Better UX and faster setup time",
            "pricing_model": "$99/month per user",
            "market_risks": "New entrants with lower prices"
        },
        "finance_runway": {
            "monthly_burn": "$50,000",
            "current_revenue": "$25,000",
            "funding_status": "Seed",
            "runway_months": "10",
            "financial_concerns": "Need to reach profitability soon"
        }
    }
}


def test_api():
    print("="*80)
    print("TESTING BOARD PANEL API WITH IMPROVED ERROR HANDLING")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Submit analysis
    print("Step 1: Submitting analysis request...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/analyze",
            json=test_startup,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        result = response.json()
        
        analysis_id = result["analysis_id"]
        print(f"✓ Analysis submitted successfully!")
        print(f"  Analysis ID: {analysis_id}")
        print(f"  Status: {result['status']}")
        print(f"  Message: {result['message']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error submitting analysis: {e}")
        return
    
    # Step 2: Poll for results
    print("Step 2: Waiting for analysis to complete...")
    print("(This will take 2-3 minutes due to rate limiting)")
    print()
    
    max_attempts = 60  # 5 minutes max
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{BASE_URL}/api/results/{analysis_id}")
            response.raise_for_status()
            status_data = response.json()
            
            current_status = status_data["status"]
            
            # Clear line and print status
            print(f"  [{datetime.now().strftime('%H:%M:%S')}] Status: {current_status}", end="")
            
            if current_status == "completed":
                print("\n")
                print("="*80)
                print("✓ ANALYSIS COMPLETED SUCCESSFULLY!")
                print("="*80)
                
                result = status_data["result"]
                
                # Display results
                categories = [
                    ("Marketing Suggestions", result["marketing_suggestions"]),
                    ("Tech Suggestions", result["tech_suggestions"]),
                    ("Org/HR Suggestions", result["org_hr_suggestions"]),
                    ("Competitive Suggestions", result["competitive_suggestions"]),
                    ("Finance Suggestions", result["finance_suggestions"])
                ]
                
                total_suggestions = 0
                for category, suggestions in categories:
                    count = len(suggestions)
                    total_suggestions += count
                    print(f"\n{category}: {count} suggestions")
                    print("-" * 60)
                    for i, suggestion in enumerate(suggestions, 1):
                        print(f"{i}. {suggestion}")
                
                print()
                print("="*80)
                print(f"Total suggestions: {total_suggestions}")
                print(f"Completed at: {status_data['completed_at']}")
                print("="*80)
                return
            
            elif current_status == "failed":
                print("\n")
                print("="*80)
                print("✗ ANALYSIS FAILED")
                print("="*80)
                print(f"Error: {status_data.get('error', 'Unknown error')}")
                print("="*80)
                return
            
            else:
                # Still processing
                print(f" (attempt {attempt + 1}/{max_attempts})", end="\r")
                time.sleep(5)
                attempt += 1
                
        except requests.exceptions.RequestException as e:
            print(f"\n✗ Error checking status: {e}")
            time.sleep(5)
            attempt += 1
    
    print("\n")
    print("="*80)
    print("⚠ Timeout waiting for analysis to complete")
    print("="*80)


if __name__ == "__main__":
    test_api()
