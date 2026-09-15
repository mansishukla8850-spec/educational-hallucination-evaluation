
import streamlit as st
import pandas as pd
import re

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Educational Hallucination Evaluation",
    page_icon="🔍",
    layout="wide"
)

# --------------------------------------------------
# Load Ground Truth Data
# --------------------------------------------------

DATA_PATH = "data/ground_truth_completed.csv"

ground_truth_df = pd.read_csv(DATA_PATH)

# --------------------------------------------------
# Text Cleaning
# --------------------------------------------------

def clean_text(text):
    if pd.isna(text):
        return set()

    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    words = text.split()

    return set(words)

# --------------------------------------------------
# Response Evaluation
# --------------------------------------------------

def evaluate_response(question_id, user_response):

    row = ground_truth_df[
        ground_truth_df["Question_ID"] == question_id
    ]

    if row.empty:
        return {
            "Evaluation": "Question Not Found",
            "Hallucination": None,
            "Severity": None,
            "Similarity": 0
        }

    ground_truth = str(row.iloc[0]["Ground_Truth"])

    gt_words = clean_text(ground_truth)
    response_words = clean_text(user_response)

    if len(gt_words) == 0 or len(response_words) == 0:
        similarity = 0
    else:
        common_words = gt_words.intersection(response_words)
        similarity = len(common_words) / len(gt_words)

    similarity_percentage = round(similarity * 100, 2)

    # Prototype decision rules
    if similarity >= 0.80:
        evaluation = "Correct"
        hallucination = 0
        severity = 0

    elif similarity >= 0.35:
        evaluation = "Partially Correct"
        hallucination = 1
        severity = 1

    else:
        evaluation = "Incorrect"
        hallucination = 1
        severity = 3

    return {
        "Evaluation": evaluation,
        "Hallucination": hallucination,
        "Severity": severity,
        "Similarity": similarity_percentage
    }

# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("🔍 Educational Hallucination Evaluation System")

st.write(
    "An evidence-based prototype for evaluating the factual "
    "accuracy of educational responses."
)

st.divider()

# --------------------------------------------------
# Question Selection
# --------------------------------------------------

st.subheader("1. Select a Question")

question_ids = ground_truth_df["Question_ID"].tolist()

selected_id = st.selectbox(
    "Question ID",
    question_ids
)

selected_row = ground_truth_df[
    ground_truth_df["Question_ID"] == selected_id
].iloc[0]

st.write("**Question:**")
st.info(selected_row["Question"])

# --------------------------------------------------
# Question Information
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.write("**Question Type**")
    st.write(selected_row["Question_Type"])

with col2:
    st.write("**Subject**")
    st.write(selected_row["Subject"])

with col3:
    st.write("**Difficulty**")
    st.write(selected_row["Difficulty"])

st.divider()

# --------------------------------------------------
# User Response
# --------------------------------------------------

st.subheader("2. Enter the Response")

user_response = st.text_area(
    "Enter the educational response you want to evaluate:",
    height=180,
    placeholder="Type or paste the response here..."
)

# --------------------------------------------------
# Evaluation Button
# --------------------------------------------------

if st.button("🔎 Evaluate Response", type="primary"):

    if user_response.strip() == "":
        st.warning("Please enter a response before evaluating.")

    else:

        result = evaluate_response(
            selected_id,
            user_response
        )

        st.divider()

        st.subheader("3. Evaluation Result")

        # Main result
        if result["Evaluation"] == "Correct":
            st.success("✅ Correct")

        elif result["Evaluation"] == "Partially Correct":
            st.warning("⚠️ Partially Correct")

        else:
            st.error("❌ Incorrect")

        # Result metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Similarity",
                f'{result["Similarity"]}%'
            )

        with col2:
            if result["Hallucination"] == 1:
                st.metric("Hallucination", "Yes")
            else:
                st.metric("Hallucination", "No")

        with col3:
            severity_names = {
                0: "None",
                1: "Minor",
                2: "Significant",
                3: "Major"
            }

            st.metric(
                "Severity",
                severity_names[result["Severity"]]
            )

        st.divider()

        # Ground Truth
        st.subheader("Reference Ground Truth")

        st.write(selected_row["Ground_Truth"])

        # Evidence source
        if "Evidence_Source" in selected_row.index:
            st.subheader("Evidence Source")
            st.write(selected_row["Evidence_Source"])

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Prototype reference-based evaluator. "
    "Results are based on simple ground-truth word-overlap rules "
    "and should be interpreted as a prototype evaluation, "
    "not as a fully automated factuality detector."
)
