from pydantic import BaseModel, Field
from typing import List, Optional

class EmailClassificationResult(BaseModel):
    classification: str = Field(description="ACTION_REQUIRED, INFORMATION_ONLY, PROMOTIONAL, IRRELEVANT, or UNCERTAIN")
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: List[str] = Field(description="List of bullet points explaining why this classification was assigned")
    is_actionable: bool
    urgency: str = Field(description="HIGH, MEDIUM, LOW, or NONE")
    detected_deadline: Optional[str] = None
    consequence_summary: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(default=30)

class ExtractedRequirement(BaseModel):
    name: str
    is_mandatory: bool = True
    details: Optional[str] = None

class ExtractedSubtask(BaseModel):
    title: str
    description: Optional[str] = None
    estimated_minutes: int = 30
    priority: str = "SHOULD_DO"
    deadline: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list, description="Titles of tasks this subtask depends on")

class DocumentActionExtraction(BaseModel):
    goal: str
    organization: Optional[str] = None
    deadline: Optional[str] = None
    eligibility: Optional[str] = None
    consequences: Optional[str] = None
    required_documents: List[ExtractedRequirement] = Field(default_factory=list)
    tasks: List[ExtractedSubtask] = Field(default_factory=list)
    confidence: float = 0.9

class NaturalLanguageInputRequest(BaseModel):
    text: str = Field(description="Natural language instruction, e.g., 'Study AWS tomorrow for 2 hours' or 'I couldn't finish assignment'")

class NaturalLanguageInputParsed(BaseModel):
    intent: str = Field(description="CREATE_TASK, ADD_CALENDAR_EVENT, REPLAN_DAY, MARK_COMPLETED")
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = 30
    priority: Optional[str] = "SHOULD_DO"
    target_date: Optional[str] = None
    target_time: Optional[str] = None
    is_fixed_commitment: bool = False
    replan_reason: Optional[str] = None
    confidence: float = 0.9
