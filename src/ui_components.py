from html import escape

import streamlit as st


def show_results(results):
    maximums = {
        key: max((abs(chunk.get(key, 0)) for chunk in results), default=0)
        for key in ("score", "rerank_score")
    }

    for rank, chunk in enumerate(results, start=1):
        document_id = chunk["document_id"]
        title = document_id.replace("-", " ").title()
        start, end = chunk["page_start"], chunk["page_end"]
        pages = f"p. {start}" if start == end else f"pp. {start}–{end}"
        movement = f" · from #{chunk['original_rank']}" if "rerank_score" in chunk else ""

        with st.container(border=True):
            st.subheader(f"{rank}. {title}")
            st.html(f'<div class="policy-meta">{escape(document_id)} · {pages}{movement}</div>')
            passage = chunk["text"]
            st.text(passage[:300] + ("…" if len(passage) > 300 else ""), width="stretch")
            with st.expander("Full passage"):
                st.text(passage, width="stretch")
            for key, label in (("score", "Retrieval"), ("rerank_score", "Reranking")):
                if key in chunk:
                    score = chunk[key]
                    width = abs(score) / maximums[key] * 100 if maximums[key] else 0
                    st.html(
                        f'<div class="policy-meta">{label} relative score {score:.4f}</div>'
                        f'<div class="policy-meter" aria-hidden="true"><span style="width:{width:.2f}%"></span></div>'
                    )

    if results:
        timing = results[0]["timing_ms"]
        st.caption(
            f"Retrieval {timing['retrieval']:.0f} ms · "
            f"Reranking {timing['reranking']:.0f} ms · "
            f"Total {timing['total']:.0f} ms · original search timing"
        )
        st.caption("Scores are relative, not probabilities. Bars show score magnitude within this result set.")
