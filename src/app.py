import psycopg
import streamlit as st

from src.db.postgres import ChunkCorpusError, save_search
from src.generation.generate import generate_answer
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
            st.session_state.pop("policy_answer", None)
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
        if st.button("Generate answer"):
            with st.spinner("Generating an answer with local Ollama…"):
                st.session_state.policy_answer = generate_answer(searched_question, results[:5])
        if "policy_answer" in st.session_state:
            generated = st.session_state.policy_answer
            if generated["answer"]:
                st.markdown(generated["answer"])
                with st.expander("Answer sources"):
                    for number, source in generated["sources"].items():
                        first, last = source["page_start"], source["page_end"]
                        pages = f"p. {first}" if first == last else f"pp. {first}–{last}"
                        st.text(f"[{number}] {source['document_id']}, {pages}")
                        st.write(source["text"])
            for warning in generated["warnings"]:
                st.warning(warning)
        show_results(results)
    else:
        st.info("No passages found.")
else:
    st.info("Search for a policy to see ranked passages and their source pages.")

st.caption(
    "Results come from the document versions in this corpus and may be outdated; "
    "verify with the university's official sources. Independent project, not an official university service."
)
