import json
import os
import random
from collections import defaultdict
from datetime import date, datetime, timedelta

from dash import Dash, Input, Output, State, callback, dcc, html, no_update
import plotly.graph_objects as go

WORDS_FILE = "norwegian_words.json"
SCORES_FILE = "scores.json"
POINTS_FILE = "points.txt"

THEME = {
    "bg": "linear-gradient(135deg, #f8f4e8 0%, #f5fbff 45%, #eef7f4 100%)",
    "surface": "#ffffff",
    "ink": "#15202b",
    "muted": "#4b5563",
    "accent": "#0f766e",
    "accent_soft": "#dff7f2",
    "highlight": "#e76f51",
    "line": "#dbe5e1",
}
FONT_FAMILY = "Segoe UI, sans-serif"


def load_words():
    if not os.path.exists(WORDS_FILE):
        return []
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return {"total_words": 0, "sessions": []}
    with open(SCORES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)


def write_points_file(scores, session_score):
    sessions = scores.get("sessions", [])
    total_words = scores.get("total_words", 0)
    average = 0.0
    if sessions:
        average = sum(s.get("score", 0) for s in sessions) / len(sessions)

    lines = [
        "Norwegian Word Game - Points Summary",
        "====================================",
        f"Last session score: {session_score}/5",
        f"Total words learned: {total_words}",
        f"Sessions played: {len(sessions)}",
        f"Average score: {average:.2f}/5",
        "",
        "Recent sessions (latest first):",
    ]

    for i, session in enumerate(reversed(sessions[-10:]), 1):
        lines.append(
            f"{i}. {session.get('date', 'unknown')} - {session.get('score', 0)}/{session.get('max', 5)}"
        )

    with open(POINTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def parse_session_date(value):
    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


def build_daily_stats(sessions):
    daily = defaultdict(lambda: {"score": 0, "max": 0, "sessions": 0})
    for session in sessions:
        d = parse_session_date(session.get("date", ""))
        if d is None:
            continue
        daily[d]["score"] += int(session.get("score", 0))
        daily[d]["max"] += int(session.get("max", 5))
        daily[d]["sessions"] += 1
    return dict(daily)


def current_streak(play_days):
    if not play_days:
        return 0

    streak = 0
    cursor = date.today()
    while cursor in play_days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def longest_streak(play_days_sorted):
    if not play_days_sorted:
        return 0

    best = 1
    run = 1
    for i in range(1, len(play_days_sorted)):
        if play_days_sorted[i] == play_days_sorted[i - 1] + timedelta(days=1):
            run += 1
            best = max(best, run)
        else:
            run = 1
    return best


def build_quiz_questions(words, amount=5):
    selected = random.sample(words, amount)
    questions = []

    for word_data in selected:
        word = word_data["word"]
        correct_description = word_data["description"]
        wrong_descriptions = random.sample(
            [w["description"] for w in words if w["word"] != word],
            2,
        )

        options = [correct_description] + wrong_descriptions
        random.shuffle(options)

        questions.append(
            {
                "word": word,
                "answer": correct_description,
                "options": options,
            }
        )

    return questions


def save_completed_session(score, max_score=5):
    scores = load_scores()
    scores["total_words"] = int(scores.get("total_words", 0)) + int(score)
    scores.setdefault("sessions", []).append(
        {
            "date": datetime.now().isoformat(),
            "score": int(score),
            "max": int(max_score),
        }
    )
    save_scores(scores)
    write_points_file(scores, score)


def statistics_payload():
    scores = load_scores()
    sessions = scores.get("sessions", [])
    total_words = int(scores.get("total_words", 0))

    daily = build_daily_stats(sessions)
    days_sorted = sorted(daily.keys())
    days_set = set(days_sorted)

    total_sessions = len(sessions)
    total_correct = sum(int(s.get("score", 0)) for s in sessions)
    total_questions = sum(int(s.get("max", 5)) for s in sessions)
    accuracy = (100.0 * total_correct / total_questions) if total_questions else 0.0

    first_day = days_sorted[0].isoformat() if days_sorted else "N/A"
    last_day = days_sorted[-1].isoformat() if days_sorted else "N/A"

    return {
        "total_words": total_words,
        "total_sessions": total_sessions,
        "total_days": len(days_sorted),
        "current_streak": current_streak(days_set),
        "longest_streak": longest_streak(days_sorted),
        "accuracy": accuracy,
        "first_day": first_day,
        "last_day": last_day,
        "days_sorted": days_sorted,
        "daily": daily,
    }


def card(title, value):
    return html.Div(
        [
            html.Div(title, style={"fontSize": "13px", "color": THEME["muted"], "letterSpacing": "0.4px"}),
            html.Div(
                value,
                style={
                    "fontSize": "30px",
                    "fontWeight": "700",
                    "marginTop": "6px",
                    "color": THEME["ink"],
                },
            ),
        ],
        style={
            "background": THEME["surface"],
            "border": f"1px solid {THEME['line']}",
            "borderRadius": "16px",
            "padding": "14px",
            "boxShadow": "0 10px 28px rgba(20, 43, 31, 0.08)",
        },
    )


def build_cumulative_figure(days_sorted, daily):
    x = []
    y = []
    running = 0
    for d in days_sorted:
        running += daily[d]["score"]
        x.append(d.isoformat())
        y.append(running)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=y,
            mode="lines+markers",
            line={"width": 4, "color": THEME["accent"]},
            marker={"size": 9, "color": THEME["highlight"]},
            name="Cumulative words",
        )
    )
    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        plot_bgcolor=THEME["surface"],
        paper_bgcolor=THEME["surface"],
        title="Cumulative Words Learned",
        yaxis_title="Words",
        xaxis_title="Date",
        font={"family": FONT_FAMILY, "color": THEME["ink"]},
    )
    return fig


