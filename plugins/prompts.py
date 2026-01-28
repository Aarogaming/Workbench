"""
AAS-286: AI Prompt Templates

Provides reusable prompt templates, composition tools, and optimization
for consistent AI interaction patterns.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class PromptType(Enum):
    """Categories of prompt templates"""
    CHAT = "chat"
    COMPLETION = "completion"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"
    Q_AND_A = "q_and_a"


@dataclass
class PromptTemplate:
    """Reusable prompt template"""
    id: str
    name: str
    prompt_type: PromptType
    template_text: str
    variables: List[str]  # Placeholders like {variable_name}
    description: str = ""
    tags: List[str] = field(default_factory=list)
    version: str = "1.0"
    
    def render(self, **kwargs) -> str:
        """Fill in template variables"""
        return self.template_text.format(**kwargs)
    
    def validate_variables(self, provided_vars: Dict[str, Any]) -> bool:
        """Check if all required variables are provided"""
        provided = set(provided_vars.keys())
        required = set(self.variables)
        return required.issubset(provided)


class PromptLibrary:
    """Repository of prompt templates"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._init_default_templates()
    
    def _init_default_templates(self):
        """Initialize built-in templates"""
        templates = [
            # Chat templates
            PromptTemplate(
                id="chat_basic",
                name="Basic Chat",
                prompt_type=PromptType.CHAT,
                template_text="You are a helpful assistant.\nUser: {input}\nAssistant:",
                variables=["input"],
                description="Simple chat completion template",
                tags=["chat", "general"]
            ),
            PromptTemplate(
                id="chat_contextual",
                name="Contextual Chat",
                prompt_type=PromptType.CHAT,
                template_text=(
                    "System: {system_role}\n\nContext:\n{context}\n\n"
                    "User: {input}\nAssistant:"
                ),
                variables=["system_role", "context", "input"],
                description="Chat template with system role and contextual grounding",
                tags=["chat", "context", "system"]
            ),
            PromptTemplate(
                id="chat_clarifying_question",
                name="Clarifying Question",
                prompt_type=PromptType.CHAT,
                template_text=(
                    "You are helping clarify a request.\n"
                    "User request: {input}\n"
                    "Ask the single most important clarifying question."
                ),
                variables=["input"],
                description="Ask a focused clarifying question",
                tags=["chat", "clarify"]
            ),
            # Completion templates
            PromptTemplate(
                id="completion_rewrite_tone",
                name="Rewrite With Tone",
                prompt_type=PromptType.COMPLETION,
                template_text=(
                    "Rewrite the following text in a {tone} tone while preserving meaning:\n"
                    "{text}"
                ),
                variables=["tone", "text"],
                description="Rewrite text with a specific tone",
                tags=["completion", "rewrite"]
            ),
            PromptTemplate(
                id="completion_expand_outline",
                name="Expand Outline",
                prompt_type=PromptType.COMPLETION,
                template_text=(
                    "Expand the following outline into full prose. Target length: {length}.\n"
                    "Outline:\n{outline}"
                ),
                variables=["length", "outline"],
                description="Expand outline into prose",
                tags=["completion", "writing"]
            ),
            # Analysis templates
            PromptTemplate(
                id="analysis_code",
                name="Code Analysis",
                prompt_type=PromptType.ANALYSIS,
                template_text="""Analyze the following code for potential issues:
```
{code}
```
Focus on: {focus_areas}
Provide suggestions for improvement.""",
                variables=["code", "focus_areas"],
                description="Code review and analysis template",
                tags=["analysis", "code-review"]
            ),
            PromptTemplate(
                id="analysis_bug_triage",
                name="Bug Triage",
                prompt_type=PromptType.ANALYSIS,
                template_text=(
                    "Triage the following bug report.\n"
                    "Issue: {issue}\n"
                    "Logs: {logs}\n"
                    "Environment: {environment}\n"
                    "Provide likely cause, impact, and next steps."
                ),
                variables=["issue", "logs", "environment"],
                description="Bug triage and root cause hints",
                tags=["analysis", "debugging"]
            ),
            PromptTemplate(
                id="analysis_root_cause",
                name="Root Cause Analysis",
                prompt_type=PromptType.ANALYSIS,
                template_text=(
                    "Perform a root cause analysis.\n"
                    "Symptoms: {symptoms}\n"
                    "Context: {context}\n"
                    "List probable causes and evidence needed to confirm."
                ),
                variables=["symptoms", "context"],
                description="Root cause analysis template",
                tags=["analysis", "debugging"]
            ),
            PromptTemplate(
                id="analysis_security_review",
                name="Security Review",
                prompt_type=PromptType.ANALYSIS,
                template_text=(
                    "Review the following code for security risks.\n"
                    "Threat model: {threat_model}\n"
                    "Code:\n{code}\n"
                    "Identify vulnerabilities and mitigations."
                ),
                variables=["threat_model", "code"],
                description="Security audit template",
                tags=["analysis", "security"]
            ),
            PromptTemplate(
                id="analysis_performance",
                name="Performance Analysis",
                prompt_type=PromptType.ANALYSIS,
                template_text=(
                    "Analyze performance issues in the code below.\n"
                    "Constraints: {constraints}\n"
                    "Code:\n{code}\n"
                    "Provide bottlenecks and optimization ideas."
                ),
                variables=["constraints", "code"],
                description="Performance analysis template",
                tags=["analysis", "performance"]
            ),
            # Generation templates
            PromptTemplate(
                id="generate_unit_tests",
                name="Generate Unit Tests",
                prompt_type=PromptType.GENERATION,
                template_text=(
                    "Generate {framework} unit tests for the following code.\n"
                    "Code:\n{code}\n"
                    "Focus on edge cases and error handling."
                ),
                variables=["framework", "code"],
                description="Unit test generation template",
                tags=["generation", "testing"]
            ),
            PromptTemplate(
                id="generate_docstring",
                name="Generate Docstring",
                prompt_type=PromptType.GENERATION,
                template_text=(
                    "Write a docstring for the following function.\n"
                    "Signature: {function_signature}\n"
                    "Behavior: {behavior}"
                ),
                variables=["function_signature", "behavior"],
                description="Docstring generation template",
                tags=["generation", "documentation"]
            ),
            PromptTemplate(
                id="generate_api_docs",
                name="Generate API Docs",
                prompt_type=PromptType.GENERATION,
                template_text=(
                    "Create API documentation for the module below.\n"
                    "Audience: {audience}\n"
                    "Module:\n{module}"
                ),
                variables=["audience", "module"],
                description="API documentation template",
                tags=["generation", "documentation"]
            ),
            PromptTemplate(
                id="generate_release_notes",
                name="Generate Release Notes",
                prompt_type=PromptType.GENERATION,
                template_text=(
                    "Draft release notes for version {version}.\n"
                    "Changes:\n{changes}\n"
                    "Group by features, fixes, and breaking changes."
                ),
                variables=["version", "changes"],
                description="Release notes template",
                tags=["generation", "release"]
            ),
            PromptTemplate(
                id="generate_brainstorm",
                name="Brainstorm Ideas",
                prompt_type=PromptType.GENERATION,
                template_text=(
                    "Brainstorm {count} ideas for the following problem.\n"
                    "Problem: {problem}\n"
                    "Constraints: {constraints}"
                ),
                variables=["count", "problem", "constraints"],
                description="Idea generation template",
                tags=["generation", "brainstorm"]
            ),
            PromptTemplate(
                id="generate_sql",
                name="Generate SQL Query",
                prompt_type=PromptType.GENERATION,
                template_text=(
                    "Given the database schema:\n{schema}\n"
                    "Write a SQL query to answer: {question}"
                ),
                variables=["schema", "question"],
                description="SQL query generation template",
                tags=["generation", "data"]
            ),
            # Summarization templates
            PromptTemplate(
                id="summarize_text",
                name="Text Summarization",
                prompt_type=PromptType.SUMMARIZATION,
                template_text="""Summarize the following text in {max_sentences} sentences:
{text}""",
                variables=["text", "max_sentences"],
                description="Text summarization template",
                tags=["summarization"]
            ),
            PromptTemplate(
                id="summarize_meeting",
                name="Meeting Summary",
                prompt_type=PromptType.SUMMARIZATION,
                template_text=(
                    "Summarize the meeting transcript for {audience}.\n"
                    "Transcript:\n{transcript}\n"
                    "Include decisions, action items, and owners."
                ),
                variables=["audience", "transcript"],
                description="Meeting notes summarization template",
                tags=["summarization", "meeting"]
            ),
            PromptTemplate(
                id="summarize_diff",
                name="Diff Summary",
                prompt_type=PromptType.SUMMARIZATION,
                template_text=(
                    "Summarize the code diff below.\n"
                    "Highlight: {highlights}\n"
                    "Diff:\n{diff}"
                ),
                variables=["highlights", "diff"],
                description="Pull request diff summary template",
                tags=["summarization", "code-review"]
            ),
            # Classification templates
            PromptTemplate(
                id="classify_intent",
                name="Intent Classification",
                prompt_type=PromptType.CLASSIFICATION,
                template_text=(
                    "Classify the user's intent.\n"
                    "Utterance: {utterance}\n"
                    "Valid labels: {labels}\n"
                    "Return the best label."
                ),
                variables=["utterance", "labels"],
                description="User intent classification template",
                tags=["classification"]
            ),
            PromptTemplate(
                id="classify_priority",
                name="Priority Classification",
                prompt_type=PromptType.CLASSIFICATION,
                template_text=(
                    "Assign a priority based on the criteria.\n"
                    "Task: {task}\n"
                    "Criteria: {criteria}\n"
                    "Return one of: P1, P2, P3."
                ),
                variables=["task", "criteria"],
                description="Task priority classification template",
                tags=["classification", "triage"]
            ),
            PromptTemplate(
                id="classify_sentiment",
                name="Sentiment Classification",
                prompt_type=PromptType.CLASSIFICATION,
                template_text=(
                    "Classify sentiment as Positive, Neutral, or Negative.\n"
                    "Text: {text}"
                ),
                variables=["text"],
                description="Sentiment classification template",
                tags=["classification", "sentiment"]
            ),
            # Q&A templates
            PromptTemplate(
                id="qa_faq",
                name="FAQ Answer",
                prompt_type=PromptType.Q_AND_A,
                template_text=(
                    "Answer the question using the provided context.\n"
                    "Context:\n{context}\n"
                    "Question: {question}\n"
                    "Answer succinctly and cite relevant context."
                ),
                variables=["context", "question"],
                description="FAQ question answering template",
                tags=["q_and_a", "faq"]
            ),
            PromptTemplate(
                id="qa_troubleshoot",
                name="Troubleshooting Q&A",
                prompt_type=PromptType.Q_AND_A,
                template_text=(
                    "Provide troubleshooting steps.\n"
                    "Symptoms: {symptoms}\n"
                    "Environment: {environment}\n"
                    "Return ordered steps and expected outcomes."
                ),
                variables=["symptoms", "environment"],
                description="Troubleshooting Q&A template",
                tags=["q_and_a", "support"]
            ),
        ]
        self.add_templates(templates)
    
    def add_template(self, template: PromptTemplate) -> None:
        """Register new template"""
        self.templates[template.id] = template

    def add_templates(self, templates: List[PromptTemplate]) -> None:
        """Register multiple templates"""
        for template in templates:
            self.add_template(template)

    def create_custom_template(
        self,
        template_id: str,
        name: str,
        prompt_type: PromptType,
        template_text: str,
        variables: List[str],
        description: str = "",
        tags: Optional[List[str]] = None,
        version: str = "1.0"
    ) -> PromptTemplate:
        """Create and register a custom template"""
        if template_id in self.templates:
            raise ValueError(f"Template {template_id} already exists")
        template = PromptTemplate(
            id=template_id,
            name=name,
            prompt_type=prompt_type,
            template_text=template_text,
            variables=variables,
            description=description,
            tags=tags or [],
            version=version,
        )
        self.add_template(template)
        return template
    
    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Retrieve template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, prompt_type: Optional[PromptType] = None) -> List[PromptTemplate]:
        """List templates, optionally filtered by type"""
        templates = list(self.templates.values())
        if prompt_type:
            templates = [t for t in templates if t.prompt_type == prompt_type]
        return templates
    
    def find_by_tags(self, tags: List[str]) -> List[PromptTemplate]:
        """Find templates by tags"""
        result = []
        for template in self.templates.values():
            if template.tags and any(tag in template.tags for tag in tags):
                result.append(template)
        return result


