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