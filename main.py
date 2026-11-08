
import streamlit as st
import plotly.express as px
import json
import csv
from datetime import date
from pathlib import Path

# НАСТРОЙКИ САЙТА
st.set_page_config(
    page_title="Habit Tracker Dashboard",
    page_icon="📊",
    layout="centered"
)

# ДИЗАЙН
st.markdown("""
<style>
.block-container {
    max-width: 750px;
    padding-top: 35px;
}

h1 {
    font-size: 34px;
    font-weight: 750;
}

div.stButton > button {
    border-radius: 8px;
}

div.stButton > button:hover {
    border-color: #9b7bff;
    color: #7952d9;
}
</style>
""", unsafe_allow_html=True)

# ФАЙЛЫ ДЛЯ СОХРАНЕНИЯ
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "habits.json"
OLD_FILE = BASE_DIR / "habits.csv"


# ЗАГРУЗКА ДАННЫХ
def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
        except (OSError, json.JSONDecodeError):
            pass

    # Перенос старых записей из CSV в JSON
    if OLD_FILE.exists():
        try:
            with open(
                OLD_FILE, "r", encoding="utf-8-sig"
            ) as file:
                return list(csv.DictReader(file))
        except (OSError, csv.Error):
            pass

    return []


# СОХРАНЕНИЕ ДАННЫХ В JSON
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            st.session_state.habits,
            file,
            ensure_ascii=False,
            indent=4
        )


# КНОПКИ МИНУТ
def decrease_minutes():
    st.session_state.minutes = max(
        0, st.session_state.minutes - 1
    )


def increase_minutes():
    st.session_state.minutes = min(
        1440, st.session_state.minutes + 1
    )


# ДАННЫЕ ПРИЛОЖЕНИЯ
if "habits" not in st.session_state:
    st.session_state.habits = load_data()

    # Сохраняем перенесённые данные в JSON
    if not DATA_FILE.exists():
        save_data()

if "minutes" not in st.session_state:
    st.session_state.minutes = 30


# ЗАГОЛОВОК
st.title("📊 Habit Tracker Dashboard")

st.write(
    "Записуй свою щоденну активність — "
    "я збережу дані і покажу статистику."
)

# ФОРМА ДОБАВЛЕНИЯ
with st.container(border=True):

    selected_date = st.date_input(
        "Дата",
        value=date.today(),
        format="YYYY/MM/DD"
    )

    category = st.selectbox(
        "Категорія",
        [
            "Навчання",
            "Спорт",
            "Читання",
            "Програмування",
            "Малювання",
            "Музика",
            "Медитація",
            "Гра на інструменті"
        ]
    )

    st.write("Скільки хвилин?")

    col1, col2, col3 = st.columns([5, 1, 1])

    with col1:
        st.number_input(
            "Хвилини",
            min_value=0,
            max_value=1440,
            key="minutes",
            label_visibility="collapsed"
        )

    with col2:
        st.button(
            "−",
            use_container_width=True,
            on_click=decrease_minutes
        )

    with col3:
        st.button(
            "+",
            use_container_width=True,
            on_click=increase_minutes
        )

    if st.button("➕ Додати запис"):

        if st.session_state.minutes <= 0:
            st.warning("Вкажи кількість хвилин!")

        else:
            new_record = {
                "Дата": str(selected_date),
                "Категорія": category,
                "Хвилини": st.session_state.minutes
            }

            st.session_state.habits.append(new_record)
            save_data()

            st.success("✅ Запис додано!")


# СТАТИСТИКА
st.divider()
st.subheader("📈 Моя статистика")

habits = st.session_state.habits

if habits:

    total_minutes = sum(
        int(record["Хвилини"])
        for record in habits
    )

    total_records = len(habits)
    total_hours = round(total_minutes / 60, 1)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📝 Записи", total_records)

    with col2:
        st.metric("⏱️ Хвилини", total_minutes)

    with col3:
        st.metric("🕒 Години", total_hours)

    # ПОДГОТОВКА ДАННЫХ
    categories = {}
    days = {}

    for record in habits:
        name = record["Категорія"]
        minutes = int(record["Хвилини"])
        day = str(record["Дата"])[:10]

        categories[name] = (
            categories.get(name, 0) + minutes
        )

        days[day] = days.get(day, 0) + minutes

    category_data = [
        {"Категорія": name, "Хвилини": minutes}
        for name, minutes in categories.items()
    ]

    day_data = [
        {"Дата": day, "Хвилини": minutes}
        for day, minutes in sorted(days.items())
    ]

    # ГРАФИК 1 — СТОЛБЧАТЫЙ
    st.subheader("📊 Хвилини за категоріями")

    fig_bar = px.bar(
        category_data,
        x="Категорія",
        y="Хвилини",
        color="Категорія",
        title="Активність за категоріями"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    # ГРАФИК 2 — ЛИНЕЙНЫЙ
    st.subheader("📈 Динаміка активності")

    fig_line = px.line(
        day_data,
        x="Дата",
        y="Хвилини",
        markers=True,
        title="Активність по днях"
    )

    st.plotly_chart(
        fig_line,
        use_container_width=True
    )

    # ГРАФИК 3 — КРУГОВОЙ
    st.subheader("🥧 Розподіл часу")

    fig_pie = px.pie(
        category_data,
        names="Категорія",
        values="Хвилини",
        title="Частка кожної категорії",
        hole=0.3
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

    # ИСТОРИЯ
    st.divider()
    st.subheader("📋 Всі записи")

    st.dataframe(
        list(reversed(habits)),
        use_container_width=True,
        hide_index=True
    )

    if st.button("🗑️ Очистити історію"):
        st.session_state.habits = []
        save_data()
        st.rerun()

else:
    st.info(
        "Поки що немає записів. "
        "Додай першу активність!"
    )