def build_accuracy_figure(days_sorted, daily):
    x = []
    y = []
    for d in days_sorted:
        x.append(d.isoformat())
        max_score = daily[d]["max"]
        if max_score == 0:
            y.append(0)
        else:
            y.append((daily[d]["score"] / max_score) * 100.0)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            marker_color=THEME["highlight"],
            name="Daily accuracy",
        )
    )
    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 30, "b": 20},
        plot_bgcolor=THEME["surface"],
        paper_bgcolor=THEME["surface"],
        title="Accuracy by Active Day",
        yaxis_title="Accuracy %",
        xaxis_title="Date",
        yaxis={"range": [0, 100]},
        font={"family": FONT_FAMILY, "color": THEME["ink"]},
    )
    return fig


def home_layout():
    return html.Div(
        [
            html.H2("Learn Norwegian Quiz", style={"marginTop": "0"}),
            html.P(
                "Pick an answer.",
                style={"color": THEME["muted"]},
            ),
            html.Button(
                "Start New Session",
                id="start-quiz",
                n_clicks=0,
                style={
                    "marginBottom": "16px",
                    "background": THEME["accent"],
                    "color": "white",
                    "border": "0",
                    "borderRadius": "12px",
                    "padding": "11px 16px",
                    "fontWeight": "700",
                    "cursor": "pointer",
                },
            ),
            html.Div(id="quiz-progress", style={"fontWeight": "700", "marginBottom": "8px", "color": THEME["muted"]}),
            html.Div(id="quiz-question", style={"fontSize": "30px", "marginBottom": "14px", "fontWeight": "700"}),
            dcc.RadioItems(
                id="answer-options",
                options=[],
                value=None,
                style={"marginBottom": "14px"},
                labelStyle={
                    "display": "block",
                    "padding": "12px 14px",
                    "marginBottom": "10px",
                    "background": "#f6fbf9",
                    "border": f"1px solid {THEME['line']}",
                    "borderRadius": "12px",
                    "cursor": "pointer",
                    "fontWeight": "600",
                },
                inputStyle={"marginRight": "10px"},
            ),
            html.Div(id="quiz-feedback", style={"marginTop": "8px", "fontWeight": "700", "color": THEME["accent"]}),
            html.Div(id="quiz-result", style={"marginTop": "10px", "fontSize": "22px", "fontWeight": "800", "color": THEME["highlight"]}),
        ],
        style={
            "background": THEME["surface"],
            "border": f"1px solid {THEME['line']}",
            "borderRadius": "18px",
            "padding": "20px",
            "boxShadow": "0 12px 30px rgba(27, 38, 49, 0.08)",
        },
    )


