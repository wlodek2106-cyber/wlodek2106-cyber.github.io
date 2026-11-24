LESSON = {"day":1,"title":"AI Fundamentals","sections":[
"Artificial intelligence is software designed to perform tasks such as classification, prediction and generation. Generative models produce outputs based on patterns learned from training data, not guaranteed facts.",
"A language model generates text from context. Image and video models generate visual content. Choose the tool according to the desired output, budget, rights and quality.",
"Use a workflow: define the goal, provide context and constraints, generate, verify, revise. Never upload confidential client data without permission. Check factual claims and commercial-use terms.",
"Practice: create three advertising concepts for an imaginary coffee brand. Specify audience, message, tone and output format. Compare results, identify unsupported claims and revise."
],"prompts":["Act as a creative strategist. Propose three coffee advertising concepts for commuters. Include audience, message and visual direction. Avoid unsupported claims.","Review these concepts for factual accuracy, clarity and originality. Identify uncertainties and suggest revisions."],
"questions":[
["What is generative AI?",["A system that generates content","A guaranteed fact database","A payment service"],0],
["What should you define first?",["Font","Goal","File name"],1],
["Are AI outputs always factual?",["Yes","Only in English","No"],2],
["What should you do with factual claims?",["Verify them","Ignore them","Publish immediately"],0],
["What helps a prompt?",["Random characters","Clear context","No instructions"],1],
["Can confidential client data be uploaded without permission?",["Always","Never check","No"],2],
["Which tool suits image generation?",["An image model","A spreadsheet only","A payment gateway"],0],
["What should you check before commercial use?",["Screen brightness","License terms","Keyboard size"],1],
["What follows an initial draft?",["Automatic publication","Deletion","Review and revision"],2],
["What is a good practice outcome?",["A reviewed set of concepts","Guaranteed income","Unverified claims"],0]
]}
def public_lesson():
    return {**LESSON, "questions":[{"id":str(i),"question":q[0],"options":q[1]} for i,q in enumerate(LESSON["questions"])]}
def answer_key():
    return {str(i):q[2] for i,q in enumerate(LESSON["questions"])}
