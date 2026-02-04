"""
Wisdom Framework Guide Agent - Core implementation.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator

from .models import (
    AgentMode,
    SDWISEAnalysis,
    TraitAnalysis,
    WisdomTrait,
    Conversation,
    Reflection,
    SelfEvaluationResult,
    SelfEvaluationResponse,
)
from .prompts import (
    WISDOM_ADVISOR_SYSTEM_PROMPT,
    SELF_EVALUATION_SYSTEM_PROMPT,
    IMPLEMENTATION_GUIDANCE_PROMPT,
    SD_WISE_TRAIT_DESCRIPTIONS,
    SELF_EVALUATION_QUESTIONS,
)

logger = logging.getLogger(__name__)


class WisdomAgent:
    """
    Wisdom Framework Guide Agent - A guided wisdom-oriented advisor.
    
    Supports three hard-separated modes:
    - WISDOM_ANALYSIS: SD-WISE trait analysis (default)
    - SELF_EVALUATION: Questionnaire-style wisdom assessment
    - IMPLEMENTATION: Architecture/deployment guidance
    """
    
    def __init__(self, llm_client=None, memory_store=None):
        """
        Initialize the Wisdom Agent.
        
        Args:
            llm_client: LLM client for generating responses (OpenAI, Anthropic, etc.)
            memory_store: Optional storage for conversations and reflections
        """
        self.llm_client = llm_client
        self.memory_store = memory_store
        self.active_conversations: Dict[str, Conversation] = {}
        
    def create_conversation(self, user_id: Optional[str] = None, mode: AgentMode = AgentMode.WISDOM_ANALYSIS) -> Conversation:
        """Create a new conversation session."""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            mode=mode,
            messages=[{
                "role": "system",
                "content": self._get_system_prompt(mode),
                "timestamp": datetime.utcnow().isoformat()
            }]
        )
        self.active_conversations[conversation.id] = conversation
        return conversation
    
    def _get_system_prompt(self, mode: AgentMode) -> str:
        """Get the appropriate system prompt for the mode."""
        prompts = {
            AgentMode.WISDOM_ANALYSIS: WISDOM_ADVISOR_SYSTEM_PROMPT,
            AgentMode.SELF_EVALUATION: SELF_EVALUATION_SYSTEM_PROMPT,
            AgentMode.IMPLEMENTATION: IMPLEMENTATION_GUIDANCE_PROMPT
        }
        return prompts.get(mode, WISDOM_ADVISOR_SYSTEM_PROMPT)
    
    async def chat(self, conversation_id: str, message: str) -> Dict[str, Any]:
        """
        Process a chat message and return a response.
        
        Args:
            conversation_id: Active conversation ID
            message: User message
            
        Returns:
            Response dictionary with content and metadata
        """
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Add user message
        conversation.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Generate response based on mode
        if conversation.mode == AgentMode.WISDOM_ANALYSIS:
            response = await self._generate_wisdom_analysis(conversation, message)
        elif conversation.mode == AgentMode.SELF_EVALUATION:
            response = await self._generate_evaluation_response(conversation, message)
        elif conversation.mode == AgentMode.IMPLEMENTATION:
            response = await self._generate_implementation_guidance(conversation, message)
        else:
            response = await self._generate_default_response(conversation, message)
        
        # Add assistant message
        conversation.messages.append({
            "role": "assistant",
            "content": response.get("content", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": response.get("metadata", {})
        })
        
        conversation.updated_at = datetime.utcnow()
        
        return response
    
    async def chat_stream(self, conversation_id: str, message: str) -> AsyncGenerator[str, None]:
        """
        Stream a chat response.
        
        Args:
            conversation_id: Active conversation ID
            message: User message
            
        Yields:
            Chunks of the response
        """
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            yield json.dumps({"error": f"Conversation {conversation_id} not found"})
            return
        
        # Add user message
        conversation.messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Stream response
        full_response = ""
        metadata = {}
        
        if self.llm_client and hasattr(self.llm_client, 'chat_stream'):
            # Use LLM streaming if available
            system_prompt = self._get_system_prompt(conversation.mode)
            async for chunk in self.llm_client.chat_stream(
                system_prompt=system_prompt,
                messages=conversation.messages[:-1],
                user_message=message
            ):
                full_response += chunk
                yield json.dumps({"chunk": chunk, "done": False})
        else:
            # Fallback to non-streaming with simulated chunks
            response = await self.chat(conversation_id, message)
            full_response = response.get("content", "")
            metadata = response.get("metadata", {})
            
            # Simulate streaming by yielding words
            words = full_response.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield json.dumps({"chunk": chunk, "done": False})
        
        # Add assistant message
        conversation.messages.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        })
        
        conversation.updated_at = datetime.utcnow()
        
        yield json.dumps({"chunk": "", "done": True, "metadata": metadata})
    
    async def _generate_wisdom_analysis(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Generate a wisdom analysis response using SD-WISE framework."""
        
        # Check if this is the first message (introduction)
        if len(conversation.messages) <= 2:  # System + first user message
            return {
                "content": """Welcome to the Wisdom Framework Guide. I analyze situations through evidence-based wisdom frameworks.

**What I can help with:**
- Analyzing personal dilemmas using the SD-WISE wisdom traits
- Assessing team conflicts through the Jeste wisdom framework  
- Helping you think through decision-making processes
- Providing implementation guidance for deploying this agent

**To get started, please tell me:**
1. What situation or question would you like to analyze?
2. Is this a **personal decision/inner conflict** OR a **group context** (team, family, organization)?

I'll then provide a structured analysis across all 9 wisdom traits from the SD-WISE framework.""",
                "metadata": {"type": "introduction", "mode": "wisdom_analysis"}
            }
        
        # Check if context has been clarified
        user_messages = [m["content"] for m in conversation.messages if m["role"] == "user"]
        context_clarified = any(keyword in " ".join(user_messages).lower() 
                               for keyword in ["personal", "my", "i ", "team", "group", "family", "organization", "we "])
        
        if not context_clarified and len(user_messages) < 3:
            return {
                "content": """Thank you for sharing. To provide the most relevant analysis, could you clarify:

**Is this a personal situation or a group/organizational context?**

For example:
- "This is a personal decision I'm facing..."
- "This is about a conflict in my team..."
- "I'm trying to decide whether to..."""",
                "metadata": {"type": "clarification", "mode": "wisdom_analysis"}
            }
        
        # Generate structured analysis
        analysis = await self._create_sdwise_analysis(message, conversation)
        
        # Format as table/markdown
        content = self._format_analysis_as_markdown(analysis)
        
        conversation.has_analysis = True
        
        return {
            "content": content,
            "metadata": {
                "type": "analysis",
                "mode": "wisdom_analysis",
                "analysis": analysis.dict()
            }
        }
    
    async def _create_sdwise_analysis(self, message: str, conversation: Conversation) -> SDWISEAnalysis:
        """Create a structured SD-WISE analysis."""
        
        # Determine if personal or group context
        all_content = " ".join([m["content"] for m in conversation.messages])
        is_personal = any(word in all_content.lower() for word in ["i ", "my ", "me ", "personal"])
        
        # Use LLM to generate analysis if available
        if self.llm_client and hasattr(self.llm_client, 'complete'):
            prompt = self._build_analysis_prompt(all_content, is_personal)
            try:
                response = await self.llm_client.complete(prompt)
                analysis_data = self._parse_analysis_response(response)
                return SDWISEAnalysis(**analysis_data)
            except Exception as e:
                logger.error(f"Error generating analysis with LLM: {e}")
        
        # Fallback: Generate template analysis
        return self._generate_template_analysis(message, is_personal)
    
    def _build_analysis_prompt(self, context: str, is_personal: bool) -> str:
        """Build the prompt for LLM-based analysis."""
        trait_descriptions = "\n".join([
            f"{i+1}. {trait}: {desc['definition']}"
            for i, (trait, desc) in enumerate(SD_WISE_TRAIT_DESCRIPTIONS.items())
        ])
        
        return f"""Analyze the following situation through the SD-WISE wisdom framework.

**Context:**
{context}

**Context Type:** {'Personal' if is_personal else 'Group/Organizational'}

**The 9 SD-WISE Wisdom Traits:**
{trait_descriptions}

Provide a structured analysis addressing each trait."""
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured analysis data."""
        # Simple parsing - in production, use structured output
        return {
            "context_summary": "Analysis based on provided context",
            "is_personal": True,
            "traits": [
                {
                    "trait": trait.value,
                    "analysis": "Analysis pending LLM integration",
                    "evidence": [],
                    "suggestions": []
                }
                for trait in WisdomTrait
            ],
            "overall_insights": response[:500] if response else "Analysis complete."
        }
    
    def _generate_template_analysis(self, message: str, is_personal: bool) -> SDWISEAnalysis:
        """Generate a template analysis when LLM is unavailable."""
        
        traits = []
        for trait in WisdomTrait:
            desc = SD_WISE_TRAIT_DESCRIPTIONS.get(trait.value, {})
            traits.append(TraitAnalysis(
                trait=trait,
                analysis=f"Consider how {trait.value.lower()} applies to your situation. {desc.get('definition', '')}",
                evidence=["Based on the situation described"],
                suggestions=desc.get("indicators", ["Reflect on this trait"])[:2]
            ))
        
        return SDWISEAnalysis(
            context_summary=message[:200] + "..." if len(message) > 200 else message,
            is_personal=is_personal,
            traits=traits,
            overall_insights="This situation invites reflection across multiple wisdom dimensions. Consider which traits feel most relevant to your current challenge."
        )
    
    def _format_analysis_as_markdown(self, analysis: SDWISEAnalysis) -> str:
        """Format analysis as markdown for display."""
        
        content = f"""## Wisdom Framework Analysis

