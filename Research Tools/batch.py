import requests
import time
import pandas as pd

# Define the base URL of your Flask app
BASE_URL = 'http://127.0.0.1:5000'

# Agents to run simulations for
selected_agents = ['Diego', 'Jinsoo', 'Yuki', 'Leila']

# Number of simulations per agent per context
num_simulations = 2

# Date contexts
date_contexts = [
    'You are meeting for a casual coffee at a local cafe on a rainy afternoon.',
    'You are attending an art exhibition together on a Saturday evening.',
    'You are on your first date at Stanford\'s Treehouse during the last day of the fall quarter.'
]

# Date duration
date_duration = 10

# Function to run a single simulation
def run_simulation(selected_agent, run_number, date_context):
    print(f"Running simulation {run_number} for agent {selected_agent} with context '{date_context}'")
    
    # Reset the game
    requests.post(f'{BASE_URL}/reset')
    
    # Start dates
    start_dates_payload = {
        'mode': 'one-to-all',
        'agents': [selected_agent],
        'dateContext': date_context,
        'dateDuration': date_duration
    }
    response = requests.post(f'{BASE_URL}/start_dates', json=start_dates_payload)
    if response.status_code != 200:
        print(f"Error starting dates for agent {selected_agent}")
        return
    
    # Run dates
    response = requests.post(f'{BASE_URL}/run_dates')
    if response.status_code != 200:
        print(f"Error running dates for agent {selected_agent}")
        return
    
    # Wait a bit to ensure dates have run (adjust if necessary)
    time.sleep(5)
    
    # Evaluate - Self Reflection
    evaluate_payload = {
        'type': 'self-reflection',
        'mode': 'one-to-all',
        'agents': [selected_agent],
    }
    response = requests.post(f'{BASE_URL}/evaluate', json=evaluate_payload)
    if response.status_code != 200:
        print(f"Error evaluating dates (self-reflection) for agent {selected_agent}")
        return
    evaluations_self = response.json()
    
    # Evaluate - Transcript-Based
    evaluate_payload['type'] = 'transcript-based'
    response = requests.post(f'{BASE_URL}/evaluate', json=evaluate_payload)
    if response.status_code != 200:
        print(f"Error evaluating dates (transcript-based) for agent {selected_agent}")
        return
    evaluations_transcript = response.json()
    
    # Combine evaluations
    combined_evaluations = combine_evaluations(evaluations_self, evaluations_transcript)
    
    # Save evaluations to CSV
    csv_filename = f"{selected_agent}_run{run_number}.csv"
    save_evaluations_to_csv(combined_evaluations, csv_filename, selected_agent, date_context)
    print(f"Saved evaluations to {csv_filename}")

# Function to combine self-reflection and transcript-based evaluations
def combine_evaluations(evaluations_self, evaluations_transcript):
    # Create a mapping from target agent to self-reflection evaluation
    self_eval_map = {}
    for eval in evaluations_self:
        if eval.get('type') == 'self-reflection':
            target = eval.get('target')
            self_eval_map[target] = eval

    # Combine with transcript-based evaluations
    combined = []
    for eval in evaluations_transcript:
        if eval.get('type') == 'transcript-based':
            agents = eval.get('agents')
            main_agent = agents[0]
            target_agent = agents[1]
            # Find corresponding self-reflection evaluation
            self_eval = self_eval_map.get(target_agent, {})
            combined_eval = {
                'MainAgent': main_agent,
                'TargetAgent': target_agent,
                # Self-Reflection Fields with 'SelfReflection' prefix
                'SelfReflectionSatisfactionScore': self_eval.get('satisfactionScore'),
                'SelfReflectionLengthFeedback': self_eval.get('lengthFeedback'),
                'SelfReflectionDecision': self_eval.get('decision'),
                'SelfReflectionAnalysis': self_eval.get('analysis'),
            }
            # Flatten attributeRatings from self-reflection with 'SelfReflection' prefix
            attribute_ratings = self_eval.get('attributeRatings', {})
            for attr in ['Ambition', 'Attractiveness', 'Fun', 'Intelligence', 'SharedInterests', 'Sincerity']:
                combined_eval[f'SelfReflection{attr}'] = attribute_ratings.get(attr)
    
            # Transcript-Based Fields
            combined_eval['CompatibilityScore'] = eval.get('compatibilityScore')
            # Flatten attributeSimilarity from transcript-based evaluation with 'Transcript' prefix
            attribute_similarity = eval.get('attributeSimilarity', {})
            for attr in ['Ambition', 'Attractiveness', 'Fun', 'Intelligence', 'SharedInterests', 'Sincerity']:
                combined_eval[f'Transcript{attr}'] = attribute_similarity.get(attr)
            combined_eval['TranscriptDecision'] = eval.get('decision')
            combined_eval['KeyFactors'] = eval.get('keyFactors')
            combined_eval['TranscriptAnalysis'] = eval.get('analysis')
    
            combined.append(combined_eval)
    return combined

