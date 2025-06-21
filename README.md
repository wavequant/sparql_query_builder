# SPARQL Query Builder & Executor

A Streamlit web application designed to help users build, execute, and explore SPARQL queries against various public endpoints like Wikidata and Europeana. It features a Wikidata entity search to help find QIDs and PIDs, query templates, and a clear display for query results.

<!-- Optional: Add a screenshot or GIF of the application in action here -->
<!-- e.g., ![App Screenshot](path/to/your/screenshot.png) -->

## Features

*   **Endpoint Selection:**
    *   Choose from predefined SPARQL endpoints (e.g., Wikidata, Europeana).
    *   Specify a custom endpoint URL for flexibility.
*   **Wikidata Entity Search (Sidebar):**
    *   Search for Wikidata Items (QIDs) and Properties (PIDs) by their labels.
    *   View search results with labels, IDs, and descriptions.
    *   Quickly copy the prefixed ID (e.g., `wd:Q123` or `wdt:P321`) to the clipboard for use in queries.
    *   Search results are cached for efficiency.
*   **SPARQL Query Editor:**
    *   Manually write or paste SPARQL queries into a dedicated text area.
    *   Load predefined query templates (currently available for Wikidata) to get started or learn common patterns.
    *   Option to easily clear the query editor and reset related state.
*   **Query Execution:**
    *   Execute the constructed SPARQL query against the currently selected endpoint.
    *   Loading indicators provide feedback during query execution.
*   **Results Display:**
    *   View `SELECT` query results in an interactive table (powered by Pandas DataFrame).
    *   Inspect the raw JSON response received from the SPARQL endpoint.
    *   Clearly display boolean results for `ASK` queries.
    *   Informative error messages and raw error details are shown if a query fails.
*   **Persistent Session State:**
    *   User inputs such as the current query, selected endpoint, and search terms are maintained within the browser session for a smoother experience.

## Tech Stack

*   **Framework:** [Streamlit](https://streamlit.io/) (for building the interactive web application)
*   **Programming Language:** Python
*   **Data Handling:** [Pandas](https://pandas.pydata.org/) (for tabular data display)
*   **HTTP Requests:** [Requests](https://requests.readthedocs.io/en/latest/) (for executing SPARQL queries and interacting with the Wikidata API)
*   **Clipboard Integration:** [Pyperclip](https://pyperclip.readthedocs.io/)
*   **Query Templates:** Stored as Python dictionaries.

## Setup and Installation

### Prerequisites

*   Python 3.8 or higher
*   `pip` (Python package installer)
*   `git` (for cloning the repository)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/wavequant/sparql_query_builder.git
    cd sparql_query_builder
    ```

2.  **Create and activate a virtual environment (recommended):**
    *   On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    Navigate to the project directory (if not already there) and run:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

Once the setup is complete and your virtual environment is activated, run the Streamlit application using the following command in your terminal:

```bash
streamlit run app_annotated.py
