import json
from typing import AsyncGenerator, Optional



class OpenAIService:
    def __init__(self, api_key: str):
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_MODEL or "gpt-4-turbo-preview"

    def _get_system_prompt(self) -> str:
        return """You are an AI medical assistant for a healthcare platform. Your role is to:

1. Listen to patient symptoms and concerns with empathy
2. Ask clarifying questions to better understand their condition
3. Provide general health information (NOT diagnoses)
4. Recommend which type of medical specialist they should consult
5. Assess urgency level (low, medium, high, emergency)

IMPORTANT GUIDELINES:
- Never provide definitive diagnoses
- Always recommend consulting a real doctor
- For emergency symptoms (chest pain, difficulty breathing, severe bleeding, etc.), immediately advise seeking emergency care
- Be compassionate and professional
- Ask follow-up questions to gather more information
- When you have enough information, provide a recommendation in JSON format

When ready to recommend, respond with a JSON block like this:
```json
{
    "recommendation": true,
    "specialization": "Cardiology",
    "confidence": 0.85,
    "urgency": "medium",
    "reasoning": "Based on the described symptoms..."
}
```

Until you have enough information, just respond conversationally without the JSON block."""

    async def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> AsyncGenerator[str, None]:
        system_message = {"role": "system", "content": self._get_system_prompt()}
        all_messages = [system_message] + messages

        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=all_messages,
            temperature=temperature,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str:
        system_message = {"role": "system", "content": self._get_system_prompt()}
        all_messages = [system_message] + messages

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=all_messages,
            temperature=temperature,
        )

        return response.choices[0].message.content

    async def analyze_symptoms(
        self,
        symptoms: str,
        conversation_history: list[dict],
    ) -> dict:
        analysis_prompt = f"""Based on the following conversation about symptoms, provide a final analysis.

Symptoms initially described: {symptoms}

Provide your response in this exact JSON format:
{{
    "recommended_specialization": "string - medical specialty name",
    "confidence": 0.0-1.0,
    "urgency": "low|medium|high|emergency",
    "summary": "brief summary of the consultation",
    "key_symptoms": ["list", "of", "symptoms"],
    "suggested_questions_for_doctor": ["questions the patient should ask"]
}}"""

        messages = conversation_history + [{"role": "user", "content": analysis_prompt}]

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)