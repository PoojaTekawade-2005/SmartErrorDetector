
import streamlit as st
import re
import csv
import io
import html
import hashlib
from datetime import datetime
from spellchecker import SpellChecker

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Smart Error Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================

DEFAULTS = {
    "project_text": "",
    "analysis": None,
    "history": [],
    "theme_choice": "Light",
    "last_uploaded_file": None,
    "upload_key": 0,
    "selected_page": "Dashboard",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# SAMPLE TEXT
# =========================================================

SAMPLE_TEXT = (
    "I am lerning Python becuse it is very intresting. "
    "Python helps me build useful projects and improve my coding skills. "
    "I really really enjoy learning new technologies because because "
    "they help me grow as a developer"
)


# =========================================================
# SESSION CALLBACKS
# =========================================================

def clear_all():
    st.session_state.project_text = ""
    st.session_state.analysis = None
    st.session_state.last_uploaded_file = None
    st.session_state.upload_key += 1


def load_sample():
    st.session_state.project_text = SAMPLE_TEXT
    st.session_state.analysis = None


def preserve_case(original, suggestion):
    if not suggestion:
        return original

    if original.isupper():
        return suggestion.upper()

    if original.istitle():
        return suggestion.capitalize()

    return suggestion.lower()


# =========================================================
# THEME SYSTEM
# =========================================================

def apply_theme(theme):

    if theme == "Dark":
        colors = {
            "background": "#101827",
            "surface": "#172235",
            "sidebar": "#131E30",
            "text": "#EDF3FC",
            "muted": "#A6B5CA",
            "border": "#2C3B52",
            "primary": "#4C9EFF",
            "secondary": "#1F3450",
            "input": "#1C2A40",
            "metric": "#1B2A40",
            "success": "#183B35",
            "warning": "#46351D",
            "error": "#48272D",
            "spell": "#69343B",
            "repeat": "#65501F",
            "punct": "#493A72",
            "spacing": "#24516B",
        }

    else:
        colors = {
            "background": "#F4F7FB",
            "surface": "#FFFFFF",
            "sidebar": "#FFFFFF",
            "text": "#172B4D",
            "muted": "#687B94",
            "border": "#E2E9F2",
            "primary": "#2368D8",
            "secondary": "#EAF1FC",
            "input": "#FFFFFF",
            "metric": "#FFFFFF",
            "success": "#E4F5EC",
            "warning": "#FFF4D9",
            "error": "#FDE9E9",
            "spell": "#FFDCDD",
            "repeat": "#FFE9AE",
            "punct": "#E8DFFF",
            "spacing": "#D8F0FF",
        }

    st.markdown(
        f"""
        <style>
        :root {{
            color-scheme: {"dark" if theme == "Dark" else "light"};
        }}

        .stApp {{
            background: {colors["background"]};
            color: {colors["text"]};
        }}

        [data-testid="stAppViewContainer"] {{
            background: {colors["background"]};
        }}

        [data-testid="stHeader"] {{
            background: transparent;
        }}

        [data-testid="stSidebar"] {{
            background: {colors["sidebar"]};
            border-right: 1px solid {colors["border"]};
        }}

        [data-testid="stMain"] {{
            background: {colors["background"]};
        }}

        .stApp h1, .stApp h2, .stApp h3,
        .stApp h4, .stApp p, .stApp label,
        .stApp li, .stApp span {{
            color: {colors["text"]};
        }}

        [data-testid="stCaptionContainer"] p {{
            color: {colors["muted"]} !important;
        }}

        [data-testid="stTextArea"] textarea,
        [data-testid="stTextInput"] input {{
            background: {colors["input"]};
            color: {colors["text"]};
            border: 1px solid {colors["border"]};
            border-radius: 11px;
        }}

        [data-testid="stSelectbox"] > div > div,
        [data-testid="stFileUploader"] section {{
            background: {colors["surface"]};
            border-color: {colors["border"]};
            border-radius: 11px;
        }}

        [data-testid="stMetric"] {{
            background: {colors["metric"]};
            border: 1px solid {colors["border"]};
            padding: 16px;
            border-radius: 13px;
            box-shadow: 0 3px 12px rgba(30,60,100,0.04);
        }}

        [data-testid="stMetricLabel"] p {{
            color: {colors["muted"]} !important;
        }}

        [data-testid="stMetricValue"] {{
            color: {colors["text"]};
        }}

        [data-testid="stButton"] button,
        [data-testid="stDownloadButton"] button {{
            border-radius: 10px;
            min-height: 42px;
            font-weight: 600;
            border: 1px solid {colors["border"]};
        }}

        [data-testid="stButton"] button[kind="primary"] {{
            background: {colors["primary"]};
            color: white;
            border: 1px solid {colors["primary"]};
        }}

        [data-testid="stExpander"] {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 12px;
        }}

        [data-testid="stTabs"] button {{
            color: {colors["text"]};
        }}

        hr {{
            border-color: {colors["border"]};
        }}

        .hero {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 17px;
            padding: 25px 26px;
            margin-bottom: 22px;
        }}

        .hero-title {{
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.8px;
            color: {colors["text"]};
            margin-bottom: 6px;
        }}

        .hero-subtitle {{
            font-size: 14px;
            color: {colors["muted"]};
        }}

        .section-title {{
            font-size: 20px;
            font-weight: 750;
            color: {colors["text"]};
            margin: 15px 0;
        }}

        .custom-card {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 14px;
            padding: 17px;
            margin-bottom: 12px;
        }}

        .small-label {{
            color: {colors["muted"]};
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.6px;
        }}

        .highlight-area {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 13px;
            padding: 19px;
            line-height: 2.2;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            color: {colors["text"]};
            min-height: 100px;
        }}

        .spell-mark {{
            background: {colors["spell"]};
            border-bottom: 2px solid #D84B55;
            border-radius: 4px;
            padding: 2px 3px;
            color: {colors["text"]};
        }}

        .repeat-mark {{
            background: {colors["repeat"]};
            border-bottom: 2px solid #D69A24;
            border-radius: 4px;
            padding: 2px 3px;
            color: {colors["text"]};
        }}

        .punct-mark {{
            background: {colors["punct"]};
            border-bottom: 2px solid #9878E0;
            border-radius: 4px;
            padding: 2px 3px;
            color: {colors["text"]};
        }}

        .space-mark {{
            background: {colors["spacing"]};
            border-bottom: 2px solid #3994BF;
            border-radius: 4px;
            padding: 2px 3px;
            color: {colors["text"]};
        }}

        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 12px 0;
            font-size: 12px;
            color: {colors["muted"]};
        }}

        .footer {{
            text-align: center;
            padding: 24px 0 10px;
            color: {colors["muted"]};
            font-size: 12px;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

    return colors


# =========================================================
# TEXT ANALYSIS ENGINE
# =========================================================

def add_issue(issues, issue_type, start, end,
              original, suggestion, message):

    issues.append({
        "type": issue_type,
        "start": start,
        "end": end,
        "original": original,
        "suggestion": suggestion,
        "message": message
    })


def analyze_text(text):

    issues = []
    spell = SpellChecker()

    # SPELLING DETECTION
    for match in re.finditer(
        r"\b[A-Za-z]+(?:'[A-Za-z]+)?\b",
        text
    ):
        word = match.group()
        lower_word = word.lower()

        if lower_word in spell.unknown([lower_word]):

            suggestion = spell.correction(lower_word)

            if suggestion and suggestion.lower() != lower_word:

                suggestion = preserve_case(word, suggestion)

                add_issue(
                    issues,
                    "Spelling",
                    match.start(),
                    match.end(),
                    word,
                    suggestion,
                    "Possible spelling mistake"
                )

    # REPEATED WORD DETECTION
    for match in re.finditer(
        r"\b([A-Za-z]+)\s+([A-Za-z]+)\b",
        text
    ):
        first = match.group(1)
        second = match.group(2)

        if first.casefold() == second.casefold():

            add_issue(
                issues,
                "Repeated word",
                match.start(2),
                match.end(2),
                second,
                "",
                "Consecutive repeated word"
            )

    # EXTRA SPACES BEFORE PUNCTUATION
    for match in re.finditer(r"[ \t]+(?=[,.;!?])", text):
        add_issue(
            issues,
            "Punctuation",
            match.start(),
            match.end(),
            match.group(),
            "",
            "Remove space before punctuation"
        )

    # REPEATED PUNCTUATION
    for match in re.finditer(r"([!?.,])\1+", text):
        add_issue(
            issues,
            "Punctuation",
            match.start(),
            match.end(),
            match.group(),
            match.group(1),
            "Repeated punctuation mark"
        )

    # EXTRA SPACES
    for match in re.finditer(r" {2,}", text):
        add_issue(
            issues,
            "Spacing",
            match.start(),
            match.end(),
            match.group(),
            " ",
            "Multiple spaces between words"
        )

    # LINE BOUNDARY SPACES
    for match in re.finditer(r"(?m)^[ \t]+|[ \t]+$", text):
        add_issue(
            issues,
            "Spacing",
            match.start(),
            match.end(),
            match.group(),
            "",
            "Unnecessary space at line boundary"
        )

    # SORT AND REMOVE OVERLAPPING ISSUES
    issues.sort(key=lambda item: (item["start"], item["end"]))

    filtered = []
    last_end = -1

    for issue in issues:
        if issue["start"] >= last_end:
            filtered.append(issue)
            last_end = issue["end"]

    return filtered


# =========================================================
# HIGHLIGHTING
# =========================================================

def highlight_text(text, issues):

    css_classes = {
        "Spelling": "spell-mark",
        "Repeated word": "repeat-mark",
        "Punctuation": "punct-mark",
        "Spacing": "space-mark"
    }

    result = []
    cursor = 0

    for issue in issues:

        start = issue["start"]
        end = issue["end"]

        result.append(html.escape(text[cursor:start]))

        selected = html.escape(text[start:end])
        css_class = css_classes[issue["type"]]

        result.append(
            f'<span class="{css_class}" '
            f'title="{html.escape(issue["message"])}">'
            f'{selected}</span>'
        )

        cursor = end

    result.append(html.escape(text[cursor:]))

    return "".join(result)


# =========================================================
# INTERACTIVE CORRECTIONS
# =========================================================

def correct_text(text, issues, selected_indices):

    corrected = text

    selected = [
        issues[index]
        for index in selected_indices
        if 0 <= index < len(issues)
    ]

    for issue in sorted(
        selected,
        key=lambda item: item["start"],
        reverse=True
    ):

        start = issue["start"]
        end = issue["end"]
        replacement = issue["suggestion"]

        # Remove the preceding whitespace with a repeated word.
        if issue["type"] == "Repeated word":
            while start > 0 and text[start - 1] in " \t":
                start -= 1

        corrected = (
            corrected[:start]
            + replacement
            + corrected[end:]
        )

    return corrected


# =========================================================
# STATISTICS
# =========================================================

def text_statistics(text):

    words = re.findall(r"\b[\w']+\b", text)

    sentences = re.findall(
        r"[.!?]+(?=\s|$)",
        text
    )

    paragraphs = [
        p for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    return {
        "words": len(words),
        "characters": len(text),
        "no_spaces": len(re.sub(r"\s", "", text)),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs)
    }


def issue_counts(issues):

    return {
        "Spelling": sum(i["type"] == "Spelling" for i in issues),
        "Repeated words": sum(i["type"] == "Repeated word" for i in issues),
        "Punctuation": sum(i["type"] == "Punctuation" for i in issues),
        "Spacing": sum(i["type"] == "Spacing" for i in issues)
    }


# =========================================================
# WRITING TIPS
# =========================================================

def get_writing_tips(text, issues):

    counts = issue_counts(issues)
    tips = []

    if counts["Spelling"]:
        tips.append(
            "Review spelling suggestions and check unfamiliar words."
        )

    if counts["Repeated words"]:
        tips.append(
            "Avoid accidentally repeating words in consecutive positions."
        )

    if counts["Punctuation"]:
        tips.append(
            "Review punctuation spacing and repeated punctuation marks."
        )

    if counts["Spacing"]:
        tips.append(
            "Use consistent spacing throughout your document."
        )

    if text.strip() and not re.search(
        r"[.!?][\"')\]]*\s*$",
        text.strip()
    ):
        tips.append(
            "Consider whether your final sentence needs ending punctuation."
        )

    if len(text.split()) > 0:
        tips.append(
            "Read your text aloud to check clarity and sentence flow."
        )

    if not tips:
        tips.append(
            "No obvious issues were detected by the current checks. "
            "Continue reviewing your writing for clarity."
        )

    return tips


# =========================================================
# REPORT GENERATION
# =========================================================

def create_csv_report(issues):

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow([
        "Issue Type",
        "Original Text",
        "Suggestion",
        "Description"
    ])

    for issue in issues:
        writer.writerow([
            issue["type"],
            issue["original"],
            issue["suggestion"],
            issue["message"]
        ])

    return buffer.getvalue()


def create_text_report(result):

    issues = result["issues"]
    stats = result["stats"]
    counts = issue_counts(issues)

    lines = [
        "SMART ERROR DETECTOR - ANALYSIS REPORT",
        "=" * 45,
        "",
        f"Analysis date: {result['date']}",
        f"Total words: {stats['words']}",
        f"Characters: {stats['characters']}",
        f"Sentences: {stats['sentences']}",
        f"Paragraphs: {stats['paragraphs']}",
        "",
        "ISSUE SUMMARY",
        "-" * 30
    ]

    for category, count in counts.items():
        lines.append(f"{category}: {count}")

    lines.extend([
        "",
        "DETECTED ISSUES",
        "-" * 30
    ])

    if issues:
        for issue in issues:
            lines.append(
                f"{issue['type']}: {issue['original']} "
                f"-> {issue['suggestion'] or 'Review manually'}"
            )
    else:
        lines.append("No issues detected.")

    lines.extend([
        "",
        "ORIGINAL TEXT",
        "-" * 30,
        result["text"]
    ])

    return "\n".join(lines)


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:

    st.markdown("## 🔍 Smart Error Detector")
    st.caption("Your intelligent writing workspace")

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Select a page",
        [
            "Dashboard",
            "Analytics",
            "History",
            "About"
        ],
        label_visibility="collapsed",
        key="selected_page",
        format_func=lambda x: {
            "Dashboard": "🏠 Dashboard",
            "Analytics": "📊 Analytics",
            "History": "🕘 History",
            "About": "ℹ️ About"
        }[x]
    )

    st.divider()

    st.markdown("### 🎨 Appearance")

    theme_choice = st.radio(
        "Choose your theme",
        ["Light", "Dark"],
        key="theme_choice",
        horizontal=True
    )

    st.caption("Change the appearance of your workspace.")

    st.divider()

    st.markdown("### Quick actions")

    st.button(
        "✨ Load sample text",
        use_container_width=True,
        on_click=load_sample
    )

    st.button(
        "🧹 Clear workspace",
        use_container_width=True,
        on_click=clear_all
    )

    st.divider()

    st.markdown("### Project information")

    st.caption("Python-based writing assistant")

    st.markdown("""
    - Spelling detection
    - Repeated word detection
    - Error highlighting
    - Interactive corrections
    - Writing analytics
    - Exportable reports
    """)

    st.divider()

    st.caption("SMART ERROR DETECTOR · VERSION 2.0")


COLORS = apply_theme(theme_choice)


# =========================================================
# PAGE HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">Smart Error Detector</div>
        <div class="hero-subtitle">
            Write better. Find mistakes. Improve your writing.
            Your professional text analysis workspace.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">📝 Writing workspace</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Enter your text or upload a text file to begin your analysis."
    )

    # FILE UPLOAD
    uploaded_file = st.file_uploader(
        "Upload a .txt document",
        type=["txt"],
        key=f"text_upload_{st.session_state.upload_key}"
    )

    if uploaded_file is not None:

        file_bytes = uploaded_file.getvalue()

        file_identity = hashlib.sha256(
            uploaded_file.name.encode("utf-8") + file_bytes
        ).hexdigest()

        if file_identity != st.session_state.last_uploaded_file:

            st.session_state.project_text = file_bytes.decode(
                "utf-8-sig",
                errors="replace"
            )

            st.session_state.last_uploaded_file = file_identity
            st.session_state.analysis = None

    # EDITOR
    st.text_area(
        "Your document",
        key="project_text",
        height=220,
        placeholder="Start typing or paste your project text here..."
    )

    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        analyze_clicked = st.button(
            "🔍 Analyze text",
            type="primary",
            use_container_width=True
        )

    with col2:
        st.button(
            "✨ Sample text",
            on_click=load_sample,
            use_container_width=True
        )

    with col3:
        st.button(
            "↺ Clear",
            on_click=clear_all,
            use_container_width=True
        )

    # ANALYSIS
    if analyze_clicked:

        text = st.session_state.project_text

        if not text.strip():

            st.warning("Please enter some text before analyzing.")

            st.session_state.analysis = None

        else:

            with st.spinner("Analyzing your text..."):

                issues = analyze_text(text)
                stats = text_statistics(text)

                result = {
                    "text": text,
                    "issues": issues,
                    "stats": stats,
                    "date": datetime.now().strftime(
                        "%d %b %Y, %I:%M %p"
                    )
                }

                st.session_state.analysis = result

                history_item = {
                    "text": text,
                    "issues": issues,
                    "stats": stats,
                    "date": result["date"]
                }

                st.session_state.history.insert(
                    0,
                    history_item
                )

                st.session_state.history = (
                    st.session_state.history[:20]
                )

    result = st.session_state.analysis

    if result:

        if result["text"] != st.session_state.project_text:

            st.info(
                "Your document has changed since the last analysis. "
                "Analyze it again to refresh the results."
            )

        else:

            issues = result["issues"]
            stats = result["stats"]
            counts = issue_counts(issues)

            # SIMPLE INDICATOR
            total_words = stats["words"]

            score = 100 if total_words == 0 else max(
                0,
                round(
                    100 * (
                        1 - min(len(issues), total_words) / total_words
                    )
                )
            )

            st.divider()

            st.markdown(
                '<div class="section-title">📈 Analysis overview</div>',
                unsafe_allow_html=True
            )

            m1, m2, m3, m4 = st.columns(4)

            m1.metric("Total issues", len(issues))
            m2.metric("Spelling", counts["Spelling"])
            m3.metric("Repeated words", counts["Repeated words"])
            m4.metric("Writing indicator", f"{score}/100")

            st.caption(
                "The writing indicator is a simple estimate based on "
                "detected issues. It is not a validated writing-quality score."
            )

            # HIGHLIGHTED TEXT
            st.divider()

            st.markdown(
                '<div class="section-title">🎨 Highlighted document</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="legend">
                    <span>🔴 Spelling</span>
                    <span>🟡 Repeated word</span>
                    <span>🟣 Punctuation</span>
                    <span>🔵 Spacing</span>
                </div>
                """,
                unsafe_allow_html=True
            )

            highlighted = highlight_text(
                result["text"],
                issues
            )

            st.markdown(
                f'<div class="highlight-area">{highlighted}</div>',
                unsafe_allow_html=True
            )

            # INTERACTIVE CORRECTIONS
            st.divider()

            st.markdown(
                '<div class="section-title">🛠️ Review corrections</div>',
                unsafe_allow_html=True
            )

            if issues:

                st.caption(
                    "Select the corrections you want to apply. "
                    "Unselected suggestions will remain unchanged."
                )

                selected_indices = []

                for index, issue in enumerate(issues):

                    if issue["suggestion"]:

                        label = (
                            f'{issue["type"]}: '
                            f'"{issue["original"]}" → '
                            f'"{issue["suggestion"]}"'
                        )

                    else:

                        label = (
                            f'{issue["type"]}: '
                            f'"{issue["original"]}" — '
                            f'{issue["message"]}'
                        )

                    if st.checkbox(
                        label,
                        key=f"correction_{index}"
                    ):
                        selected_indices.append(index)

                if st.button(
                    "Apply selected corrections",
                    type="primary"
                ):

                    corrected = correct_text(
                        result["text"],
                        issues,
                        selected_indices
                    )

                    st.session_state.project_text = corrected
                    st.session_state.analysis = None

                    st.success(
                        "Selected corrections applied. "
                        "Analyze the updated text to see the new results."
                    )

                    st.rerun()

            else:

                st.success(
                    "No obvious issues detected by the current checks!"
                )

            # TEXT STATISTICS
            st.divider()

            st.markdown(
                '<div class="section-title">📚 Document statistics</div>',
                unsafe_allow_html=True
            )

            s1, s2, s3, s4, s5 = st.columns(5)

            s1.metric("Words", stats["words"])
            s2.metric("Characters", stats["characters"])
            s3.metric("No whitespace", stats["no_spaces"])
            s4.metric("Sentences", stats["sentences"])
            s5.metric("Paragraphs", stats["paragraphs"])

            # WRITING TIPS
            st.divider()

            st.markdown(
                '<div class="section-title">💡 Writing recommendations</div>',
                unsafe_allow_html=True
            )

            for tip in get_writing_tips(result["text"], issues):
                st.markdown(f"- {tip}")

            # DOWNLOAD REPORTS
            st.divider()

            st.markdown(
                '<div class="section-title">📥 Export your report</div>',
                unsafe_allow_html=True
            )

            text_report = create_text_report(result)
            csv_report = create_csv_report(issues)

            d1, d2 = st.columns(2)

            with d1:

                st.download_button(
                    "⬇️ Download text report",
                    data=text_report,
                    file_name="smart_error_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            with d2:

                st.download_button(
                    "⬇️ Download CSV report",
                    data=csv_report,
                    file_name="smart_error_report.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            st.download_button(
                "⬇️ Download original analyzed text",
                data=result["text"],
                file_name="analyzed_text.txt",
                mime="text/plain",
                use_container_width=True
            )


# =========================================================
# ANALYTICS PAGE
# =========================================================

elif page == "Analytics":

    st.markdown(
        '<div class="section-title">📊 Writing analytics</div>',
        unsafe_allow_html=True
    )

    result = st.session_state.analysis

    if not result:

        st.info(
            "Analyze a document from the Dashboard to view its analytics."
        )

    else:

        issues = result["issues"]
        stats = result["stats"]
        counts = issue_counts(issues)

        st.markdown("#### Issue distribution")

        chart_data = {
            "Issue category": list(counts.keys()),
            "Number of issues": list(counts.values())
        }

        st.bar_chart(
            chart_data,
            x="Issue category",
            y="Number of issues",
            horizontal=True
        )

        st.markdown("#### Text overview")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Words", stats["words"])
        c2.metric("Characters", stats["characters"])
        c3.metric("Sentences", stats["sentences"])
        c4.metric("Paragraphs", stats["paragraphs"])

        st.caption(
            "Analytics show the most recently analyzed document."
        )


# =========================================================
# HISTORY PAGE
# =========================================================

elif page == "History":

    st.markdown(
        '<div class="section-title">🕘 Analysis history</div>',
        unsafe_allow_html=True
    )

    history = st.session_state.history

    st.caption(
        "Your recent analyses in this app session."
    )

    if not history:

        st.info(
            "No analysis history yet. Analyze a document to get started."
        )

    else:

        if st.button("Clear history"):

            st.session_state.history = []
            st.rerun()

        for index, item in enumerate(history):

            with st.expander(
                f"Analysis {index + 1} · {item['date']}"
            ):

                st.write(
                    f"**Words:** {item['stats']['words']}"
                )

                st.write(
                    f"**Issues:** {len(item['issues'])}"
                )

                st.text_area(
                    "Analyzed document",
                    value=item["text"],
                    height=120,
                    key=f"history_document_{index}",
                    disabled=True
                )

                if st.button(
                    "Load this document",
                    key=f"load_history_{index}"
                ):

                    st.session_state.project_text = item["text"]
                    st.session_state.analysis = None
                    st.session_state.selected_page = "Dashboard"

                    st.rerun()


# =========================================================
# ABOUT PAGE
# =========================================================

elif page == "About":

    st.markdown(
        '<div class="section-title">ℹ️ About the project</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    Smart Error Detector is a Python-based writing assistant
    that helps users identify common text mistakes and review
    possible corrections.

    ### Core features

    - Possible spelling error detection
    - Consecutive repeated-word detection
    - Punctuation and spacing checks
    - Color-coded error highlighting
    - Selectable corrections
    - Writing tips and text statistics
    - Analytics and analysis history
    - Text and CSV report exports
    - Light and Dark themes

    ### Technologies

    - Python
    - Streamlit
    - PySpellChecker
    - Regular expressions
    - CSV and HTML formatting

    ### Current limitations

    - Spelling suggestions may not match the intended meaning.
    - Names and technical words may be flagged incorrectly.
    - This is not a full grammar or context-aware writing engine.
    - History is stored only during the current app session.
    - The writing indicator is an estimate, not a validated score.

    **Always review suggested corrections before using them.**
    """)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        <strong>SMART ERROR DETECTOR</strong><br>
        Professional Writing Assistant · Built with Python and Streamlit<br>
        Version 2.0
    </div>
    """,
    unsafe_allow_html=True
)