def statistics_layout():
    payload = statistics_payload()
    days_sorted = payload["days_sorted"]
    daily = payload["daily"]

    cards = html.Div(
        [
            card("Total words learned", payload["total_words"]),
            card("Total sessions", payload["total_sessions"]),
            card("Days played", payload["total_days"]),
            card("Current streak", payload["current_streak"]),
            card("Longest streak", payload["longest_streak"]),
            card("Overall accuracy", f"{payload['accuracy']:.1f}%"),
            card("First play date", payload["first_day"]),
            card("Most recent play", payload["last_day"]),
        ],
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
            "gap": "12px",
            "marginBottom": "20px",
        },
    )

    if days_sorted:
        cumulative = dcc.Graph(figure=build_cumulative_figure(days_sorted, daily))
        accuracy = dcc.Graph(figure=build_accuracy_figure(days_sorted, daily))

        last_days = days_sorted[-14:]
        table_rows = []
        for d in last_days:
            score = daily[d]["score"]
            max_score = daily[d]["max"]
            sessions = daily[d]["sessions"]
            acc = (100.0 * score / max_score) if max_score else 0.0
            table_rows.append(
                html.Tr(
                    [
                        html.Td(d.isoformat()),
                        html.Td(str(sessions)),
                        html.Td(f"{score}/{max_score}"),
                        html.Td(f"{acc:.1f}%"),
                    ]
                )
            )

        table = html.Table(
            [
                html.Thead(
                    html.Tr(
                        [
                            html.Th("Date", style={"textAlign": "left", "padding": "10px"}),
                            html.Th("Sessions", style={"textAlign": "left", "padding": "10px"}),
                            html.Th("Score", style={"textAlign": "left", "padding": "10px"}),
                            html.Th("Accuracy", style={"textAlign": "left", "padding": "10px"}),
                        ]
                    )
                ),
                html.Tbody(table_rows),
            ],
            style={
                "width": "100%",
                "borderCollapse": "collapse",
                "background": THEME["surface"],
                "border": f"1px solid {THEME['line']}",
                "borderRadius": "12px",
                "overflow": "hidden",
            },
        )
    else:
        empty_style = {
            "padding": "16px",
            "background": THEME["surface"],
            "border": f"1px solid {THEME['line']}",
            "borderRadius": "12px",
        }
        cumulative = html.Div("No session data yet.", style=empty_style)
        accuracy = html.Div("Play a session to unlock charts.", style=empty_style)
        table = html.Div("No active days available yet.", style=empty_style)

    return html.Div(
        [
            html.H2("Statistics", style={"marginTop": "0"}),
            cards,
            cumulative,
            accuracy,
            html.H3("Last 14 active days", style={"marginTop": "16px"}),
            table,
        ],
        style={
            "background": THEME["surface"],
            "border": f"1px solid {THEME['line']}",
            "borderRadius": "18px",
            "padding": "20px",
            "boxShadow": "0 12px 30px rgba(27, 38, 49, 0.08)",
        },
    )


