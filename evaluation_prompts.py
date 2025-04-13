"""
Prompts and formats for different types of evaluations in LoveSims
"""

# Format specifications for different evaluation types
SELF_REFLECTION_FORMAT = """{
    "satisfactionScore": "Score from 0-100 indicating overall satisfaction with the interaction",
    "lengthFeedback": "One of: 'Too short', 'Just right', 'Too long'",
    "attributeRatings": {
        "Attractiveness": "Score 0-100 on how attracted you felt",
        "Sincerity": "Score 0-100 on how sincere they seemed",
        "Intelligence": "Score 0-100 on how intelligent they appeared",
        "Fun": "Score 0-100 on how fun the interaction was",
        "Ambition": "Score 0-100 on how ambitious they seemed",
        "SharedInterests": "Score 0-100 on level of shared interests"
    },
    "decision": "Answer 'yes' or 'no': Would you want to see this person again?",
    "analysis": "Brief analysis of the interaction and compatibility"
}"""

TRANSCRIPT_ANALYSIS_FORMAT = """{
    "analysis": "Detailed analysis of the interaction and compatibility",
    "compatibilityScore": "Overall compatibility score from 0-100",
    "attributeSimilarity": {
        "Attractiveness": "Score 0-100 on similarity in attractiveness levels",
        "Sincerity": "Score 0-100 on similarity in sincerity levels",
        "Intelligence": "Score 0-100 on similarity in intelligence levels",
        "Fun": "Score 0-100 on similarity in fun/playfulness",
        "Ambition": "Score 0-100 on similarity in ambition levels",
        "SharedInterests": "Score 0-100 on overlap in interests"
    },
    "decision": "Answer 'yes' or 'no': Should these two people see each other again?",
    "keyFactors": "List of 3-5 key factors affecting compatibility"
}"""

PROFILE_ANALYSIS_FORMAT = """{
    "analysis": "Detailed analysis of potential compatibility based on profiles",
    "compatibilityScore": "Overall compatibility score from 0-100",
    "attributeSimilarity": {
        "Attractiveness": "Score 0-100 on compatibility in attractiveness preferences",
        "Sincerity": "Score 0-100 on alignment in sincerity/authenticity",
        "Intelligence": "Score 0-100 on intellectual compatibility",
        "Fun": "Score 0-100 on similarity in approach to fun/entertainment",
        "Ambition": "Score 0-100 on alignment in ambition/goals",
        "SharedInterests": "Score 0-100 on overlap in interests/hobbies"
    },
    "decision": "Answer 'yes' or 'no': Should these two people see each other again?",
    "keyFactors": "List of 3-5 key factors affecting compatibility"
}"""

def get_self_reflection_prompt(agent_name, agent_profile, memories, other_agent, context, transcript):
    return f"""You are {agent_name}. Based on your profile:
{agent_profile}

And your memories:
{memories}

You just had a conversation with {other_agent} in the context: {context}

Here's the transcript:
{transcript}

Please reflect on this interaction by providing:
1. A satisfaction score (0-100). Be BRUTALLY honest - most dates are mediocre or bad. Consider:
   - Did you feel a genuine spark or was it just polite conversation?
   - Were there any red flags, turn-offs, or deal-breakers?
   - Did they meet your standards or were you settling?
   - Be harsh - give low scores (0-30) for bad matches, medium (31-70) for okay ones, and only high scores (71-100) for truly exceptional connections

2. Feedback on conversation length and engagement quality
3. Ratings (0-100) for different attributes. Use the FULL range:
   - 0-20: Terrible/Major red flags
   - 21-40: Poor/Significant issues
   - 41-60: Mediocre/Just okay
   - 61-80: Good but not great
   - 81-100: Exceptional/Perfect match
4. A critical analysis highlighting both positives AND negatives

Don't sugarcoat anything. If something was bad, say it was bad. Most interactions should NOT get high scores."""

def get_transcript_analysis_prompt(agents, context, transcript):
    return f"""As a harsh critic, analyze this conversation between {' and '.join(agents)}:

Context: {context}

Transcript:
{transcript}

Provide a brutally honest analysis:
1. Overall compatibility (0-100):
   - 0-20: Terrible match, clear incompatibility
   - 21-40: Poor connection, major issues
   - 41-60: Mediocre interaction, nothing special
   - 61-80: Good but with notable concerns
   - 81-100: Exceptional match (should be rare!)

2. Score these specific aspects (0-100):
   - Conversation flow (awkward vs natural)
   - Emotional connection
   - Shared interests/values
   - Red flags/concerning behavior
   
3. Key factors affecting compatibility (positive AND negative)
4. Detailed critique of their interaction - don't hold back on criticism

Remember: Most conversations are average or below. Don't inflate scores."""

def get_profile_analysis_prompt(agent1, profile1, memories1, agent2, profile2, memories2):
    return f"""As a ruthlessly honest matchmaker, analyze the compatibility between:

Person 1 ({agent1}):
Profile: {profile1}
Memories: {memories1}

Person 2 ({agent2}):
Profile: {profile2}
Memories: {memories2}

Provide a harsh assessment:
1. Overall compatibility potential (0-100):
   - 0-20: Terrible match, should avoid
   - 21-40: Poor compatibility, major concerns
   - 41-60: Average match, nothing special
   - 61-80: Good potential but with issues
   - 81-100: Exceptional match (extremely rare!)

2. Score these aspects (0-100, use the full range):
   - Values alignment
   - Lifestyle compatibility
   - Personality match
   - Long-term potential
   
3. Dealbreakers and red flags
4. Detailed compatibility analysis - focus on potential problems

Be merciless in your assessment. Most matches are NOT highly compatible."""
