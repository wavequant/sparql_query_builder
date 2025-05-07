import requests
import pandas as pd
import io
import streamlit as st 

@st.cache_data(ttl=3600)
def search_wikidata_entities(search_term, language="en", entity_type="item", limit=7):
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
    headers = {
        "User-Agent": "MyStreamlitSPARQLQueryBuilder/1.0 (Python requests; streamlit.io)"
    }
    try:
        response = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=10) # Added timeout
        response.raise_for_status() 
        results = response.json()

        if "search" in results:
            formatted_results = []
            for item in results["search"]:
                label = item.get("label", "No label")
                item_id = item.get("id")
                description = item.get("description", "No description")
                if item_id: 
                    formatted_results.append((label, item_id, description))
            return formatted_results
        return []
    except requests.exceptions.Timeout:
        st.error(f"Wikidata API request timed out for '{search_term}'.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching Wikidata for '{search_term}': {e}")
        return []
    except ValueError as e: 
        st.error(f"Error decoding JSON from Wikidata API for '{search_term}': {e}")
        return []

def execute_sparql_query(query_string, endpoint_url, return_format_header="application/sparql-results+json"):

    headers = {
        "Accept": return_format_header,
        "User-Agent": "MyStreamlitSPARQLQueryBuilder/1.0 (Python requests; streamlit.io)"
    }
    params = {
        "query": query_string,
        "format": "json" 
    }

    try:
        response = requests.get(endpoint_url, params=params, headers=headers, timeout=60) # 60s timeout for query
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()

        if "application/sparql-results+json" in content_type or "application/json" in content_type:
            raw_results = response.json()
            if "results" in raw_results and "bindings" in raw_results["results"]:
                bindings = raw_results["results"]["bindings"]
                if not bindings:
                    return pd.DataFrame(columns=raw_results.get("head", {}).get("vars", [])), raw_results, None
                
                data = []
                for item in bindings:
                    row = {}
                    for var_name in raw_results.get("head", {}).get("vars", []):
                        if var_name in item:
                            row[var_name] = item[var_name].get('value', None)
                        else:
                            row[var_name] = None 
                    data.append(row)
                return pd.DataFrame(data), raw_results, None
            elif "boolean" in raw_results: 
                return None, raw_results, None 
            else:
                return None, raw_results, "Неочакван JSON."
        elif "application/sparql-results+xml" in content_type or "application/xml" in content_type:
            return None, response.text, "XML Получен."
        elif "text/csv" in content_type:
            csv_string = response.text
            try:
                df = pd.read_csv(io.StringIO(csv_string))
                return df, csv_string, None
            except Exception as e_csv:
                 return None, csv_string, f"CSV получен, но грешка в парсването му в pandas: {e_csv}"
        else:
            return None, response.text, f"Незнаен тип съдържание: {content_type}. Суров респонс показвам."

    except requests.exceptions.Timeout:
        return None, None, f"60-секундовият таймаут мина за: {endpoint_url}."
    except requests.exceptions.HTTPError as e_http:
        error_detail = e_http.response.text[:500] if e_http.response else str(e_http)
        return None, None, f"HTTP грешка за заявка: {e_http}. Детайли: {error_detail}"
    except requests.exceptions.RequestException as e_req:
        return None, None, f"Рекуест грешка за заявка: {e_req}"
    except ValueError as e_json: 
        return None, response.text if 'response' in locals() else None, f"Грешка при обработка на JSON: {e_json}. Възможно е да има суров резултат."
    except Exception as e:
        return None, None, f"Незнайна грешка по време на изпълнението на заявката: {e}"