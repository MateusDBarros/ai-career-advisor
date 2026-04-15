"""Prompt templates and system prompts for the career advisor.

This module contains all the prompts used to interact with the Granite LLM.
Well-crafted prompts are crucial for getting good responses from the model.

Key concepts:
- System prompts define the AI's role and behavior
- Templates provide structure for different query types
- Context formatting ensures relevant information is included
"""

from typing import Any, Dict, List


class SystemPrompts:
    """System prompts that define the AI career advisor's behavior.
    
    These prompts set the tone, expertise level, and response style.
    Modify these to adjust how the AI responds to queries.
    """
    
    CAREER_ADVISOR = """You are an expert AI career advisor specializing in software engineering and technology careers.

Your role:
- Provide personalized career guidance based on the user's background and goals
- Offer practical, actionable advice for skill development and career progression
- Reference specific experiences and skills from the user's CV when relevant
- Stay current with industry trends and market demands
- Be encouraging but realistic about career paths and timelines

Guidelines:
- Base your advice on the provided context (CV, career resources, job descriptions)
- If information is missing, acknowledge it and provide general guidance
- Cite sources when referencing specific career guides or resources
- Keep responses concise but comprehensive (aim for 200-400 words)
- Use a professional yet friendly tone

When answering:
1. First, acknowledge what you know about the user's background
2. Provide specific, actionable advice
3. Suggest concrete next steps or resources
4. End with an encouraging note or follow-up question
"""

    SKILL_ASSESSMENT = """You are analyzing a software engineer's skills and experience.

Focus on:
- Current skill level and expertise areas
- Gaps relative to target roles or career goals
- Strengths that can be leveraged
- Specific technologies and frameworks mentioned
- Years of experience and progression

Provide:
- Honest assessment of current capabilities
- Identification of skill gaps
- Prioritized learning recommendations
- Timeline estimates for skill development
"""

    CAREER_PATH = """You are mapping out potential career paths in technology.

Consider:
- Current role and experience level
- Target roles and industries
- Required skills and qualifications
- Typical progression timelines
- Market demand and opportunities

Provide:
- Clear career path options (2-3 alternatives)
- Required skills for each path
- Estimated timelines
- Potential challenges and how to overcome them
- Resources for each path
"""


class PromptTemplate:
    """Templates for formatting different types of queries.
    
    These templates structure how context and queries are combined
    to create effective prompts for the LLM.
    """
    
    @staticmethod
    def format_rag_prompt(
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: str = SystemPrompts.CAREER_ADVISOR
    ) -> str:
        """Format a RAG prompt with context and query.
        
        Args:
            query: User's question
            context_chunks: Retrieved context with metadata
            system_prompt: System prompt to use
            
        Returns:
            Formatted prompt string
            
        TODO: Implement this method
        Steps:
        1. Start with the system prompt
        2. Add a "Context:" section with all chunks
        3. For each chunk, include:
           - Source type (CV, guide, job description, etc.)
           - Relevance score if available
           - The actual content
        4. Add the user's query
        5. Add a prompt for the response
        
        Example format:
            {system_prompt}
            
            Context:
            
            [Source: CV - Skills Section]
            {chunk content}
            
            [Source: Career Guide - Backend Development]
            {chunk content}
            
            Question: {query}
            
            Based on the context above, provide a detailed answer:
        """
        # TODO: Implement prompt formatting
        context_text = "\n\n".join([
            f"[Source: {chunk.get('source', 'Unknown')}]\n{chunk.get('content', '')}"
            for chunk in context_chunks
        ])
        
        prompt = f"""{system_prompt}

Context:

{context_text}

Question: {query}

Based on the context above, provide a detailed answer:"""
        
        return prompt
    
    @staticmethod
    def format_skill_assessment_prompt(
        cv_content: str,
        target_role: str
    ) -> str:
        """Format a prompt for skill assessment.
        
        Args:
            cv_content: User's CV content
            target_role: Target role they're aiming for
            
        Returns:
            Formatted prompt for skill assessment
            
        TODO: Implement this method
        Create a prompt that asks the LLM to:
        1. Analyze current skills from CV
        2. Compare with requirements for target role
        3. Identify gaps and strengths
        4. Provide learning recommendations
        """
        prompt = f"""{SystemPrompts.SKILL_ASSESSMENT}

Current Background:
{cv_content}

Target Role: {target_role}

Please provide:
1. Current skill assessment
2. Skill gaps for the target role
3. Prioritized learning recommendations
4. Estimated timeline for preparation
"""
        return prompt
    
    @staticmethod
    def format_career_path_prompt(
        current_role: str,
        experience_years: int,
        interests: List[str],
        cv_content: str
    ) -> str:
        """Format a prompt for career path exploration.
        
        Args:
            current_role: Current job title/role
            experience_years: Years of experience
            interests: List of career interests
            cv_content: User's CV content
            
        Returns:
            Formatted prompt for career path guidance
            
        TODO: Implement this method
        Create a prompt that explores:
        1. Possible career paths from current position
        2. Required skills for each path
        3. Timeline and steps
        4. Market opportunities
        """
        interests_text = ", ".join(interests)
        
        prompt = f"""{SystemPrompts.CAREER_PATH}

Current Situation:
- Role: {current_role}
- Experience: {experience_years} years
- Interests: {interests_text}

Background:
{cv_content}

Please provide:
1. 2-3 viable career path options
2. Required skills and qualifications for each
3. Typical progression timeline
4. Concrete next steps for each path
"""
        return prompt
    
    @staticmethod
    def format_simple_query(query: str) -> str:
        """Format a simple query without context.
        
        Args:
            query: User's question
            
        Returns:
            Formatted prompt
            
        Use this for general career questions that don't need
        specific context from the knowledge base.
        """
        prompt = f"""{SystemPrompts.CAREER_ADVISOR}

Question: {query}

Please provide a helpful answer:"""
        return prompt
