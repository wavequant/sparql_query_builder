import requests
import pandas as pd
import io
import streamlit as st # For caching

# --- Wikidata Entity Search ---
@st.cache_data(ttl=3600) # Cache API results for 1 hour
def search_wikidata_entities(search_term, language="en", entity_type="item", limit=7):
    """
    Searches Wikidata for entities (items or properties) by label.
    Returns a list of tuples: (label, id, description).
    """
    API_ENDPOINT = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": language,
        "uselang": language,
        "search": search_term,
        "limit": limit,
        "type": entity_type
    }
    # It's good practice to set a User-Agent
    headers = {
        "User-Agent": "MyStreamlitSPARQLQueryBuilder/1.0 (Python requests; streamlit.io)"
    }
    try:
        response = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=10) # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        results = response.json()

        if "search" in results:
            formatted_results = []
            for item in results["search"]:
                label = item.get("label", "No label")
                item_id = item.get("id")
                description = item.get("description", "No description")
                if item_id: # Ensure there's an ID
                    formatted_results.append((label, item_id, description))
            return formatted_results
        return []
    except requests.exceptions.Timeout:
        st.error(f"Wikidata API request timed out for '{search_term}'.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching Wikidata for '{search_term}': {e}")
        return []
    except ValueError as e: # JSON decoding error
        st.error(f"Error decoding JSON from Wikidata API for '{search_term}': {e}")
        return []

# --- SPARQL Query Execution ---
def execute_sparql_query(query_string, endpoint_url, return_format_header="application/sparql-results+json"):
    """
    Executes a SPARQL query against the given endpoint.
    Returns a tuple: (pandas.DataFrame or None, raw_results_dict_or_str, error_message_str or None)
    """
    headers = {
        "Accept": return_format_header,
        "User-Agent": "MyStreamlitSPARQLQueryBuilder/1.0 (Python requests; streamlit.io)"
    }
    params = {
        "query": query_string,
        "format": "json" # This is often overridden by the Accept header for some endpoints
    }

    try:
        response = requests.get(endpoint_url, params=params, headers=headers, timeout=60) # 60s timeout for query
        response.raise_for_status()

        # Handle different content types, prioritize JSON for DataFrame conversion
        content_type = response.headers.get("Content-Type", "").lower()

        if "application/sparql-results+json" in content_type or "application/json" in content_type:
            raw_results = response.json()
            if "results" in raw_results and "bindings" in raw_results["results"]:
                bindings = raw_results["results"]["bindings"]
                if not bindings:
                    return pd.DataFrame(columns=raw_results.get("head", {}).get("vars", [])), raw_results, None
                
                # Extract data, being careful about missing keys or different structures
                data = []
                for item in bindings:
                    row = {}
                    for var_name in raw_results.get("head", {}).get("vars", []):
                        if var_name in item:
                            row[var_name] = item[var_name].get('value', None)
                        else:
                            row[var_name] = None # Handle OPTIONAL variables not bound
                    data.append(row)
                return pd.DataFrame(data), raw_results, None
            elif "boolean" in raw_results:  # ASK query
                return None, raw_results, None # DataFrame is None, pass raw boolean result
            else: # Other JSON structure
                return None, raw_results, "Unexpected JSON structure in SPARQL response."
        elif "application/sparql-results+xml" in content_type or "application/xml" in content_type:
            # Basic handling, could be parsed further with lxml if needed
            return None, response.text, "XML result received. Raw XML shown."
        elif "text/csv" in content_type:
            csv_string = response.text
            try:
                df = pd.read_csv(io.StringIO(csv_string))
                return df, csv_string, None
            except Exception as e_csv:
                 return None, csv_string, f"CSV result received, but failed to parse into DataFrame: {e_csv}"
        else: # Other content types
            return None, response.text, f"Received unexpected content type: {content_type}. Raw response shown."

    except requests.exceptions.Timeout:
        return None, None, f"Query timed out after 60 seconds at {endpoint_url}."
    except requests.exceptions.HTTPError as e_http:
        # Try to get more detailed error message from response body if available
        error_detail = e_http.response.text[:500] if e_http.response else str(e_http)
        return None, None, f"HTTP Error executing query: {e_http}. Detail: {error_detail}"
    except requests.exceptions.RequestException as e_req:
        return None, None, f"Request Exception executing query: {e_req}"
    except ValueError as e_json: # JSON decoding error for the query result itself
        return None, response.text if 'response' in locals() else None, f"Error decoding JSON query result: {e_json}. Raw response might be available."
    except Exception as e:
        return None, None, f"An unexpected error occurred during query execution: {e}"