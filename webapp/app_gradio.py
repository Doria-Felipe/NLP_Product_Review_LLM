import re
import json
import tempfile
from pathlib import Path
import gradio as gr
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------- Model ----------------
GEN_MODEL_NAME = "google/flan-t5-base"
device = "cuda" if torch.cuda.is_available() else "cpu"

dtype = torch.float16 if device == "cuda" else torch.float32
tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(
    GEN_MODEL_NAME,
    torch_dtype=dtype
).to(device)
model.eval()

print("Device:", device)

STATE = {"df": None}

# ---------------- Clean complaint keywords ----------------
STOP = {"don", "didn", "doesn", "dont", "isn", "wasn", "weren",
        "cant", "couldn", "wouldn", "buy"}

def prettify_reason(reason: str) -> str:
    r = (reason or "").strip()
    if not r:
        return "No clear reason provided."

    if ";" not in r and len(r.split()) > 5:
        return r

    toks = [t.strip().lower() for t in r.split(";") if t.strip()]
    toks = [t for t in toks if len(t) >= 3 and t not in STOP]

    seen = set()
    cleaned = []
    for t in toks:
        if t not in seen:
            seen.add(t)
            cleaned.append(t)

    cleaned = cleaned[:6]

    if not cleaned:
        return "Negative feedback appears general without a clear recurring issue."

    return "Negative reviews repeatedly mention: " + ", ".join(cleaned) + "."

# ---------------- Brief parsing ----------------
def parse_brief(brief: str):
    b = (brief or "").replace("\r\n", "\n").replace("\r", "\n").strip()

    cat = "Category"
    m = re.search(r"^\s*CATEGORY:\s*(.+?)\s*$", b, flags=re.MULTILINE)
    if m:
        cat = m.group(1).strip()

    top3 = []
    top_match = re.search(
        r"TOP 3 PRODUCTS:\s*(.*?)(?:\n\s*WORST PRODUCT:|\Z)",
        b,
        flags=re.DOTALL | re.IGNORECASE
    )
    top_block = top_match.group(1).strip() if top_match else ""

    if top_block:
        chunks = re.split(r"\n\s*(?=\d+\)\s)", "\n" + top_block)
        for ch in chunks:
            ch = ch.strip()
            if not ch:
                continue
            lines = [ln.strip() for ln in ch.split("\n") if ln.strip()]
            header = re.sub(r"^\d+\)\s*", "", lines[0]).strip()
            name = header.split("|")[0].strip()

            rating = None
            reviews = None
            mr = re.search(r"rating\s*=\s*([0-9.]+)", header, flags=re.IGNORECASE)
            mv = re.search(r"reviews\s*=\s*(\d+)", header, flags=re.IGNORECASE)
            if mr: rating = float(mr.group(1))
            if mv: reviews = int(mv.group(1))

            complaints = ""
            for ln in lines[1:]:
                if ln.lower().startswith("complaints:"):
                    complaints = ln.split(":", 1)[1].strip()
                    break

            top3.append({
                "name": name,
                "rating": rating,
                "reviews": reviews,
                "complaints": complaints
            })

    worst = {"name": "", "rating": None, "reviews": None, "reason": ""}
    w = re.search(r"WORST PRODUCT:\s*(.+)", b, flags=re.IGNORECASE)
    if w:
        wline = w.group(1).strip().split("\n")[0]
        worst["name"] = wline.split("|")[0].strip()
        mr = re.search(r"rating\s*=\s*([0-9.]+)", wline, flags=re.IGNORECASE)
        mv = re.search(r"reviews\s*=\s*(\d+)", wline, flags=re.IGNORECASE)
        if mr: worst["rating"] = float(mr.group(1))
        if mv: worst["reviews"] = int(mv.group(1))

    r = re.search(r"avoid because:\s*(.+)\s*$", b, flags=re.IGNORECASE | re.MULTILINE)
    if r:
        worst["reason"] = r.group(1).strip()

    return cat, top3, worst

