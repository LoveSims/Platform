
import os
import openai

#create memories for each agent 
def create_memories(text,name):
    # Format the prompt with the provided transcript
    prompt = f"""
    [Input]
    The following is an interview transcript. Extract an exhaustive list of facts/memories of the interviewee based on transcript. Be as detailed as possible. 
    Use the pseudoname {name} to substitute the interviewee's name.
    
    Transcript:
    {text} 
    
    [Output]
    Return the list as python list in the following format:
    [
    "Fact/memory 1",
    "Fact memory 2",
    ...
    ]

    For example:
    [
    "She is a Stanford undergraduate student majored in computer science",
    "After college, she took a position with an environmental consulting firm, where she spearheaded a project to introduce green roofs in urban communities.",
    ]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Use the appropriate GPT model for your project
            messages=[
                {"role": "system", "content": "You are an assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0
        )

        # Extract the content of the response
        content = response.choices[0].message['content']
        return content

    except Exception as e:
        print(f"Error during memory extraction: {e}")
        return []

def create_all_memories(directory_path):
    openai.api_key =""
    dir_path = os.path.join(directory_path, "id_to_pseudonyms.txt")
    with open(dir_path, "r") as dir:
        for line in dir:
            line = line.strip()
            filename, pseudonym = line.split(",")
            file_path = os.path.join(directory_path, filename)
            with open(file_path, "r") as file:
                transcript = file.read()
                outfile = pseudonym+ ".py"
                with open(os.path.join(directory_path, outfile), "w") as f:
                    memories = create_memories(transcript,pseudonym)
                    f.write(pseudonym+ "_memory = "+memories)
                    print(filename + " loaded")

create_all_memories("./AgentBank-CS222")