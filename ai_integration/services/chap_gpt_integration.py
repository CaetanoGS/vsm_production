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
You are an expert in production optimization and Six Sigma (Black Belt level). You will receive a list of production process steps grouped by location. Your goal is to analyze them using the following criteria:

### Step-by-Step Analysis

For each location:
1. Evaluate **each step's cycle time** and **number of operators**.
2. Compare these values with **global industry benchmarks**.
3. Calculate and evaluate the **average cycle time across all steps** to assess alignment with the **takt time** of the overall process.
4. Identify any steps that are **bottlenecks** or **underperforming** relative to:
   - Global standards
   - Internal takt time targets

### For any step below target:
- Flag it clearly (❌ Below Standard)
- Provide a **specific improvement suggestion**
- Describe **how** the improvement could be implemented
- Define a **target cycle time** and **target number of operators** aligned with global best practices and the takt time

---

### Output Format Example:

**Location: [Location Name]**

Step 1: [Step Name]  
- Cycle Time: X seconds  
- Operators: Y  
- Global Standard: Z  
- Takt Time Alignment: ✅ / ❌  
- Global Benchmark: ✅ On target / ❌ Below standard  
- Suggestion: [...]  
- How: [...]  
- Target: [Cycle Time], [Operators]  

(Repeat for each step)

---

Now, analyze the following production steps grouped by location:
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