class PromptComposer:
    """Compose complex prompts from templates and components"""
    
    def __init__(self, library: PromptLibrary):
        self.library = library
    
    def compose(self, template_id: str, **variables) -> str:
        """Compose prompt from template"""
        template = self.library.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        if not template.validate_variables(variables):
            missing = set(template.variables) - set(variables.keys())
            raise ValueError(f"Missing variables: {missing}")
        
        return template.render(**variables)
    
    def compose_multi(self, template_ids: List[str], **variables) -> str:
        """Compose multi-part prompt from multiple templates"""
        parts = []
        for template_id in template_ids:
            part = self.compose(template_id, **variables)
            parts.append(part)
        return "\n\n".join(parts)
    
    def with_system_message(self, system_role: str, user_prompt: str) -> str:
        """Combine system message with user prompt"""
        return f"System: {system_role}\n\nUser: {user_prompt}"
    
    def with_context(self, context: str, prompt: str) -> str:
        """Add context to prompt"""
        return f"Context:\n{context}\n\nQuery:\n{prompt}"


class PromptOptimizer:
    """Optimize prompts for better AI responses"""
    
    @staticmethod
    def add_clarity_markers(prompt: str) -> str:
        """Add clarity markers to structure prompt"""
        return f"""
Please respond to the following request:

REQUEST:
{prompt}

INSTRUCTIONS:
- Be clear and concise
- Focus on accuracy
- Provide examples if helpful
""".strip()
    
    @staticmethod
    def add_constraints(prompt: str, constraints: List[str]) -> str:
        """Add constraints to prompt"""
        constraint_str = "\n".join([f"- {c}" for c in constraints])
        return f"{prompt}\n\nConstraints:\n{constraint_str}"
    
    @staticmethod
    def add_output_format(prompt: str, format_spec: str) -> str:
        """Specify output format"""
        return f"{prompt}\n\nExpected output format:\n{format_spec}"


# Export public API
__all__ = ['PromptType', 'PromptTemplate', 'PromptLibrary', 'PromptComposer', 'PromptOptimizer']
