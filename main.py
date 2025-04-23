import os
import csv
import random
import io
import ast
from flask import Flask, render_template, jsonify, request, send_file, Response
from flask_cors import CORS
from agents import agent_list
from llm_utils import *
from evaluation_prompts import (
    SELF_REFLECTION_FORMAT,
    TRANSCRIPT_ANALYSIS_FORMAT,
    PROFILE_ANALYSIS_FORMAT,
    get_self_reflection_prompt,
    get_transcript_analysis_prompt,
    get_profile_analysis_prompt
)

base_dir = os.path.dirname(os.path.abspath(__file__))


class Agent:
    def __init__(self, name, persona):
        self.name = name
        self.persona = persona
        self.messages = []


class Game:
    def __init__(self, date_duration=10):
        self.agents = []
        self.date_context = ""
        self.date_transcript = []
        self.date_duration = date_duration
        self.current_pairs = []

    def add_agents(self, agent_names):
        self.agents = [Agent(name, next(a["persona"] for a in agent_list if a["name"] == name))
                       for name in agent_names]

    def set_date_context(self, context):
        self.date_context = context
        print(f"Date context set to: {self.date_context}")

    def set_pairs(self, mode: str, selected_agents: list[str]):
        """Populate self.current_pairs based on the chosen mode."""
        if mode == "one-to-one":
            if len(selected_agents) < 2:
                raise ValueError("one-to-one mode requires exactly two agents")
            self.current_pairs = [(selected_agents[0], selected_agents[1])]

        elif mode == "one-to-all":
            if not selected_agents:
                raise ValueError("one-to-all mode requires at least one agent")
            main_agent   = selected_agents[0]
            other_agents = [a["name"] for a in agent_list if a["name"] != main_agent]
            self.current_pairs = [(main_agent, other) for other in other_agents]

        else:
            raise ValueError(f"Unsupported mode '{mode}'")

    def run_dates(self):
        for agent1_name, agent2_name in self.current_pairs:
            # Reset conversation history for each new pair
            self.date_transcript = []

            agent1 = Agent(agent1_name, next(a["persona"] for a in agent_list if a["name"] == agent1_name))
            agent2 = Agent(agent2_name, next(a["persona"] for a in agent_list if a["name"] == agent2_name))

            # Log the start of the date
            date_start = f"\nDate between {agent1_name} and {agent2_name}:"
            response_data = {"agent": "System", "response": date_start, "number": 0}
            if not hasattr(stream, 'queue'):
                stream.queue = []
            stream.queue.append(response_data)

            for i in range(self.date_duration):
                # Determine the stage of the date
                if i < self.date_duration * 0.2:
                    stage = "greeting"
                elif i < self.date_duration * 0.8:
                    stage = "conversation"
                else:
                    stage = "goodbye"

                # Alternate between agents
                if i % 2 == 0:
                    current_agent = agent1
                    other_agent = agent2
                else:
                    current_agent = agent2
                    other_agent = agent1

                # Generate and stream the response
                system_prompt = self._create_date_prompt(current_agent, other_agent, stage)
                conversation_context = '\n'.join([msg["response"] for msg in self.date_transcript[-10:]])
                response = self.generate_response(system_prompt, conversation_context)

                response_data = self.log_date(current_agent, f"{current_agent.name}: {response}", i+1)
                if not hasattr(stream, 'queue'):
                    stream.queue = []
                stream.queue.append(response_data)

    def generate_response(self, system_prompt, conversation_context):
        """
        Generates a response from the agent based on the system prompt and current conversation context.
        """
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if conversation_context.strip():
            messages.append({"role": "user", "content": conversation_context})
        response = gen_oai(messages)
        return response.strip()

    def _create_date_prompt(self, agent, other_agent, stage):
        # Get agent memories
        memory_file = os.path.join(base_dir, 'AgentBank', 'memories', f'{agent.name}.py')
        memories = []
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                memories = parse_memory_file(content)

        memories_str = "\n".join([f"- {memory}" for memory in memories])

        return f"""
        You are {agent.name}, {agent.persona}

        Your memories and experiences:
        {memories_str}

        You are on a date with {other_agent.name}.
        The date should follow this structure: start with a greeting, then progress from light to deeper conversation topics, and end with a goodbye.
        You are currently in the {stage} stage of the date.
        Respond in character as {agent.name}, with short, conversational responses appropriate for the current stage of the date.
        Do not include your name or any prefixes or labels in your responses.
        Only output what you would say as {agent.name}.
        Context: {self.date_context}.
        """

    def log_date(self, agent, response, response_number):
        self.date_transcript.append({"agent": agent.name, "response": response, "number": response_number})
        return {"agent": agent.name, "response": response, "number": response_number}

    def get_log(self):
        return "\n".join([msg["response"] for msg in self.date_transcript])