# Function to save evaluations to CSV
def save_evaluations_to_csv(evaluations, filename, main_agent, date_context):
    # Create DataFrame
    df = pd.DataFrame(evaluations)
    
    # Add additional columns
    df['DateContext'] = date_context
    df['RunNumber'] = filename.split('_run')[1].split('.')[0]
    
    # Rename columns to include spaces
    df.rename(columns={
        'SelfReflectionSatisfactionScore': 'Self Reflection Satisfaction Score',
        'SelfReflectionLengthFeedback': 'Self Reflection Length Feedback',
        'SelfReflectionDecision': 'Self Reflection Decision',
        'SelfReflectionAnalysis': 'Self Reflection Analysis',
        'SelfReflectionAmbition': 'Self Reflection Ambition',
        'SelfReflectionAttractiveness': 'Self Reflection Attractiveness',
        'SelfReflectionFun': 'Self Reflection Fun',
        'SelfReflectionIntelligence': 'Self Reflection Intelligence',
        'SelfReflectionSharedInterests': 'Self Reflection Shared Interests',
        'SelfReflectionSincerity': 'Self Reflection Sincerity',
        'TranscriptAmbition': 'Transcript Ambition',
        'TranscriptAttractiveness': 'Transcript Attractiveness',
        'TranscriptFun': 'Transcript Fun',
        'TranscriptIntelligence': 'Transcript Intelligence',
        'TranscriptSharedInterests': 'Transcript Shared Interests',
        'TranscriptSincerity': 'Transcript Sincerity',
        'TranscriptDecision': 'Transcript Decision',
        'TranscriptAnalysis': 'Transcript Analysis',
        'CompatibilityScore': 'Transcript Compatibility Score',
        'KeyFactors': 'Transcript Key Factors',
    }, inplace=True)
    
    # Reorder columns to match the desired header
    column_order = [
        'MainAgent',
        'TargetAgent',
        'Self Reflection Satisfaction Score',
        'Self Reflection Length Feedback',
        'Self Reflection Decision',
        'Self Reflection Analysis',
        'Self Reflection Ambition',
        'Self Reflection Attractiveness',
        'Self Reflection Fun',
        'Self Reflection Intelligence',
        'Self Reflection Shared Interests',
        'Self Reflection Sincerity',
        'Transcript Compatibility Score',
        'Transcript Ambition',
        'Transcript Attractiveness',
        'Transcript Fun',
        'Transcript Intelligence',
        'Transcript Shared Interests',
        'Transcript Sincerity',
        'Transcript Decision',
        'Transcript Key Factors',
        'Transcript Analysis',
        'DateContext',
        'RunNumber'
    ]
    
    # Ensure all columns are present in the DataFrame
    for col in column_order:
        if col not in df.columns:
            df[col] = None
    
    # Reorder columns
    df = df[column_order]
    
    # Sort if necessary
    df = df.sort_values(by=['RunNumber', 'MainAgent', 'TargetAgent'])
    
    # Save to CSV
    df.to_csv(filename, index=False)

# Main script
if __name__ == '__main__':
    for date_context in date_contexts:
        for agent in selected_agents:
            for run_number in range(1, num_simulations + 1):
                run_simulation(agent, run_number, date_context)
                # Wait between simulations if necessary
                time.sleep(5)
