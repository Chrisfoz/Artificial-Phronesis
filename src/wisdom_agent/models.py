"""
Data models for the Wisdom Framework Guide Agent.
"""

from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgentMode(str, Enum):
    """Hard-separated agent modes - never mix implicitly."""
    WISDOM_ANALYSIS = "wisdom_analysis"  # Default: SD-WISE trait analysis
    SELF_EVALUATION = "self_evaluation"  # Questionnaire-style wisdom assessment
    IMPLEMENTATION = "implementation"    # Architecture/deployment guidance


class WisdomTrait(str, Enum):
    """The 9 SD-WISE wisdom traits (Jeste et al.)."""
    SELF_REFLECTION = "Self-reflection"
    PROSOCIAL_BEHAVIORS = "Prosocial Behaviors"
    EMOTIONAL_REGULATION = "Emotional Regulation"
    ACCEPTANCE_OF_DIVERSE_PERSPECTIVES = "Acceptance of Diverse Perspectives"
    DECISIVENESS = "Decisiveness"
    SOCIAL_ADVISING = "Social Advising"
    SPIRITUALITY = "Spirituality"
    OPENNESS_TO_NEW_EXPERIENCES = "Openness to New Experiences"
    SENSE_OF_HUMOR = "Sense of Humor"


class TraitAnalysis(BaseModel):
    """Analysis of a single wisdom trait."""
    trait: WisdomTrait
    score: Optional[int] = Field(None, ge=1, le=5, description="1-5 score if applicable")
    analysis: str = Field(..., description="Detailed analysis of this trait in context")
    evidence: List[str] = Field(default_factory=list, description="Evidence from user's situation")
    suggestions: List[str] = Field(default_factory=list, description="Actionable suggestions")


class SDWISEAnalysis(BaseModel):
    """Complete SD-WISE wisdom framework analysis."""
    context_summary: str = Field(..., description="Brief summary of the situation being analyzed")
    is_personal: bool = Field(..., description="Whether this is a personal or group context")
    traits: List[TraitAnalysis] = Field(..., description="Analysis of all 9 SD-WISE traits")
    overall_insights: str = Field(..., description="Synthesized wisdom insights")
    frameworks_used: List[str] = Field(default=["SD-WISE (Jeste et al.)"], description="Frameworks applied")
    
    def to_table_format(self) -> Dict[str, Any]:
        """Convert to tabular format for display."""
        return {
            "context": self.context_summary,
            "traits": [
                {
                    "trait": t.trait.value,
                    "score": t.score,
                    "analysis": t.analysis,
                    "evidence": t.evidence,
                    "suggestions": t.suggestions
                }
                for t in self.traits
            ],
            "insights": self.overall_insights
        }


class Reflection(BaseModel):
    """A user-authored reflective insight (opt-in memory)."""
    id: str = Field(..., description="Unique reflection ID")
    user_id: str = Field(..., description="User who created this reflection")
    content: str = Field(..., description="The reflective insight")
    context: Optional[str] = Field(None, description="Original situation/context")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    is_private: bool = Field(default=True, description="Whether this reflection is private")


class Conversation(BaseModel):
    """A conversation session with the Wisdom Agent."""
    id: str = Field(..., description="Unique conversation ID")
    user_id: Optional[str] = Field(None, description="User ID if authenticated")
    mode: AgentMode = Field(default=AgentMode.WISDOM_ANALYSIS)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    has_analysis: bool = Field(default=False)
    saved_reflection_id: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SelfEvaluationQuestion(BaseModel):
    """A single self-evaluation question."""
    id: str
    trait: WisdomTrait
    question: str
    reverse_scored: bool = Field(default=False, description="Whether higher scores indicate lower wisdom")


class SelfEvaluationResponse(BaseModel):
    """User response to a self-evaluation question."""
    question_id: str
    score: int = Field(..., ge=1, le=5)


class SelfEvaluationResult(BaseModel):
    """Results from the self-evaluation questionnaire."""
    id: str
    user_id: str
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    trait_scores: Dict[str, float] = Field(..., description="Average score per trait (1-5)")
    overall_score: float = Field(..., description="Overall wisdom score (1-5)")
    interpretation: str = Field(..., description="Plain-language interpretation")
    strengths: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)
    
    def to_radar_data(self) -> Dict[str, Any]:
        """Convert to format suitable for radar chart visualization."""
        return {
            "labels": [t.value for t in WisdomTrait],
            "datasets": [{
                "label": "Your Wisdom Profile",
                "data": [self.trait_scores.get(t.value, 3) for t in WisdomTrait],
                "fill": True,
                "backgroundColor": "rgba(43, 124, 233, 0.2)",
                "borderColor": "rgb(43, 124, 233)",
                "pointBackgroundColor": "rgb(43, 124, 233)",
                "pointBorderColor": "#fff",
                "pointHoverBackgroundColor": "#fff",
                "pointHoverBorderColor": "rgb(43, 124, 233)"
            }]
        }


class WisdomProfile(BaseModel):
    """Aggregated wisdom profile for a user (opt-in, never raw chat logs)."""
    user_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    evaluation_results: List[str] = Field(default_factory=list, description="IDs of self-evaluations")
    trait_tendencies: Dict[str, float] = Field(default_factory=dict)
    reflection_count: int = Field(default=0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ImplementationGuidance(BaseModel):
    """Implementation guidance response."""
    architecture_overview: str
    frontend_stack: Dict[str, Any]
    backend_stack: Dict[str, Any]
    ai_layer: Dict[str, Any]
    deployment_options: List[Dict[str, Any]]
    security_considerations: List[str]
    next_steps: List[str]