app = Flask(__name__)
CORS(app)
game = None

# Load agent name mapping
agent_id_map = {}
mapping_file = os.path.join(base_dir, 'AgentBank', 'raw_data', 'id_to_pseudonyms.txt')
with open(mapping_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == 2:
            file_id, display_name = row
            file_id = file_id.strip()
            display_name = display_name.strip()
            agent_id_map[display_name] = file_id.replace('.txt', '')

def parse_memory_file(content):
    try:
        # Find the list content between square brackets
        start = content.find('[')
        end = content.rfind(']')
        if start != -1 and end != -1:
            list_content = content[start:end + 1]
            return ast.literal_eval(list_content)
    except:
        pass
    return ["Error parsing memories file"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_dates', methods=['POST'])
def start_dates():
    """Initialize a new Game and validate that the mode is either
    one‑to‑one or one‑to‑all.  Any other value returns HTTP 400."""
    global game
    data = request.get_json()

    mode = data.get('mode')
    if mode not in ("one-to-one", "one-to-all"):
        return jsonify({"error": f"Unsupported mode '{mode}'"}), 400

    selected_agents = data.get('agents')
    date_context    = data.get('dateContext', '')
    date_duration   = data.get('dateDuration', 10)

    game = Game(date_duration=date_duration)
    game.set_date_context(date_context)
    game.set_pairs(mode, selected_agents)

    print(
        f"Game initialized | mode: {mode} | agents: {selected_agents} | "
        f"context: {date_context} | duration: {date_duration}"
    )
    return jsonify({"status": "success"})

@app.route('/run_dates', methods=['POST'])
def run_dates():
    global game
    if not game:
        print("No game initialized")
        return jsonify({"error": "No game initialized"}), 400

    def run_dates_async():
        game.run_dates()
        return jsonify({"status": "completed"})

    return run_dates_async()

@app.route('/stream')
def stream():
    def generate():
        while True:
            if not hasattr(stream, 'queue'):
                stream.queue = []
            if stream.queue:
                data = stream.queue.pop(0)
                yield f"data: {json.dumps(data)}\n\n"
    return Response(generate(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset_game():
    global game
    game = None
    print("Game reset")
    return jsonify({"status": "reset"})

@app.route('/download_log', methods=['GET'])
def download_log():
    if game:
        log_content = game.get_log()
        buffer = io.BytesIO()
        buffer.write(log_content.encode('utf-8'))
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name='date_transcript.md', mimetype='text/markdown')
    else:
        print("No date transcript available for download")
        return jsonify({"error": "No date transcript available"}), 400

@app.route('/agent/<display_name>')
def get_agent_details(display_name):
    try:
        # Get the file ID for this display name
        file_id = agent_id_map.get(display_name)
        if not file_id:
            return jsonify({"error": f"No mapping found for agent {display_name}"})

        response_data = {
            "profile": "",
            "memories": []
        }

        # Get profile from raw_data
        profile_file = os.path.join(base_dir, 'AgentBank', 'raw_data', f'{file_id}.txt')
        if os.path.exists(profile_file):
            with open(profile_file, 'r', encoding='utf-8') as f:
                response_data["profile"] = f.read()

        # Get memories from memories directory
        memory_file = os.path.join(base_dir, 'AgentBank', 'memories', f'{display_name}.py')
        if os.path.exists(memory_file):
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                response_data["memories"] = parse_memory_file(content)

        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": f"Error loading agent details: {str(e)}"})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    eval_type = data.get('type')
    mode = data.get('mode')
    agents = data.get('agents')
    transcript = data.get('transcript')

    results = []

    def get_agent_profile(agent_name):
        # Set project_root to base_dir so that AgentBank is a subfolder
        project_root = base_dir

        # Construct path to the pseudonyms file and load it
        pseudonyms_path = os.path.join(project_root, 'AgentBank', 'raw_data', 'id_to_pseudonyms.txt')
        with open(pseudonyms_path, 'r', encoding='utf-8') as f:
            id_map = dict(line.strip().split(',') for line in f)

        # Find the file_id that matches the agent name
        file_id = next((k for k, v in id_map.items() if agent_name == v), None)
        if not file_id:
            raise ValueError(f"Agent {agent_name} not found in pseudonyms file")

        profile_path = os.path.join(project_root, 'AgentBank', 'raw_data', file_id)
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile = f.read()

        memory_path = os.path.join(project_root, 'AgentBank', 'memories', f'{agent_name}.py')
        if os.path.exists(memory_path):
            with open(memory_path, 'r', encoding='utf-8') as f:
                memories = parse_memory_file(f.read())
        else:
            memories = []

        return {'profile': profile, 'memories': memories}

    if eval_type in ['self-reflection', 'all'] and mode in ['one-to-one', 'one-to-all']:
        if mode == 'one-to-one':
            # Get reflections from both agents
            for agent_name in agents[:2]:
                agent_profile = get_agent_profile(agent_name)
                other_agent = agents[1] if agent_name == agents[0] else agents[0]

                prompt = get_self_reflection_prompt(
                    agent_name=agent_name,
                    agent_profile=agent_profile['profile'],
                    memories=agent_profile['memories'],
                    other_agent=other_agent,
                    context=game.date_context if game else '',
                    transcript=transcript
                )

                reflection = json_gen_oai(prompt, SELF_REFLECTION_FORMAT)
                results.append({
                    'type': 'self-reflection',
                    'agent': agent_name,
                    **reflection
                })
        else:  # one-to-many mode
            main_agent = agents[0]
            main_profile = get_agent_profile(main_agent)

            for other_agent in agents[1:]:
                prompt = get_self_reflection_prompt(
                    agent_name=main_agent,
                    agent_profile=main_profile['profile'],
                    memories=main_profile['memories'],
                    other_agent=other_agent,
                    context=game.date_context if game else '',
                    transcript=transcript
                )

                reflection = json_gen_oai(prompt, SELF_REFLECTION_FORMAT)
                results.append({
                    'type': 'self-reflection',
                    'agent': main_agent,
                    'target': other_agent,
                    **reflection
                })

    if eval_type in ['transcript-based', 'all']:
        prompt = get_transcript_analysis_prompt(
            agents=agents,
            context=game.date_context if game else '',
            transcript=transcript
        )
        evaluation = json_gen_oai(prompt, TRANSCRIPT_ANALYSIS_FORMAT)
        results.append({
            'type': 'transcript-based',
            **evaluation
        })

    if eval_type in ['profiles-based', 'all']:
        profiles = [get_agent_profile(agent) for agent in agents]
        prompt = get_profile_analysis_prompt(
            agent1=agents[0],
            profile1=profiles[0]['profile'],
            memories1=profiles[0]['memories'],
            agent2=agents[1],
            profile2=profiles[1]['profile'],
            memories2=profiles[1]['memories']
        )
        evaluation = json_gen_oai(prompt, PROFILE_ANALYSIS_FORMAT)
        results.append({
            'type': 'profiles-based',
            **evaluation
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
