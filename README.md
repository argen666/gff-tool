# Google Form Filler (Gff) Tool

The Google Form Filler (Gff) is a tool designed to automate the process of filling out Google Forms using context extracted from custom documents.

Gff is a smart assistant that knows exactly what to put in each field of the form, thanks to Google Gemini AI and learning from documents you provide.

## Features

- **Automatic Form Filling**: Fill out Google Forms automatically using context extracted from documents.
- **Google Gemini AI Integration**: Leverage the power of AI to understand and fill forms accurately.
- **Interactive Prompts**: Get prompted for additional context when necessary, ensuring comprehensive form filling.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or higher
- Obtain API key by following the [Google AI Quickstart Guide](https://ai.google.dev/tutorials/quickstart).

## Installation
1. Add GOOGLE_API_KEY to environment variables
2. Install the required Python packages:

```bash
pip install -r requirements.txt
```
## Usage

1. **Add Documents to context** (Optional):

To add context from a document or a directory of  documents, use the `--doc-add` flag:
```bash
python gff.py --doc-add path/to/your/document_or_directory
```

2. **Fill a Google Form**:

Simply run the tool and follow the interactive prompts:

```bash
python gff.py
```

The `--copilot` flag prompts users for additional input when the tool needs more context to accurately fill out a Google Form. This ensures higher accuracy and completeness in form submissions.
```bash
python gff.py --copilot
```

3. To enable debug mode for additional logs, use the `--debug` flag.

## Demo

Watch our demo video to see how it works.

[![Watch the Demo](http://img.youtube.com/vi/AeSELE88cJw/3.jpg)](https://youtu.be/AeSELE88cJw)

### Try It Yourself

Use the link below to access an example form featured in the demo video:

[Fake Hackathon Registration Form](https://forms.gle/HGg3VmA1GDAauUSX9)


