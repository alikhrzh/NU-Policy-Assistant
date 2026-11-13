import psycopg
import streamlit as st

from src.db.postgres import ChunkCorpusError, save_search
from src.ui.ui_components import show_results
from src.retrieval.ui_search import MODEL_LABELS, search
from src.ui.ui_style import apply_style


EXAMPLES = (
    "Can I take more than 36 credits in one semester?",
    "Что будет, если я пропущу слишком много занятий?",
    "Where can I find the underload form?",
)

st.set_page_config(page_title="NU Policy Assistant", layout="centered")
apply_style()
st.html('<h1 class="policy-identity">NU Policy Assistant</h1>')
st.write("Search Nazarbayev University policy passages in English or Russian.")

st.caption("Try a question")
for example in EXAMPLES:
    st.button(example, on_click=st.session_state.update, kwargs={"policy_question": example})

with st.form("policy_search"):
    question = st.text_input("Question", key="policy_question", placeholder="Ask about a university policy")
    with st.expander("Advanced"):
        model_name = st.selectbox(
            "Embedding model", tuple(MODEL_LABELS), format_func=MODEL_LABELS.__getitem__
        )
        top_k = st.slider("Results shown", 1, 10, 5)
        pool_size = st.slider("Candidate pool size", 10, 50, 20)
        use_reranker = st.toggle("Rerank results", value=True)
    submitted = st.form_submit_button("Search policies", type="primary")

if submitted:
    question = question.strip()
    if not question:
        st.warning("Enter a question to search the policy corpus.")
    elif len(question) > 1000:
        st.warning("Shorten your question to 1,000 characters or fewer.")
    else:
        try:
            with st.spinner("Searching policy passages…"):
                results = search(question, top_k, pool_size, use_reranker, model_name=model_name)
            st.session_state.policy_results = (question, model_name, results)
        except (Exception, SystemExit) as error:
            st.error(f"Search failed with {MODEL_LABELS[model_name]}.")
            if isinstance(error, (FileNotFoundError, ValueError)) and str(error).startswith(("Restore ", "Run ")):
                st.write(str(error))
            elif isinstance(error, ChunkCorpusError):
                st.write(str(error))
            elif isinstance(error, psycopg.Error) or (
                isinstance(error, KeyError) and error.args == ("DATABASE_URL",)
            ):
                st.write("Check DATABASE_URL and confirm that the corpus is imported into PostgreSQL.")
            else:
                st.write("Check the local model weights and the prepared embedding cache.")
        else:
            chunk_ids = [chunk["chunk_id"] for chunk in results]
            try:
                save_search(question, chunk_ids, model_name, use_reranker)
            except (KeyError, psycopg.Error):
                st.warning("Search history could not be saved. Check the local PostgreSQL connection.")

if "policy_results" in st.session_state:
    searched_question, searched_model, results = st.session_state.policy_results
    st.subheader("Matching passages")
    st.text(searched_question, width="stretch")
    st.caption(MODEL_LABELS[searched_model])
    if results:
        show_results(results)
    else:
        st.info("No passages found.")
else:
    st.info("Search for a policy to see ranked passages and their source pages.")

st.caption(
    "Retrieval prototype. Results come from the document versions in this corpus and may be outdated; "
    "verify with the university's official sources. Independent project, not an official university service."
)
