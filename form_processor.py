import json
from datetime import datetime
from dateutil import parser
import logging
import google.generativeai as genai
import os
import urllib.parse
from embedchain import App

from prompts import ANALYZE_FORM_PROMPT, QA_PROMPT

logger = logging.getLogger("GFF")
GOOGLE_API_KEY = os.environ['GOOGLE_API_KEY']
genai.configure(api_key=GOOGLE_API_KEY)
current_date = datetime.now().strftime("%Y-%m-%d")


def extract_json(text):
    """
    Extracts JSON objects from a string, handling nested structures.

    Args:
        text (str): The text response to extract JSON objects from.

    Returns:
        list: A list of extracted JSON objects. Returns an empty list if no valid JSON objects are found.
    """
    json_objects = []
    stack = []
    start_index = None

    for i, char in enumerate(text):
        if char == '{':
            stack.append(char)
            if len(stack) == 1:
                # Mark the start of a potential JSON object
                start_index = i
        elif char == '}':
            if stack:
                stack.pop()
                if not stack and start_index is not None:
                    # We've found a complete JSON object
                    try:
                        json_obj = json.loads(text[start_index:i + 1])
                        json_objects.append(json_obj)
                        start_index = None
                    except json.JSONDecodeError:
                        # If JSON is invalid, reset start_index and continue
                        start_index = None
                        continue

    return json_objects


def extract_form_data(html_content, model_name='gemini-1.5-pro-latest'):
    model = genai.GenerativeModel(model_name=model_name,
                                  tools=[])  # Tested with tools but not worked, returns empty json
    formatted_prompt = ANALYZE_FORM_PROMPT.substitute(html_content=html_content, current_date=current_date)
    # logger.debug(f"Prompt: {formatted_prompt}")
    logger.debug(
        f"Prompt: {''.join([formatted_prompt[:formatted_prompt.find('HTML Form Code:') + 200], '... [Log Cropped]']) if 'HTML Form Code:' in formatted_prompt else formatted_prompt}")
    response = model.generate_content(formatted_prompt)
    model_output = response.text
    logger.debug(f"Model output: {model_output}")
    json_out = extract_json(model_output)
    logger.debug(f"Model output json: {json_out}")
    return json_out


def query_database(json_input, config_path="config.yaml"):
    """
    Queries the database with questions from the json_input and accumulates unique contexts.

    :param json_input: List of dictionaries, each containing a "field_text" key with a question.
    :param config_path: Path to the configuration file for the App.
    :return: A string containing all unique contexts separated by new lines.
    """
    # Initialize the application with the given configuration
    app = App.from_config(config_path=config_path)

    seen_docs = set()
    unique_contexts = []

    for entry in json_input:
        question = entry.get("field_text")
        # Search for documents based on the question
        docs = app.search(question)

        for doc in docs:
            context = doc.get("context")
            # Add unique contexts to the list
            if context not in seen_docs:
                unique_contexts.append(context)
                seen_docs.add(context)

    doc_string = "\nAdditional context:\n" + "\n".join(unique_contexts)
    logger.debug(f"Extracted documents from DB: {doc_string}")
    return doc_string


def filling_out_form(json_out, user_context, prompt=QA_PROMPT, model_name='gemini-1.5-pro-latest'):
    context = user_context
    if prompt == QA_PROMPT:
        doc_context = query_database(json_out)
        context = f"{user_context}\n\n{doc_context}"
    model = genai.GenerativeModel(model_name=model_name,
                                  tools=[])  # Tested with tools but not worked, returns empty json
    formatted_prompt = prompt.substitute(context=context, json=json_out, current_date=current_date)
    logger.debug(f"Prompt: {formatted_prompt}")
    response = model.generate_content(formatted_prompt)
    model_output = response.text
    logger.debug(f"Model output: {model_output}")
    json_out = extract_json(model_output)
    logger.debug(f"Model output json: {json_out}")
    return json_out, model_output


def generate_prefilled_form_url(json_out, google_form_url):
    query_params = []

    for entry in json_out:
        field_id = entry["field_id"]
        answer = entry.get("answer", "N/A")

        # Handle answers that are 'N/A'
        if answer == "N/A":
            continue

        # Handle answers that are arrays (e.g., checkboxes)
        if isinstance(answer, list):
            for ans in answer:
                query_params.append(f"{field_id}={urllib.parse.quote(ans)}")
            continue

        # Handle date and time types with ISO format prompt
        if entry.get("field_type") in ["Date", "Time"] and answer != "N/A":
            try:
                if entry.get("field_type") == "Date":
                    parsed_date = parser.parse(answer)
                    year = parsed_date.year
                    month = parsed_date.month
                    day = parsed_date.day
                    query_params.append(f"{field_id}_year={urllib.parse.quote(str(year))}")
                    query_params.append(f"{field_id}_month={urllib.parse.quote(str(month))}")
                    query_params.append(f"{field_id}_day={urllib.parse.quote(str(day))}")
                elif entry.get("field_type") == "Time":
                    parsed_time = parser.parse(answer).time()
                    hour = parsed_time.hour
                    minute = parsed_time.minute
                    query_params.append(f"{field_id}_hour={urllib.parse.quote(str(hour))}")
                    query_params.append(f"{field_id}_minute={urllib.parse.quote(str(minute))}")
            except ValueError:
                pass
            continue

        # Append the parameter for non-array and valid date/time answers
        query_params.append(f"{field_id}={urllib.parse.quote(str(answer))}")
    prefilled_url = f"{google_form_url}?{'&'.join(query_params)}"
    return prefilled_url