### Context Summary
{analysis.context_summary}

### SD-WISE Trait Analysis

| Trait | Analysis | Suggestions |
|-------|----------|-------------|
"""
        
        for trait in analysis.traits:
            suggestions = "; ".join(trait.suggestions[:2]) if trait.suggestions else "—"
            analysis_text = trait.analysis[:100] + "..." if len(trait.analysis) > 100 else trait.analysis
            content += f"| **{trait.trait.value}** | {analysis_text} | {suggestions} |\n"
        
        content += f"""
### Overall Insights
{analysis.overall_insights}

---

**Additional Frameworks Available:**
- Self-Assessed Wisdom Scale (Webster - HERO(E))
- Three-Dimensional Wisdom Scale (Ardelt)
- Berlin Wisdom Paradigm (Baltes)
- Social Reasoning Measure (Grossmann)

Would you like me to explore any specific trait in more depth, or apply an additional framework?
"""
        
        return content
    
    async def _generate_evaluation_response(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Generate a self-evaluation response."""
        return {
            "content": "Self-evaluation mode is being initialized. Please visit the Self-Evaluation page for the full questionnaire experience.",
            "metadata": {"type": "evaluation_init", "mode": "self_evaluation"}
        }
    
    async def _generate_implementation_guidance(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Generate implementation guidance."""
        
        content = """## Implementation Guidance

### Reference Architecture

**Minimal Viable Stack (Railway-friendly):**

```
Frontend: Next.js (App Router) + Tailwind CSS
Backend: Next.js API Routes (Node.js)
Database: PostgreSQL (Railway managed)
AI Layer: OpenAI/Anthropic API
Auth: Auth.js or Clerk
Deployment: Railway (monorepo)
```

**Scalable Stack (when usage grows):**

```
Frontend: Next.js + Tailwind CSS
Backend: Express.js or FastAPI
Database: PostgreSQL + Redis (caching)
AI Layer: OpenAI/Anthropic with fallback
Queue: BullMQ for background jobs
Analytics: PostHog or OpenTelemetry
Vector Store: pgvector (PostgreSQL extension)
Mobile: SwiftUI (iOS) + shared API
```

### Key Implementation Considerations

1. **Streaming Responses**: Use Server-Sent Events (SSE) or WebSockets
2. **Rate Limiting**: Implement per-user rate limits (e.g., 50 requests/hour)
3. **Memory Management**: Store only user-authored reflections, not raw chat logs
4. **Security**: Validate inputs, use parameterized queries, implement auth middleware

### Next Steps

1. Set up Next.js project with App Router
2. Configure PostgreSQL schema for users, sessions, reflections
3. Implement streaming chat UI
4. Add authentication
5. Deploy to Railway

Would you like more detail on any specific component?"""
        
        return {
            "content": content,
            "metadata": {"type": "implementation", "mode": "implementation"}
        }
    
    async def _generate_default_response(self, conversation: Conversation, message: str) -> Dict[str, Any]:
        """Generate a default response."""
        return {
            "content": "I'm here to help you analyze situations through wisdom frameworks or provide implementation guidance. How can I assist you today?",
            "metadata": {"type": "default"}
        }
    
    def save_reflection(self, conversation_id: str, user_id: str, content: Optional[str] = None) -> Reflection:
        """Save a reflection from a conversation."""
        conversation = self.active_conversations.get(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        # Extract content from conversation if not provided
        if content is None:
            for msg in reversed(conversation.messages):
                if msg.get("metadata", {}).get("type") == "analysis":
                    content = msg["content"]
                    break
        
        if not content:
            raise ValueError("No analysis found to save as reflection")
        
        reflection = Reflection(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content,
            context=conversation.messages[1]["content"] if len(conversation.messages) > 1 else None
        )
        
        # Store if memory_store available
        if self.memory_store:
            self.memory_store.save_reflection(reflection)
        
        conversation.saved_reflection_id = reflection.id
        
        return reflection
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.active_conversations.get(conversation_id)
    
    def get_self_evaluation_questions(self) -> List[Dict[str, Any]]:
        """Get the self-evaluation questionnaire."""
        return SELF_EVALUATION_QUESTIONS
    
    def calculate_self_evaluation(self, responses: List[SelfEvaluationResponse]) -> SelfEvaluationResult:
        """Calculate self-evaluation results from responses."""
        
        # Group by trait
        trait_scores: Dict[str, List[int]] = {trait.value: [] for trait in WisdomTrait}
        
        for response in responses:
            question = next((q for q in SELF_EVALUATION_QUESTIONS if q["id"] == response.question_id), None)
            if question:
                trait_name = question["trait"]
                score = response.score
                if question.get("reverse_scored", False):
                    score = 6 - score  # Reverse 1-5 scale
                trait_scores[trait_name].append(score)
        
        # Calculate averages
        avg_scores = {
            trait: sum(scores) / len(scores) if scores else 3.0
            for trait, scores in trait_scores.items()
        }
        
        overall = sum(avg_scores.values()) / len(avg_scores) if avg_scores else 3.0
        
        # Sort for strengths and growth areas
        sorted_traits = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
        strengths = [t[0] for t in sorted_traits[:3]]
        growth_areas = [t[0] for t in sorted_traits[-3:]]
        
        # Generate interpretation
        if overall >= 4.0:
            interpretation = "You demonstrate strong wisdom tendencies across most dimensions."
        elif overall >= 3.0:
            interpretation = "You show moderate wisdom traits with room for growth."
        else:
            interpretation = "This assessment suggests opportunities for developing wisdom capacities."
        
        return SelfEvaluationResult(
            id=str(uuid.uuid4()),
            user_id="",
            trait_scores=avg_scores,
            overall_score=overall,
            interpretation=interpretation,
            strengths=strengths,
            growth_areas=growth_areas
        )
