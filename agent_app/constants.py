models =  {
    "noushermes" : "Nous-Hermes-Llama2-13B",
    "neuralchat" : "Neural-Chat-7B"
}


neuralchat_template = """### System:
{prompt}

### User:
{context}

### Assistant:
"""


noushermes_template = """### Instruction:
{prompt}

### Input:
{context}

### Response:
"""

brand_personality = """BRAND PERSONALITY:
    Who we are:
    Goal: To empower businesses to leverage the latest wave of Large Language Models (LLMs) in a secure and compliant manner.

    How we describe the need for Prediction Guard:
    Challenge: Limited resources, inconsistency in AI output, compliance and privacy concerns, and the high cost and risks of deploying AI solutions
    Solution: Prediction Guard offers a streamlined, cost-effective solution for businesses to incorporate private, controlled and compliant Large Language Models (LLMs) functionality  
    
    Brand values: 
    Empathy and Authority

    Voice and tone: 
    We are humans speaking to humans. We are confident (never cocky), witty (but never silly), conversational (but always appropriate and respectful), intelligent (and always treating our users as intelligent, too), friendly (but not ingratiating), clear, and simple.

    """