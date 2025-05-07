import streamlit as st
import pandas as pd
import pyperclip
from sparql_utils import execute_sparql_query, search_wikidata_entities
from query_templates import WIKIDATA_TEMPLATES

st.set_page_config(layout="wide", page_title="SPARQL Query Builder")

SEARCH_TYPE_DISPLAY_OPTIONS = ("Клас (QID)", "Предикат (PID)")
DEFAULT_TEMPLATE_KEY = "Празен"
TEXT_AREA_KEY = "query_text_main_area_ta_widget_state"

def init_session_state():
    defaults = {
        'current_query_text': "",
        TEXT_AREA_KEY: "",
        'selected_endpoint_url': "https://query.wikidata.org/sparql",
        'last_successful_query': "",
        'last_endpoint_for_success': "",
        'last_loaded_template_name': DEFAULT_TEMPLATE_KEY,
        'search_entity_type_param': st.query_params.get("search_type", "item"),
        'query_executed_in_this_run': False,
        'results_df': None,
        'raw_results_response': None,
        'query_error_message': None,
        'endpoint_selectbox_key_value': "Wikidata"
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    if "search_term_input_key" not in st.session_state:
        st.session_state.search_term_input_key = st.query_params.get("search_term", "")

    if st.session_state.search_entity_type_param not in ["item", "property"]:
        st.session_state.search_entity_type_param = "item"

init_session_state()

ENDPOINTS_AVAILABLE = {
    "Wikidata": "https://query.wikidata.org/sparql",
    "Europeana": "http://sparql.europeana.eu/",
}

def update_search_type():
    selected_display_value = st.session_state.search_type_radio_widget_key
    if selected_display_value == SEARCH_TYPE_DISPLAY_OPTIONS[0]: new_type = "item"
    elif selected_display_value == SEARCH_TYPE_DISPLAY_OPTIONS[1]: new_type = "property"
    else: new_type = "item"
    if new_type != st.session_state.search_entity_type_param:
        st.session_state.search_entity_type_param = new_type
        st.query_params["search_type"] = new_type

def handle_endpoint_change():
    selected_name = st.session_state.endpoint_selector_widget_key
    new_url = ENDPOINTS_AVAILABLE.get(selected_name)
    if new_url and new_url != st.session_state.selected_endpoint_url:
        st.session_state.selected_endpoint_url = new_url
        st.session_state.endpoint_selectbox_key_value = selected_name
        st.session_state.query_executed_in_this_run = False
        st.session_state.results_df = None
        st.session_state.raw_results_response = None
        st.session_state.query_error_message = None

def clear_all_query_related_state():
    st.session_state.current_query_text = ""
    st.session_state[TEXT_AREA_KEY] = ""
    st.session_state.last_loaded_template_name = DEFAULT_TEMPLATE_KEY
    st.session_state.last_successful_query = ""
    st.session_state.last_endpoint_for_success = ""
    st.session_state.query_executed_in_this_run = False
    st.session_state.results_df = None
    st.session_state.raw_results_response = None
    st.session_state.query_error_message = None

def search_term_changed():
    st.query_params["search_term"] = st.session_state.search_term_input_key
    st.query_params["search_type"] = st.session_state.search_entity_type_param

st.title("SPARQL Query Builder & Executor")

with st.sidebar:
    st.header("Настройки")
    st.subheader("SPARQL Endpoint (Сървър)")
    current_endpoint_name_for_select = st.session_state.endpoint_selectbox_key_value
    if current_endpoint_name_for_select not in ENDPOINTS_AVAILABLE:
        current_endpoint_name_for_select = list(ENDPOINTS_AVAILABLE.keys())[0]
        st.session_state.endpoint_selectbox_key_value = current_endpoint_name_for_select
        st.session_state.selected_endpoint_url = ENDPOINTS_AVAILABLE[current_endpoint_name_for_select]
    st.selectbox(
        "Избери Endpoint:", options=list(ENDPOINTS_AVAILABLE.keys()),
        key="endpoint_selector_widget_key", on_change=handle_endpoint_change,
        index=list(ENDPOINTS_AVAILABLE.keys()).index(current_endpoint_name_for_select)
    )
    custom_endpoint_input = st.text_input(
        "Или въведи друг endpoint URL:", value=st.session_state.selected_endpoint_url,
        key="custom_endpoint_input_ti"
    )
    if custom_endpoint_input != st.session_state.selected_endpoint_url:
        st.session_state.selected_endpoint_url = custom_endpoint_input
        found_name = next((name for name, url in ENDPOINTS_AVAILABLE.items() if url == custom_endpoint_input), "Custom")
        st.session_state.endpoint_selectbox_key_value = found_name

    st.markdown("---")
    st.subheader("Wikidata Entity Search")
    st.caption("Търси Wikidata QIDs (класове) и PIDs (предикати).")

    current_search_type_idx = 1 if st.session_state.search_entity_type_param == "property" else 0
    st.radio(
        "Търси:", SEARCH_TYPE_DISPLAY_OPTIONS, index=current_search_type_idx,
        horizontal=True, key="search_type_radio_widget_key", on_change=update_search_type
    )

    prefix_to_use = "wd:" if st.session_state.search_entity_type_param == "item" else "wdt:"

    st.text_input(
        f"Търси за {st.session_state.search_entity_type_param}s",
        key="search_term_input_key", 
        on_change=search_term_changed 
    )

    if st.session_state.search_term_input_key: 
        if st.query_params.get("search_type") != st.session_state.search_entity_type_param:
            st.query_params["search_type"] = st.session_state.search_entity_type_param
        if st.query_params.get("search_term") != st.session_state.search_term_input_key:
            st.query_params["search_term"] = st.session_state.search_term_input_key

        with st.expander("Резултати от търсенето", expanded=True):
            with st.spinner(f"Търсене в Wikidata за '{st.session_state.search_term_input_key}' като {st.session_state.search_entity_type_param}..."):
                results = search_wikidata_entities(
                    st.session_state.search_term_input_key, 
                    entity_type=st.session_state.search_entity_type_param
                )
            if results:

                for label, item_id, description in results:
                    col1_res, col2_res = st.columns([3, 1])
                    with col1_res: st.markdown(f"**{label}** (`{item_id}`)<br><small>{description}</small>", unsafe_allow_html=True)
                    with col2_res:
                        id_to_copy = f"{prefix_to_use}{item_id}"
                        if st.button(f"Копирай код", key=f"copy_{item_id}_btn"):
                            try:
                                pyperclip.copy(id_to_copy)
                                st.toast(f"Копирано '{id_to_copy}' в клипборда!", icon="📋")
                            except pyperclip.PyperclipException as e:
                                st.error(f"Не може да се копира в клипборда, грешка: {e}.")
                                st.info(f"Копирай ръчно: {id_to_copy}")
            elif st.session_state.search_term_input_key: # Check again
                st.info("Няма намерени резултати за твоето търсене.")
    st.markdown("---")
    if st.button("Изчисти редактора за заявки", key="clear_query_btn_main_sidebar"):
        clear_all_query_related_state()
        st.rerun()


col_query, col_results = st.columns(2)

with col_query:
    st.subheader("Напиши своята SPARQL заявка")
    is_wikidata_endpoint = "wikidata.org" in st.session_state.selected_endpoint_url
    
    if is_wikidata_endpoint:
        current_template_idx = 0
        if st.session_state.last_loaded_template_name in WIKIDATA_TEMPLATES:
            if st.session_state.last_loaded_template_name in list(WIKIDATA_TEMPLATES.keys()):
                current_template_idx = list(WIKIDATA_TEMPLATES.keys()).index(st.session_state.last_loaded_template_name)
            else: st.session_state.last_loaded_template_name = DEFAULT_TEMPLATE_KEY
        else: st.session_state.last_loaded_template_name = DEFAULT_TEMPLATE_KEY

        selected_template_name_input = st.selectbox(
            "Зареди WIKIDATA Шаблон:", options=list(WIKIDATA_TEMPLATES.keys()),
            index=current_template_idx, key="template_selector_main_sb"
        )
        if selected_template_name_input != st.session_state.last_loaded_template_name:
            template_text = WIKIDATA_TEMPLATES.get(selected_template_name_input, "").strip()
            st.session_state.current_query_text = template_text
            st.session_state[TEXT_AREA_KEY] = template_text
            st.session_state.last_loaded_template_name = selected_template_name_input
            st.session_state.query_executed_in_this_run = False
            st.session_state.results_df = None
            st.session_state.raw_results_response = None
            st.session_state.query_error_message = None
            st.rerun()

    st.text_area(
        "SPARQL Заявка:",
        height=350,
        key=TEXT_AREA_KEY, 
        help="Въведи своята SPARQL заявка..."
    )

    if st.session_state[TEXT_AREA_KEY] != st.session_state.current_query_text:
        st.session_state.current_query_text = st.session_state[TEXT_AREA_KEY]
        st.session_state.query_executed_in_this_run = False
        st.session_state.results_df = None
        st.session_state.raw_results_response = None
        st.session_state.query_error_message = None

    if st.button("⚡ ИЗПЪЛНИ ЗАЯВКА", type="primary", use_container_width=True, key="execute_query_btn"):
        st.session_state.query_executed_in_this_run = True
        st.session_state.results_df = None 
        st.session_state.raw_results_response = None
        st.session_state.query_error_message = None

        if not st.session_state.current_query_text.strip(): 
            st.session_state.query_error_message = "Заявката е празна. Въведи текст."
        elif not st.session_state.selected_endpoint_url.strip():
            st.session_state.query_error_message = "Няма избрана крайна точка (сървър) за заявката."
        else:
            query_to_run = st.session_state.current_query_text
            endpoint_to_run = st.session_state.selected_endpoint_url
            with st.spinner(f"Изпълнявам заявка с {endpoint_to_run}..."):
                df_res, raw_res, err_msg = execute_sparql_query(query_to_run, endpoint_to_run)
            st.session_state.results_df = df_res
            st.session_state.raw_results_response = raw_res
            st.session_state.query_error_message = err_msg
            if not err_msg and (df_res is not None or (raw_res and "boolean" in raw_res)):
                st.session_state.last_successful_query = query_to_run
                st.session_state.last_endpoint_for_success = endpoint_to_run

with col_results:
    st.subheader("Резултати")
    if st.session_state.query_executed_in_this_run:
        if st.session_state.query_error_message:
            st.error(f"Грешка при изпълнение: {st.session_state.query_error_message}")
            if st.session_state.raw_results_response:
                with st.expander("Пълен текст на грешката:"): st.code(str(st.session_state.raw_results_response), language="json" if isinstance(st.session_state.raw_results_response, dict) else "text")
        elif st.session_state.results_df is not None:
            if not st.session_state.results_df.empty: st.success(f"Заявката е изпълнена. Попълнени {len(st.session_state.results_df)} реда.")
            else: st.info("Заявката е изпълнена, но няма съвпадащи резултати за нея.")
            st.dataframe(st.session_state.results_df, use_container_width=True)
            if st.session_state.raw_results_response:
                with st.expander("Върнат JSON"): st.json(st.session_state.raw_results_response)
        elif st.session_state.raw_results_response and "boolean" in st.session_state.raw_results_response:
            st.success("Заявката е изпълнена успешно!")
            st.metric(label="Резултат", value=str(st.session_state.raw_results_response["boolean"]))
            if st.session_state.raw_results_response:
                with st.expander("Върнат JSON"): st.json(st.session_state.raw_results_response)
        elif st.session_state.raw_results_response:
            st.info("Заявката е изпълнена успешно!")
            st.code(str(st.session_state.raw_results_response), language="text")
        else: st.info("Заявката бе обработена.")
    else:
        if st.session_state.last_successful_query and not st.session_state.current_query_text:
            st.caption(f"Последна успешна заявка (за {st.session_state.last_endpoint_for_success}):")
            st.code(st.session_state.last_successful_query, language="sparql")
        elif not st.session_state.query_executed_in_this_run:
            st.info("Резултатите ще се появят тук, след като се изпълни заявката.")

st.markdown("---")
st.caption("Дарин Крумов, Самуил Ганев - 2025 ЕТМД")