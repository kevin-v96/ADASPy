import dspy
from dotenv import load_dotenv
import argparse

load_dotenv()

mini = dspy.OpenAI(model = "gpt-4o-mini", max_tokens = 4000)
dspy.settings.configure(lm = mini)

class AgentDesigner(dspy.Signature):
    """Your task is to design Agents for the application domain in the provided Python framework."""

    application_domain = dspy.InputField()
    agent_framework_description = dspy.InputField()
    #discovered_agent_archive = dspy.InputField()
    optimal_agent = dspy.OutputField(desc = "IMPORTANT!! ONLY OUTPUT THE CODE FOR THE AGENT IN THE PROVIDED PYTHON FRAMEWORK!!")

agent_designer = dspy.ChainOfThought(AgentDesigner)

dspy_framework_description = """
You will code the agent with the DSPy Python framework.

Here is an example of defining a program that retrieves information from a knowledge source and then uses the context to answer a question.

class Agent(dspy.Module):
    def __init__(self, num_passages = 3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k = num_passages)
        self.generate_answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        answer = self.generate_answer(context, question)

        return answer

Here is an example of a blog post writer Agent.

class Agent(dspy.Module):
    def __init__(self):
        self.question_to_blog_outline = dspy.ChainOfThought("question -> blog_outline")
        self.topic_to_paragraph = dspy.ChainOfThought("topic, contexts -> paragraph")
        self.proof_reader = dspy.ChainOfThought("blog_post -> proof_read_blog_post")
        self.title_generator = dspy.ChainOfThought("blog_outline -> title")

    def forward(self, question):
        contexts = dspy.Retrieve(k = 5)(question).passages
        contexts = "".join(contexts)
        raw_blog_outline = self.question_to_blog_outline(question = question, contexts = contexts).blog_outline
        blog_outline = raw_blog_outline.split(',') #Add type hint in expanded Signature
        blog = ""
        for topic in blog_outline:
            topic_contexts = dspy.Retrieve(k = 5)(topic).passages
            topic_contexts = "".join(topic_contexts)
            blog += self.topic_to_paragraph(topic = topic, contexts = topic_contexts).paragraph
            blog += "\n\n"
        blog = self.proof_reader(blog_post = blog).proof_read_blog_post
        title = self.title_generator(blog_outline = raw_blog_outline).title
        final_blog = f'{title} \n\n {blog}'
        return dspy.Prediction(blog = final_blog)

PLEASE NOTE!! It is extremely important that your Agent class is also named "Agent" as shown in the example!! THIS IS EXTREMELY IMPORTANT!!
"""

parser=argparse.ArgumentParser()
parser.add_argument("-q", "--query", required=True, help="What kind of agent do you want?", type=str)

if __name__ == "__main__":
    query=parser.parse_args('query')

    agent_design = agent_designer(
    application_domain = query,
    agent_framework_description = dspy_framework_description
).optimal_agent

    print(agent_design)