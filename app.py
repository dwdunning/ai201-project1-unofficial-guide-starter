"""
Milestone 5 — Gradio Web Interface

A simple web UI that wraps the RAG pipeline from rag.py.
Calls ask() from rag.py — does not duplicate any retrieval or generation logic.

Run with:
    python app.py
Then open the URL printed in the terminal (usually http://127.0.0.1:7860).
"""

import gradio as gr

from rag import ask


def respond(question: str) -> tuple[str, str]:
    """Bridge between the Gradio UI and the RAG pipeline."""
    if not question.strip():
        return "", ""

    result = ask(question)

    sources_text = (
        "\n".join(result["sources"]) if result["sources"] else "No relevant sources found"
    )
    return result["answer"], sources_text


with gr.Blocks(title="SSU CS Professor Reviews") as demo:
    gr.Markdown("## SSU CS Professor Review Assistant")
    gr.Markdown(
        "Ask a question about Computer Science professors at Sonoma State University. "
        "Answers are grounded in student reviews from Rate My Professors."
    )

    question_box = gr.Textbox(
        label="Your question",
        placeholder="e.g. What do students say about CS315 with Ali Kooshesh?",
        lines=2,
    )
    ask_btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(label="Answer", lines=8, interactive=False)
    sources_box = gr.Textbox(label="Sources", lines=4, interactive=False)

    ask_btn.click(fn=respond, inputs=question_box, outputs=[answer_box, sources_box])
    question_box.submit(fn=respond, inputs=question_box, outputs=[answer_box, sources_box])


if __name__ == "__main__":
    demo.launch()
