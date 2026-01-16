"""
Quick test to verify Pydantic structured outputs work correctly
"""
from src.models import (
    ProductTechnology,
    MarketingGrowth,
    TeamOrganization,
    CompetitionMarket,
    FinanceRunway,
    StartupInput
)
from src.main import prepare_inputs
from src.crew import BoardPanelCrew

def test_structured_outputs():
    """Test that each task returns proper Pydantic output"""
    
    # Create test data
    test_data = StartupInput(
        product_technology=ProductTechnology(
            product_type="SaaS",
            current_features=["Analytics", "API"],
            tech_stack=["React", "Node.js"],
            data_strategy="User Data",
            ai_usage="Planned",
            tech_challenges="Scaling issues"
        ),
        marketing_growth=MarketingGrowth(
            current_marketing_channels=["SEO", "LinkedIn"],
            monthly_users=1000,
            customer_acquisition_cost="$50",
            retention_strategy="Email campaigns",
            growth_problems="High churn"
        ),
        team_organization=TeamOrganization(
            team_size=5,
            founder_roles=["CEO", "CTO"],
            hiring_plan_next_3_months="2 engineers",
            org_challenges="Remote coordination"
        ),
        competition_market=CompetitionMarket(
            known_competitors=["Competitor A"],
            unique_advantage="AI-powered",
            pricing_model="Freemium",
            market_risks="Large competitors"
        ),
        finance_runway=FinanceRunway(
            monthly_burn="$50,000",
            current_revenue="$10,000 MRR",
            funding_status="Seed",
            runway_months="12",
            financial_concerns="Need better unit economics"
        )
    )
    
    print("="*80)
    print("TESTING PYDANTIC STRUCTURED OUTPUTS")
    print("="*80)
    
    # Prepare inputs
    inputs = prepare_inputs(test_data)
    
    # Run crew
    print("\nRunning BoardPanel Crew...")
    crew = BoardPanelCrew().crew()
    result = crew.kickoff(inputs=inputs)
    
    # Verify outputs
    print("\n" + "="*80)
    print("VERIFYING PYDANTIC OUTPUTS")
    print("="*80)
    
    tasks_output = result.tasks_output
    
    for i, task in enumerate(tasks_output):
        task_names = ["Marketing", "Tech", "Org/HR", "Competitive", "Finance"]
        print(f"\n{task_names[i]} Task:")
        
        if hasattr(task, 'pydantic'):
            print(f"  ✅ Has Pydantic output")
            print(f"  ✅ Type: {type(task.pydantic).__name__}")
            print(f"  ✅ Suggestions count: {len(task.pydantic.suggestions)}")
            
            # Show first suggestion
            if task.pydantic.suggestions:
                print(f"  ✅ Sample: {task.pydantic.suggestions[0][:80]}...")
        else:
            print(f"  ❌ NO PYDANTIC OUTPUT!")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    # Check if org/HR has suggestions
    if len(tasks_output) > 2 and hasattr(tasks_output[2], 'pydantic'):
        if len(tasks_output[2].pydantic.suggestions) == 5:
            print("\n✅ SUCCESS: Org/HR task has exactly 5 suggestions!")
        else:
            print(f"\n⚠️  WARNING: Org/HR has {len(tasks_output[2].pydantic.suggestions)} suggestions (expected 5)")
    else:
        print("\n❌ FAIL: Org/HR task has no Pydantic output!")

if __name__ == "__main__":
    test_structured_outputs()
