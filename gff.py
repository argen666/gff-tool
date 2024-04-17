import argparse
import os, re
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from rich.console import Console
from embedchain import App
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from form_loader import load_form_source
from form_processor import extract_form_data, filling_out_form, generate_prefilled_form_url
from logger import enable_debug_logging
from prompts import UNANSWERED_PROMPT

app = App.from_config(config_path="config.yaml")
console = Console()


def get_user_context(context_request=""):
    console.print("📝 [bold cyan]Your Input is Requested[/bold cyan]")
    console.print(
        "[italic]You can add any context or details you think are relevant. If you don't have anything to add, simply press [Enter].[/italic]")
    if context_request:
        console.print(Markdown(context_request))
    # Visual separator
    console.print(Panel.fit("[bold green]Your Response Below[/bold green]", border_style="green"))
    # User input
    context = Prompt.ask(">").strip()
    return context


def get_google_form_url():
    """
    Prompts the user for a Google Form URL and validates the input.
    Returns a valid Google Form URL.
    """
    url_pattern = re.compile(
        r'(https://docs\.google\.com/forms/d/e/[a-zA-Z0-9_-]+/viewform.*)|(https://forms\.gle/[a-zA-Z0-9_-]+)'
    )

    url = Prompt.ask("[bold cyan]\nPlease enter the Google Form URL[/bold cyan]").strip()
    if url_pattern.match(url):
        parsed_url = urlparse(url)
        clean_url = urlunparse(parsed_url._replace(query=""))
        console.print("\nGoogle Form URL accepted\n", style="bold green")
        return clean_url
    else:
        raise ValueError("Invalid URL. Please enter a valid Google Form URL.")


def collect_files(path):
    """
    Returns a list of file paths. If 'path' is a directory, returns all file paths in the directory
    """
    files_list = []
    if os.path.isdir(path):
        files = list(Path(path).glob('*'))
        if not files:
            raise FileNotFoundError(f"No files found in the directory: {path}")
        for file in files:
            files_list.append(str(file))
    elif os.path.isfile(path):
        files_list.append(path)
    else:
        raise ValueError(f"The specified path '{path}' is not a valid file or directory.")

    return files_list


def process_file(file_path):
    app.add(file_path)
    console.print(f"Processing file: {file_path}")


def get_unanswered_questions(json_out):
    unanswered_questions = []
    for entry in json_out:
        if entry.get("answer", "N/A") == "N/A":
            unanswered_questions.append(entry)
    return unanswered_questions


def fill_google_form(google_form_url, user_context, copilot=False):
    # Getting form data...
    with console.status("Getting form data...", spinner="bouncingBar"):
        html_content, form_full_url = load_form_source(google_form_url)
    console.print("\nGetting form data...Success\n", style="bold green")
    # Analyzing form data...
    with console.status("Analyzing form data...", spinner="bouncingBar"):
        json_out = extract_form_data(html_content)
    console.print("\nAnalyzing form data...Success\n", style="bold green")
    # Filling out...
    with console.status("Filling out the form...", spinner="bouncingBar"):
        json_out, _ = filling_out_form(json_out, user_context)
    if copilot:
        json_unanswered = get_unanswered_questions(json_out)
        if json_unanswered:
            with console.status("Analyzing answers...", spinner="bouncingBar"):
                _, unanswered_out = filling_out_form(json_unanswered, user_context, prompt=UNANSWERED_PROMPT)
            new_user_context = get_user_context(unanswered_out)
            with console.status("Filling out the form...", spinner="bouncingBar"):
                json_unanswered_out, _ = filling_out_form(json_unanswered,
                                                          "\n".join([user_context, unanswered_out, new_user_context]))
            json_out = json_out + json_unanswered_out
    console.print("\nFilling out the form...Success\n", style="bold green")
    with console.status("Generating result...", spinner="bouncingBar"):
        url = generate_prefilled_form_url(json_out, form_full_url)
    console.print("✅ Success! Open the link:", style="bold green")
    console.print(url)


def main():
    parser = argparse.ArgumentParser(description="gff: Google Form Filler Tool")
    parser.add_argument('--doc-add', type=str,
                        help="Path to a document or directory of documents to the context [OPTIONAL]")
    parser.add_argument('--copilot', action='store_true',
                        help="Requests additional context when necessary [OPTIONAL]")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode for additional logs [OPTIONAL]")

    console.print("\n 🚀 Welcome to Gff tool!\n", style="bold green")
    try:
        args = parser.parse_args()
        if args.debug:
            enable_debug_logging()
        if args.doc_add:
            files = collect_files(args.doc_add)
            console.print("\nFound files:")
            console.print("\n".join(f"- {file}" for file in files))
            confirm_add = Confirm.ask("Do you want to add these files? [y/N]")
            if not confirm_add:
                console.print("No files added. Exiting.", style="bold green")
                return
            with console.status("Adding files to vector store", spinner="bouncingBar"):
                [process_file(file) for file in files]
            console.print("\nAdding files to vector store...Success\n", style="bold green")
            continue_to_form = Confirm.ask("Do you want to continue to form filling? [y/N]")
            if not continue_to_form:
                console.print("Exiting. Have a great day!", style="bold green")
                return

        google_form_url = get_google_form_url()
        user_context = get_user_context()
        fill_google_form(google_form_url, user_context, args.copilot)

    except (FileNotFoundError, ValueError) as e:
        console.print(e, style="bold red")


if __name__ == "__main__":
    main()
