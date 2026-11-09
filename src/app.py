import streamlit as st

from ui_components import show_results
from ui_search import load_pipeline, search
from ui_style import apply_style


EXAMPLES = (
    "Can I take more than 36 credits in one semester?",
    "Что будет, если я пропущу слишком много занятий?",
    "Where can I find the underload form?",
)

st.set_page_config(page_title="NU Policy Assistant", layout="centered")
apply_style()
st.html('<h1 class="policy-identity">NU Policy Assistant</h1>')
st.write("Search Nazarbayev University policy passages in English or Russian.")

try:
    with st.spinner("Loading local search models and warming up…"):
        load_pipeline()
except (Exception, SystemExit) as error:
    st.error("Could not start policy search.")
    if isinstance(error, (FileNotFoundError, ValueError)) and str(error).startswith(("Restore ", "Run ")):
        st.write(str(error))
    else:
        st.write(
            "Check that the prepared chunks and BGE-M3 embeddings are present "
            "and that BAAI/bge-m3 and BAAI/bge-reranker-v2-m3 are in your local model cache."
        )
    st.stop()

st.caption("Try a question")
for example in EXAMPLES:
    st.button(example, on_click=st.session_state.update, kwargs={"policy_question": example})

with st.form("policy_search"):
    question = st.text_input("Question", key="policy_question", placeholder="Ask about a university policy")
    with st.expander("Advanced"):
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
                results = search(question, top_k, pool_size, use_reranker)
            st.session_state.policy_results = (question, results)
        except (Exception, SystemExit):
            st.error("Search failed. Check that the chunk files and BGE-M3 embedding cache match, then try again.")

if "policy_results" in st.session_state:
    searched_question, results = st.session_state.policy_results
    st.subheader("Matching passages")
    st.text(searched_question, width="stretch")
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
