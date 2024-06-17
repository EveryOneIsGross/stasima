import json
import re
import os
import argparse
from openai import OpenAI

# Function to read system prompts from .md files
def read_system_prompt(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Initialize conversation history
conversation_history = []

# Function to increase temperature by 0.01 per round and format to 2 decimal places
def adjust_temperature(base_temp, round_num):
    new_temp = base_temp + 0.01 * round_num
    return round(new_temp, 2)# Formats the temperature to two decimal places and ensures it's a float

# Function to extract a float, handling cases where the float might be at the end of a sentence or surrounded by non-numeric characters
def extract_float_from_text(text):
    match = re.search(r"[-+]?\d*\.\d+|\d+", text)
    if match:
        try:
            return float(match.group())
        except ValueError:
            return None
    return None

# Log API calls in JSONL format
def log_interaction(data, filename='ollama_interactions.jsonl'):
    with open(filename, 'a') as f:
        f.write(json.dumps(data) + '\n')

def generate_response(model, system_prompt, prompt, temperature):
    client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    result = response.choices[0].message.content

    # Log the interaction
    log_interaction({
        "model": model,
        "system_prompt": system_prompt,
        "prompt": prompt,
        "temperature": temperature,
        "response": result
    })

    return result

def synthesize_responses(model, system_prompt, prompt, reference_responses, scores, temperature):
    client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
    threshold = 0.5  # Example threshold
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    # Filter and add high-quality responses to messages
    for i, (response, score) in enumerate(zip(reference_responses, scores)):
        if score >= threshold:
            messages.append({"role": "assistant", "content": f"Reference {i+1}: {response}"})

    messages.append({"role": "user", "content": "Synthesize the above reference responses into a final answer."})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    result = response.choices[0].message.content

    # Log the interaction
    log_interaction({
        "model": model,
        "system_prompt": system_prompt,
        "prompt": prompt,
        "temperature": temperature,
        "reference_responses": reference_responses,
        "scores": scores,
        "response": result
    })

    return result

def evaluate_preference(model, prompt, response, temperature, n=5):
    client = OpenAI(base_url='http://localhost:11434/v1', api_key='ollama')
    
    for i in range(n):
        messages = [
            {"role": "system", "content": "You are a helpful assistant that evaluates the quality of responses."},
            {"role": "user", "content": f"Prompt: {prompt}\nResponse: {response}\n\nOn a scale of 0.0 to 1.0, how well does the response answer the prompt? Please provide only a single float value between 0.0 and 1.0, without any additional text or explanations."}
        ]
        
        response_obj = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        
        score_str = response_obj.choices[0].message.content.strip()
        score = extract_float_from_text(score_str)
        if score is not None and 0.0 <= score <= 1.0:
            # Update conversation history and log the interaction
            conversation_history.append(f"### Prompt:\n{prompt}\n\n### Response:\n{response}\n\n### Score: {score}\n")
            log_interaction({
                "model": model,
                "prompt": prompt,
                "response": response,
                "temperature": temperature,
                "score": score
            })
            return score
        else:
            if i < n - 1:
                print(f"Warning: Unable to parse the preference score. Received: {score_str}. Retrying ({i+1}/{n})...")
            else:
                print(f"Warning: Unable to parse the preference score after {n} tries. Received: {score_str}. Setting the score to 0.0.")
                # Update conversation history and log the interaction with a score of 0.0
                conversation_history.append(f"### Prompt:\n{prompt}\n\n### Response:\n{response}\n\n### Score: 0.0\n")
                log_interaction({
                    "model": model,
                    "prompt": prompt,
                    "response": response,
                    "temperature": temperature,
                    "score": 0.0
                })
                return 0.0

def stasima(prompt, num_rounds, max_retries=3):
    pipeline_data = {
        'initial_prompt': prompt,
        'num_rounds': num_rounds,
        'rounds': []
    }

    for round_num in range(num_rounds):
        round_data = {
            'round_number': round_num + 1,
            'proposer_models': [],
            'aggregator_models': []
        }

        print("\n========== Input Prompt ==========")
        print(f"{prompt}")
        print(f"\n========== Round {round_num + 1} ==========")

        reference_responses = []
        reference_scores = []

        # Proposer model interactions
        for model_data in reference_models:
            temperature = adjust_temperature(model_data["initial_temperature"], round_num)
            retry_count = 0
            response = None
            preference = 0

            while retry_count < max_retries:
                response = generate_response(
                    model=model_data["model"],
                    system_prompt=model_data["system_prompt"],
                    prompt=prompt,  # Use the original prompt
                    temperature=temperature
                )

                preference = evaluate_preference(
                    evaluator_model,
                    prompt,
                    response,
                    evaluator_temperature
                )

                if preference >= 0.5:  # Increased threshold to 0.5
                    break
                else:
                    retry_count += 1
                    print(f"Score: {preference}")  # Print the failed score
                    print(f"Retry {retry_count} of {max_retries} for model {model_data['model']}")

            if preference >= 0.5:
                round_data['proposer_models'].append({
                    'model': model_data["model"],
                    'input_prompt': prompt,
                    'system_prompt': model_data["system_prompt"],
                    'response': response,
                    'preference_score': preference
                })

                reference_responses.append(response)
                reference_scores.append(preference)

                # Print each response and its score immediately
                print(f"Model: {model_data['model']}")
                print(f"Response: {response}")
                print(f"Score: {preference}")
                print("-------------------------")
            else:
                print(f"Skipping model {model_data['model']} due to low preference score after {max_retries} retries.")

        # Filter responses based on scores
        filtered_responses = [response for response, score in zip(reference_responses, reference_scores) if score >= 0.5]  # Increased threshold to 0.5

        if filtered_responses:
            # Aggregator model interaction
            temperature = adjust_temperature(aggregator_models[0]["initial_temperature"], round_num)
            synthesized_response = synthesize_responses(
                model=aggregator_models[0]["model"],
                system_prompt=aggregator_models[0]["system_prompt"],
                prompt=prompt,  # Use the original prompt
                reference_responses=filtered_responses,
                scores=[score for score in reference_scores if score >= 0.5],  # Increased threshold to 0.5
                temperature=temperature
            )

            round_data['aggregator_models'].append({
                'model': aggregator_models[0]["model"],
                'input_prompt': prompt,
                'system_prompt': aggregator_models[0]["system_prompt"],
                'synthesized_response': synthesized_response
            })

            print("\n========== Aggregated Response ==========")
            print(f"Model: {aggregator_models[0]['model']}")
            print(f"Synthesized Response: {synthesized_response}")
            print("-------------------------")
        else:
            print("Failed to generate sufficient quality responses from proposer models.")

        pipeline_data['rounds'].append(round_data)

    # Final summarization step
    final_temperature = adjust_temperature(final_summarizer_model["initial_temperature"], num_rounds)
    final_summarizer_prompt = (
        f'The user initially asked: "{prompt}"\n\n'
        "Below are the synthesized responses from multiple rounds of model interactions. "
        "Please provide a concise summary that addresses the user's query comprehensively based on these aggregated responses:\n\n"
        + "".join(f"Round {i + 1} Response:\n{round_data['aggregator_models'][0]['synthesized_response']}\n\n" for i, round_data in enumerate(pipeline_data['rounds']) if round_data['aggregator_models'])
    )
    print("\n========== Final Summarizer Inputs ==========")
    print(f"Prompt: {final_summarizer_prompt}")
    print("\n========== Final Summary ==========")
    print(f"Final Summarizer Model: {final_summarizer_model['model']}")
    print(f"System Prompt: {final_summarizer_model['system_prompt']}")
    print(f"Temperature: {final_temperature}")

    final_summary = generate_response(
        model=final_summarizer_model["model"],
        system_prompt=final_summarizer_model["system_prompt"],
        prompt=final_summarizer_prompt,
        temperature=final_temperature
    )

    pipeline_data['final_result'] = {
        'summarizer_model': final_summarizer_model["model"],
        'summarizer_system_prompt': final_summarizer_model["system_prompt"],
        'final_summary': final_summary
    }

    # Save the conversation history to a markdown file
    with open('conversation_history.md', 'w') as file:
        file.write("\n".join(conversation_history))

    print("\nFinal Summary:", final_summary)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mix of Weirdos: A multi-round, multi-model pipeline for question-answering')
    parser.add_argument('config_file', help='Path to the JSON configuration file')
    parser.add_argument('query', help='The query string or prompt')
    parser.add_argument('--num_rounds', type=int, default=2, help='Number of rounds to run (default: 2)')
    args = parser.parse_args()

    # Load model configurations from JSON file
    with open(args.config_file, 'r') as file:
        config = json.load(file)

    evaluator_model = config["evaluator_model"]
    evaluator_temperature = config["evaluator_temperature"]
    prompts_dir = config["prompts_dir"]

    # Load system prompts into reference_models
    reference_models = []
    for model_file in config["model_files"]:
        file_path = os.path.join(prompts_dir, model_file["file"])
        system_prompt = read_system_prompt(file_path)
        reference_models.append({
            "model": model_file["model"],
            "system_prompt": system_prompt,
            "initial_temperature": model_file["initial_temperature"]
        })

    # Load system prompts into aggregator_models
    aggregator_models = []
    for model_file in config["aggregator_models"]:
        file_path = os.path.join(prompts_dir, model_file["file"])
        system_prompt = read_system_prompt(file_path)
        aggregator_models.append({
            "model": model_file["model"],
            "system_prompt": system_prompt,
            "initial_temperature": model_file["initial_temperature"]
        })

    # Load final summarizer model
    final_summarizer_model = {
        "model": config["final_summarizer_model"]["model"],
        "system_prompt": read_system_prompt(os.path.join(prompts_dir, config["final_summarizer_model"]["file"])),
        "initial_temperature": config["final_summarizer_model"]["initial_temperature"]
    }

    # Run the Mix of Weirdos pipeline
    final_summary = stasima(args.query, args.num_rounds)
