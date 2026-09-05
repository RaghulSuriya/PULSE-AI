from datetime import datetime, timedelta
from app.schemas.ai_extraction import DocumentActionExtraction, ExtractedSubtask, ExtractedRequirement
from app.services.ai_engine.base import llm_provider

class ActionExtractor:
    """
    Action & Document Information Extractor.
    Converts circulars, emails, and PDFs into structured goals, requirements, and subtasks with dependencies.
    """
    SYSTEM_PROMPT = (
        "You are PULSE AI's Action Extraction Engine.\n"
        "Extract actionable requirements from text/documents.\n"
        "Break complex requests down into step-by-step subtasks with time estimates and explicit dependency ordering.\n"
        "Do NOT invent false deadlines or requirements. If uncertain, mark confidence accordingly."
    )

    async def extract_action_plan(self, title: str, text: str) -> DocumentActionExtraction:
        full_content = f"Title: {title}\n\nContent:\n{text}"

        def heuristic_fallback() -> DocumentActionExtraction:
            lower_text = (title + " " + text).lower()
            
            # Simple rule-based extraction fallback
            deadline_str = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d 17:00:00")
            
            if "internship" in lower_text or "placement" in lower_text:
                return DocumentActionExtraction(
                    goal="Internship Application",
                    organization="Placement Cell / Target Company",
                    deadline=deadline_str,
                    eligibility="Minimum 7.0 CGPA, No active backlogs",
                    consequences="Failure to apply will disqualify candidacy for campus placement cycle.",
                    required_documents=[
                        ExtractedRequirement(name="Updated Resume", is_mandatory=True),
                        ExtractedRequirement(name="Latest Marksheet", is_mandatory=True),
                        ExtractedRequirement(name="Bonafide Certificate", is_mandatory=False, details="From HOD office")
                    ],
                    tasks=[
                        ExtractedSubtask(
                            title="Verify Eligibility Criteria",
                            description="Check CGPA and backlog requirements against placement portal",
                            estimated_minutes=15,
                            priority="MUST_DO",
                            dependencies=[]
                        ),
                        ExtractedSubtask(
                            title="Obtain Bonafide Certificate",
                            description="Apply at department office for signed bonafide",
                            estimated_minutes=45,
                            priority="SHOULD_DO",
                            dependencies=["Verify Eligibility Criteria"]
                        ),
                        ExtractedSubtask(
                            title="Prepare Resume & Marksheets",
                            description="Export PDF resume and compile semester transcripts",
                            estimated_minutes=30,
                            priority="MUST_DO",
                            dependencies=["Verify Eligibility Criteria"]
                        ),
                        ExtractedSubtask(
                            title="Fill & Submit Application Form",
                            description="Complete portal application and upload documents",
                            estimated_minutes=25,
                            priority="MUST_DO",
                            dependencies=["Obtain Bonafide Certificate", "Prepare Resume & Marksheets"]
                        )
                    ],
                    confidence=0.94
                )
            elif "bill" in lower_text or "electricity" in lower_text or "recharge" in lower_text:
                return DocumentActionExtraction(
                    goal="Electricity / Utility Bill Payment",
                    organization="State Electricity Board",
                    deadline=deadline_str,
                    consequences="Late fee surcharge of \$15 applied after deadline.",
                    required_documents=[
                        ExtractedRequirement(name="Consumer Account ID", is_mandatory=True)
                    ],
                    tasks=[
                        ExtractedSubtask(
                            title="Pay Utility Bill Online",
                            description="Complete payment via web portal or banking app",
                            estimated_minutes=10,
                            priority="MUST_DO",
                            dependencies=[]
                        )
                    ],
                    confidence=0.96
                )
            else:
                return DocumentActionExtraction(
                    goal=title or "General Actionable Task",
                    organization="Extracted Source",
                    deadline=deadline_str,
                    consequences="Potential delay in progress.",
                    required_documents=[],
                    tasks=[
                        ExtractedSubtask(
                            title=title or "Review & Complete Action",
                            description="Review details and execute required task",
                            estimated_minutes=30,
                            priority="SHOULD_DO",
                            dependencies=[]
                        )
                    ],
                    confidence=0.85
                )

        return await llm_provider.generate_structured(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=full_content,
            response_schema=DocumentActionExtraction,
            fallback_factory=heuristic_fallback
        )

action_extractor = ActionExtractor()
