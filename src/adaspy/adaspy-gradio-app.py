from adaspy import agent_designer, dspy_framework_description
import gradio as gr


def get_agent(query):
    agent_design = agent_designer(
        application_domain=query, agent_framework_description=dspy_framework_description
    ).optimal_agent

    return agent_design

demo = gr.Interface(fn=get_agent, 
                    inputs=["text"], 
                    examples=["Write an agent that given a repository and a \
                               research direction, gives you a research paper",
                               "Poem writer agent", "Agent that writes travel itinerary"], 
                    outputs="text")

demo.launch()