# ---------------- Summary generation ----------------
@torch.inference_mode()
def generate_summary_from_brief(brief: str) -> str:
    cat, top3, worst = parse_brief(brief)

    lines = [f"Category: {cat}."]
    for p in top3:
        lines.append(
            f"{p['name']} has rating {p['rating']} from {p['reviews']} reviews."
        )

    if worst["name"]:
        lines.append(
            f"The lowest rated is {worst['name']} with rating {worst['rating']} from {worst['reviews']} reviews."
        )

    facts = "\n".join(lines)

    prompt = f"""Write 2 short natural paragraphs for shoppers.

Use ONLY the facts below.

FACTS:
{facts}
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384).to(device)

    out = model.generate(
        **inputs,
        max_new_tokens=140,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        repetition_penalty=1.15,
        use_cache=False,
    )

    return tokenizer.decode(out[0], skip_special_tokens=True).strip()

# ---------------- Markdown builder ----------------
def build_full_markdown(brief: str) -> str:
    cat, top3, worst = parse_brief(brief)
    summary = generate_summary_from_brief(brief)

    md = [f"# {cat}", "", summary, "", "## Top Picks"]

    for p in top3:
        md.append(
            f"**{p['name']}**  \n"
            f"Rating: {p['rating']} • Reviews: {p['reviews']}  \n"
            f"Complaints: {p['complaints']}"
        )

    md.append("\n## Avoid / Lowest Rated")

    if worst["name"]:
        md.append(
            f"⚠️ **{worst['name']}**  \n"
            f"Rating: {worst['rating']} • Reviews: {worst['reviews']}  \n"
            f"Complaint signal: {prettify_reason(worst['reason'])}"
        )

    return "\n\n".join(md)

# ---------------- JSON Export ----------------
def export_json():
    df = STATE["df"]
    if df is None:
        raise ValueError("No CSV loaded.")

    cluster_summaries = {}
    product_summaries = {}

    for _, row in df.iterrows():
        category = str(row["category"])
        brief = str(row["brief"])

        cluster_summaries[category] = build_full_markdown(brief)

        cat, top3, worst = parse_brief(brief)

        for p in top3:
            product_summaries[p["name"]] = {
                "cluster": category,
                "stats": {
                    "total_reviews": p["reviews"],
                    "avg_rating": p["rating"],
                    "pct_positive": None,
                    "pct_negative": None,
                    "pct_neutral": None
                },
                "summary": f"{p['name']} has rating {p['rating']} from {p['reviews']} reviews."
            }

    export_obj = {
        "provider": "huggingface",
        "model": "google/flan-t5-base",
        "cluster_summaries": cluster_summaries,
        "product_summaries": product_summaries
    }

    tmpdir = tempfile.mkdtemp()
    path = Path(tmpdir) / "export.json"
    path.write_text(json.dumps(export_obj, indent=2, ensure_ascii=False), encoding="utf-8")

    return str(path)

# ---------------- Gradio UI ----------------
with gr.Blocks(title="Category Blog Generator") as demo:
    gr.Markdown("# Category Blog Generator")

    csv_file = gr.File(file_types=[".csv"])
    load_btn = gr.Button("Load CSV")

    category_dd = gr.Dropdown(label="Category")
    gen_btn = gr.Button("Generate Summary")

    output_md = gr.Markdown()

    export_btn = gr.Button("Export JSON")
    export_file = gr.File()

    def load_csv(file):
        df = pd.read_csv(file.name)
        STATE["df"] = df
        categories = sorted(df["category"].unique())
        return gr.Dropdown(choices=categories, value=categories[0])

    def generate(category):
        df = STATE["df"]
        row = df[df["category"] == category].iloc[0]
        return build_full_markdown(row["brief"])

    load_btn.click(load_csv, inputs=[csv_file], outputs=[category_dd])
    gen_btn.click(generate, inputs=[category_dd], outputs=[output_md])
    export_btn.click(export_json, outputs=[export_file])

if __name__ == "__main__":
    demo.launch()
