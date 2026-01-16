from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal


class ProductTechnology(BaseModel):
    product_type: Literal["Web", "Mobile", "SaaS", "Hardware", "AI"]
    current_features: List[str] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    data_strategy: Literal["None", "User Data", "External APIs", "Proprietary"]
    ai_usage: Literal["None", "Planned", "In Production"]
    tech_challenges: str = ""


class MarketingGrowth(BaseModel):
    current_marketing_channels: List[str] = Field(default_factory=list)
    monthly_users: int = 0
    customer_acquisition_cost: str = ""
    retention_strategy: str = ""
    growth_problems: str = ""


class TeamOrganization(BaseModel):
    team_size: int = 0
    founder_roles: List[str] = Field(default_factory=list)
    hiring_plan_next_3_months: str = ""
    org_challenges: str = ""


class CompetitionMarket(BaseModel):
    known_competitors: List[str] = Field(default_factory=list)
    unique_advantage: str = ""
    pricing_model: str = ""
    market_risks: str = ""


class FinanceRunway(BaseModel):
    monthly_burn: str = ""
    current_revenue: str = ""
    funding_status: Literal["Bootstrapped", "Angel", "Seed", "Series A"]
    runway_months: str = ""
    financial_concerns: str = ""


class StartupInput(BaseModel):
    product_technology: ProductTechnology
    marketing_growth: MarketingGrowth
    team_organization: TeamOrganization
    competition_market: CompetitionMarket
    finance_runway: FinanceRunway


# Structured output models for LLM responses - One for each agent type
class MarketingSuggestions(BaseModel):
    """Structured output for marketing advisor"""
    suggestions: List[str] = Field(
        description="List of 3-7 actionable marketing suggestions",
        min_length=3,  # Relaxed from 5 to 3
        max_length=7
    )
    
    @field_validator('suggestions')
    @classmethod
    def validate_suggestions(cls, v):
        if not v:
            raise ValueError("Suggestions list cannot be empty")
        # Filter out empty strings
        v = [s.strip() for s in v if s and s.strip()]
        if len(v) < 3:
            raise ValueError(f"Need at least 3 suggestions, got {len(v)}")
        return v


class TechSuggestions(BaseModel):
    """Structured output for tech lead"""
    suggestions: List[str] = Field(
        description="List of 3-7 actionable technical suggestions",
        min_length=3,
        max_length=7
    )
    
    @field_validator('suggestions')
    @classmethod
    def validate_suggestions(cls, v):
        if not v:
            raise ValueError("Suggestions list cannot be empty")
        v = [s.strip() for s in v if s and s.strip()]
        if len(v) < 3:
            raise ValueError(f"Need at least 3 suggestions, got {len(v)}")
        return v


class OrgHRSuggestions(BaseModel):
    """Structured output for org/HR strategist"""
    suggestions: List[str] = Field(
        description="List of 3-7 actionable organizational/HR suggestions",
        min_length=3,
        max_length=7
    )
    
    @field_validator('suggestions')
    @classmethod
    def validate_suggestions(cls, v):
        if not v:
            raise ValueError("Suggestions list cannot be empty")
        v = [s.strip() for s in v if s and s.strip()]
        if len(v) < 3:
            raise ValueError(f"Need at least 3 suggestions, got {len(v)}")
        return v


class CompetitiveSuggestions(BaseModel):
    """Structured output for competitive analyst"""
    suggestions: List[str] = Field(
        description="List of 3-7 actionable competitive strategy suggestions",
        min_length=3,
        max_length=7
    )
    
    @field_validator('suggestions')
    @classmethod
    def validate_suggestions(cls, v):
        if not v:
            raise ValueError("Suggestions list cannot be empty")
        v = [s.strip() for s in v if s and s.strip()]
        if len(v) < 3:
            raise ValueError(f"Need at least 3 suggestions, got {len(v)}")
        return v


class FinanceSuggestions(BaseModel):
    """Structured output for finance advisor"""
    suggestions: List[str] = Field(
        description="List of 3-7 actionable financial suggestions",
        min_length=3,
        max_length=7
    )
    
    @field_validator('suggestions')
    @classmethod
    def validate_suggestions(cls, v):
        if not v:
            raise ValueError("Suggestions list cannot be empty")
        v = [s.strip() for s in v if s and s.strip()]
        if len(v) < 3:
            raise ValueError(f"Need at least 3 suggestions, got {len(v)}")
        return v


# Legacy model for backward compatibility
class AgentSuggestions(BaseModel):
    """Structured output for agent suggestions"""
    agent_name: str = Field(description="Name of the agent providing suggestions")
    suggestions: List[str] = Field(
        description="List of 5-7 actionable suggestions",
        min_length=5,
        max_length=7
    )


class AnalysisResults(BaseModel):
    """Complete analysis results from all agents"""
    marketing_suggestions: List[str] = Field(default_factory=list)
    tech_suggestions: List[str] = Field(default_factory=list)
    org_hr_suggestions: List[str] = Field(default_factory=list)
    competitive_suggestions: List[str] = Field(default_factory=list)
    finance_suggestions: List[str] = Field(default_factory=list)


# API Request/Response models
class AnalysisRequest(BaseModel):
    startup_data: StartupInput


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str


class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str
    submitted_at: str
    completed_at: Optional[str] = None
    result: Optional[AnalysisResults] = None
    error: Optional[str] = None
