import openai
from tb2_vsm.models import Location, Process
from vsm_tb import settings


def call_chatgpt(prompt, model="gpt-4o", temperature=0.2):
    openai.api_key = settings.OPENAI_API_KEY

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in manufacturing optimization and process engineering.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            max_tokens=2000,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error calling ChatGPT: {str(e)}"


def analyze_processes_per_location(location: Location):
    prompt = """
You will receive a list of production process steps grouped by location. For each location:

1. Analyze each step's **cycle time** and **number of operators**.
2. Perform a **global benchmark comparison**.
3. If the performance is **below global standards**, give:
   - **Improvement suggestions**
   - **How** the improvements can be made
   - A **target** to align with global standards.

Example format per location:
---
**Location: [Location Name]**

Step 1: [Step Name]
- Cycle Time: X seconds
- Operators: Y
- Global Standard: Z
- ✅ On target OR ❌ Below standard
- Suggestion: [...]
- How: [...]
- Target: [...]

Repeat for all steps.

Now, analyze the following process steps grouped by location:
{steps}
"""

    # Gather and format steps
    formatted_steps = (
        f"---\n**Location: {location.supplier_name} ({location.country})**\n"
    )
    productions = location.toniebox_productions.all()
    for production in productions:
        for process in production.processes.all():
            for step in process.steps.all():
                formatted_steps += f"Step: {step.name}\n"
                formatted_steps += f"- Cycle Time: {step.cycle_time or 'N/A'}s\n"
                formatted_steps += f"- Operators: {step.amount_of_operators or 0}\n"

    full_prompt = prompt.format(steps=formatted_steps)

    return call_chatgpt(full_prompt)
