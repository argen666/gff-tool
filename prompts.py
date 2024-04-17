from string import Template

ANALYZE_FORM_PROMPT = Template("""
Task: Convert the provided Google Form HTML code into a JSON representation following specific rules.

HTML Form Characteristics:

-Field IDs are found in the "name" attribute of input elements, prefixed with "entry.".
-The "textarea" element is used for Paragraph question types.
-Checkbox fields have multiple "input" nodes with the same values and an extra input element with a "_sentinel" suffix in its ID. Duplicate nodes should be ignored.

-The form consists of various field types: Short Text, Paragraph, Multiple Choice, Checkbox, List of Choices, File Upload, Scale, Multiple Choice Grid, Tick Box Grid, Date, Time.

Output Format:

-Return a JSON array where each object represents a form field.
-Each object should include field_id, field_type, field_text, and field_options (if applicable).
-field_text should include both the question title and description. For Grid questions, include the row questions as part of field_text.
-For fields with options (e.g., Multiple Choice, Checkbox), include an array of options in field_options.

Example JSON Object:

[
  {
    "field_id": "entry.xxxx",
    "field_type": "Field Type",
    "field_text": "Question Title and Description",
    "field_options": ["Option1", "Option2"]
  }
]

Instructions:

-Analyze the provided HTML code to identify form fields and their attributes.
-Construct a JSON representation following the specified format.
-Ensure the JSON is valid and can be parsed using json.loads in Python.

-Current date is ${current_date}

HTML Form Code:
${html_content}
""")

QA_PROMPT = Template("""
Task: Process the provided JSON containing multiple form questions and provide concise answers based on the context given. The JSON is structured as an output from a previous task, detailing various form fields and their characteristics.

Instructions:

Read through the JSON to understand the questions, their types, and options (if any).
Provide answers:
For open-ended questions (e.g., Short Text, Paragraph), provide a brief answer, typically a single word or a short sentence.
For questions with options (e.g., Multiple Choice, Checkbox, List of Choices), select your answer directly from the provided options. If none of the options apply based on the context, respond with "N/A".
For grid questions (Multiple Choice Grid, Tick Box Grid), provide answers according to the row questions, selecting from the provided options for each row.
For Date and Time questions answer in ISO 8601 format
If the answer cannot be determined from the provided context, respond with "N/A". Do not attempt to infer or create an answer.
Update the JSON by adding an "answer" field to each question object with your response.

-Current date is ${current_date}

Context: 
${context}

Questions JSON:
${json}

Updated Questions JSON with Answers:

Provide the updated JSON here, with an "answer" field added to each question object.
""")

UNANSWERED_PROMPT = Template("""
Please review the provided survey responses and identify any fields that have been left unanswered, marked as "N/A".
For each of these fields, generate a clear and concise directive that asks the user for the needed information in a format that allows for all responses to be provided in a single line of natural language.
If a field involves choices, please rephrase the directive to allow the user to specify their choices in a natural, conversational manner within the same line.

-Current date is ${current_date}

Context: 
${context}

Unanswered Fields:
${json}

Instead of creating separate questions for each unanswered field, formulate a single, comprehensive directive that encompasses all the information gaps. This directive should be clear and concise, guiding the user to provide all the missing information in one line of natural language. For example, if there are unanswered fields for "Favorite Color" and "Preferred Contact Method", the directive could be:

"Please tell us your favorite color and how you'd prefer to be contacted, all in one line."

This approach ensures the responses are suitable for a simple environment where users are expected to provide their answers in a single, straightforward input.
""")
