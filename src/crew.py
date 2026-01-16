from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
import os
from dotenv import load_dotenv
from models import (
    MarketingSuggestions,
    TechSuggestions,
    OrgHRSuggestions,
    CompetitiveSuggestions,
    FinanceSuggestions
)

load_dotenv()


@CrewBase
class BoardPanelCrew:
    """BoardPanel Startup Advisory Crew - SUGGESTIONS ONLY"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        groq_api_key = os.getenv('GROQ_API_KEY', '')
        groq_model = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
        
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        os.environ['GROQ_API_KEY'] = groq_api_key
        
        # Token configuration:
        # - 8000 TPM rate limit / 5 agents = 1600 tokens per agent
        # - Increased to 1200 output tokens for better completion
        # - With ~400 input tokens, total ~1600 per task
        # - Lower temperature for more consistent JSON output
        self.llm = LLM(
            model=f"groq/{groq_model}",
            api_key=groq_api_key,
            temperature=0.3,  # Lower temperature for more consistent JSON
            max_tokens=1200,  # Increased from 800 for better completion
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        print(f"Initialized LLM: {groq_model} with max_tokens=1200, temperature=0.3")
        
        super(BoardPanelCrew, self).__init__()

    @agent
    def marketing_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['marketing_advisor'],
            llm=self.llm,
            verbose=True,
            max_iter=3,  # Limit iterations to stay within token budget
        )

    @agent
    def tech_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['tech_lead'],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

    @agent
    def org_hr_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['org_hr_strategist'],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

    @agent
    def competitive_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitive_analyst'],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

    @agent
    def finance_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['finance_advisor'],
            llm=self.llm,
            verbose=True,
            max_iter=3,
        )

    @task
    def marketing_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['marketing_analysis_task'],
            agent=self.marketing_advisor(),
            output_pydantic=MarketingSuggestions,
        )

    @task
    def tech_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['tech_analysis_task'],
            agent=self.tech_lead(),
            output_pydantic=TechSuggestions,
        )

    @task
    def org_hr_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['org_hr_analysis_task'],
            agent=self.org_hr_strategist(),
            output_pydantic=OrgHRSuggestions,
        )

    @task
    def competitive_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['competitive_analysis_task'],
            agent=self.competitive_analyst(),
            output_pydantic=CompetitiveSuggestions,
        )

    @task
    def finance_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['finance_analysis_task'],
            agent=self.finance_advisor(),
            output_pydantic=FinanceSuggestions,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the BoardPanel crew with sequential execution and rate limit management."""
        # Explicitly define task order to ensure consistent index-based mapping
        ordered_tasks = [
            self.marketing_analysis_task(),
            self.tech_analysis_task(),
            self.org_hr_analysis_task(),
            self.competitive_analysis_task(),
            self.finance_analysis_task()
        ]
        
        print(f"\nCreated crew with {len(ordered_tasks)} tasks in sequential order")
        print("Task order: Marketing → Tech → Org/HR → Competitive → Finance\n")
        
        return Crew(
            agents=self.agents,
            tasks=ordered_tasks,
            process=Process.sequential,
            verbose=True,
            # Removed max_rpm to rely on our custom rate limiting
        )
