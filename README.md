# LLM - Marketing Agent

Getting started :

1. Create a new virtual environment :

    1. Create a virtual environment named myvenv : ```python -m venv ipvenv```
    2. Activate this virtual environment : ```.\ipvenv\Scripts\activate```

2. Connecting virtual environment to jupyter
    1. Inside this virtual environment install ipykernel : ```pip install ipykernel```
    2. Add this virtual environment as a kernel ```python -m ipykernel install --name=ipvenv```
    3. Now go to Jupyter notebook kernel -> change kernel -> select myvenv

3. Install required libraries : ```pip install -r requirements.txt```