app = Dash(__name__, suppress_callback_exceptions=True)
app.title = "Learn Words"
server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dcc.Store(id="quiz-state", storage_type="session"),
        html.Div(
            [
                html.H1("Learn Words", style={"margin": "0"}),
                html.Div(
                    [
                        dcc.Link(
                            "Play",
                            href="/",
                            style={
                                "marginRight": "10px",
                                "padding": "8px 12px",
                                "borderRadius": "20px",
                                "textDecoration": "none",
                                "background": "rgba(255,255,255,0.6)",
                                "color": THEME["ink"],
                                "fontWeight": "600",
                            },
                        ),
                        dcc.Link(
                            "Statistics",
                            href="/statistics",
                            style={
                                "padding": "8px 12px",
                                "borderRadius": "20px",
                                "textDecoration": "none",
                                "background": "rgba(255,255,255,0.6)",
                                "color": THEME["ink"],
                                "fontWeight": "600",
                            },
                        ),
                    ],
                    style={"marginTop": "10px"},
                ),
            ],
            style={
                "background": "linear-gradient(120deg, #7fd8be 0%, #95c8ff 45%, #ffd2a3 100%)",
                "padding": "22px",
                "borderRadius": "16px",
                "marginBottom": "18px",
                "boxShadow": "0 14px 32px rgba(46, 72, 65, 0.20)",
            },
        ),
        html.Div(id="page-content"),
    ],
    style={
        "maxWidth": "980px",
        "margin": "20px auto",
        "padding": "0 16px",
        "fontFamily": FONT_FAMILY,
        "background": THEME["bg"],
        "minHeight": "100vh",
        "color": THEME["ink"],
    },
)


@callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/statistics":
        return statistics_layout()
    return home_layout()


@callback(
    Output("quiz-state", "data"),
    Output("quiz-feedback", "children"),
    Input("start-quiz", "n_clicks"),
    prevent_initial_call=True,
)
def start_quiz(_n_clicks):
    words = load_words()
    if len(words) < 5:
        return None, "Need at least 5 words in norwegian_words.json"

    questions = build_quiz_questions(words, amount=5)
    state = {
        "index": 0,
        "score": 0,
        "max": 5,
        "finished": False,
        "questions": questions,
    }
    return state, "Session started."


@callback(
    Output("quiz-progress", "children"),
    Output("quiz-question", "children"),
    Output("answer-options", "options"),
    Output("answer-options", "value"),
    Output("quiz-result", "children"),
    Input("quiz-state", "data"),
)
def render_quiz(state):
    if not state:
        return "", "Press Start New Session", [], None, ""

    if state.get("finished"):
        score = int(state.get("score", 0))
        max_score = int(state.get("max", 5))
        return (
            "Session complete",
            "Start a new session to play again",
            [],
            None,
            f"Final score: {score}/{max_score}",
        )

    idx = int(state.get("index", 0))
    max_score = int(state.get("max", 5))
    question = state["questions"][idx]

    options = [{"label": option, "value": option} for option in question["options"]]
    return (
        f"Question {idx + 1}/{max_score}",
        f"What does '{question['word']}' mean?",
        options,
        None,
        "",
    )


@callback(
    Output("quiz-state", "data", allow_duplicate=True),
    Output("quiz-feedback", "children", allow_duplicate=True),
    Input("answer-options", "value"),
    State("quiz-state", "data"),
    prevent_initial_call=True,
)
def submit_answer(selected_value, state):
    if not state or state.get("finished"):
        return no_update, no_update

    if not selected_value:
        return no_update, no_update

    idx = int(state["index"])
    question = state["questions"][idx]
    answer = question["answer"]

    feedback = "Correct."
    if selected_value == answer:
        state["score"] = int(state.get("score", 0)) + 1
    else:
        feedback = f"Wrong. Correct answer: {answer}"

    state["index"] = idx + 1

    if state["index"] >= int(state.get("max", 5)):
        state["finished"] = True
        save_completed_session(state["score"], state["max"])
        feedback = f"{feedback} Session saved."

    return state, feedback


if __name__ == "__main__":
    app.run(debug=False)
