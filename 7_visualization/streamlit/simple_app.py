from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "penguins.csv"

st.set_page_config(page_title="Пингвины Палмера", page_icon="🐧", layout="wide")
sns.set_theme(style="whitegrid")


@st.cache_data
def load_csv(source) -> pd.DataFrame:
    return pd.read_csv(source)


def none_label(value):
    return "— нет —" if value is None else value


if __name__ == '__main__':
    st.sidebar.header("Данные и фильтры")
    uploaded = st.sidebar.file_uploader("Свой CSV (необязательно)", type="csv")
    df = load_csv(uploaded if uploaded is not None else DATA_PATH)

    num_cols = df.select_dtypes("number").columns.tolist()
    cat_cols = [c for c in df.select_dtypes(
        exclude="number").columns if df[c].nunique() <= 12]

    if len(num_cols) < 2:
        st.error("Нужно минимум два числовых столбца.")
        st.stop()

    mask = pd.Series(True, index=df.index)
    for col in cat_cols:
        options = sorted(df[col].dropna().unique())
        chosen = st.sidebar.multiselect(col, options, default=options)
        mask &= df[col].isin(chosen) | df[col].isna()

    drop_na = st.sidebar.checkbox("Убрать строки с пропусками", value=False)
    filtered = df[mask]
    if drop_na:
        filtered = filtered.dropna()

    if filtered.empty:
        st.warning("Под выбранные фильтры не попало ни одной строки.")
        st.stop()

    st.title("🐧 Дашборд: пингвины Палмера")
    st.caption("Тема 7. Визуализация · matplotlib + seaborn + Streamlit")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Строк", len(filtered), delta=len(
        filtered) - len(df), delta_color="off")
    c2.metric("Доля от всех данных", f"{len(filtered) / len(df):.0%}")
    c3.metric("Пропусков", int(filtered.isna().sum().sum()))
    c4.metric(f"Среднее: {num_cols[0]}", f"{filtered[num_cols[0]].mean():.1f}")

    tab_dist, tab_rel, tab_data = st.tabs(["Распределения", "Связи", "Данные"])

    with tab_dist:
        left, right = st.columns([1, 3])
        with left:
            col = st.selectbox("Числовой признак", num_cols, key="dist_col")
            kind = st.radio(
                "Тип графика", ["Гистограмма", "KDE", "Boxplot", "Violin"])
            hue = st.selectbox("Раскраска (hue)", [
                               None] + cat_cols, format_func=none_label, key="dist_hue")
        with right:
            fig, ax = plt.subplots(figsize=(8, 4.5))
            if kind == "Гистограмма":
                sns.histplot(data=filtered, x=col, hue=hue, kde=True, ax=ax)
            elif kind == "KDE":
                sns.kdeplot(data=filtered, x=col, hue=hue,
                            fill=True, common_norm=False, ax=ax)
            elif kind == "Boxplot":
                sns.boxplot(data=filtered, x=hue, y=col, ax=ax)
            else:
                sns.violinplot(data=filtered, x=hue, y=col, ax=ax)
            ax.set_title(f"{kind}: {col}")
            st.pyplot(fig)

    with tab_rel:
        left, right = st.columns([1, 3])
        with left:
            x = st.selectbox("Ось X", num_cols, index=0, key="rel_x")
            y = st.selectbox("Ось Y", num_cols, index=1, key="rel_y")
            hue2 = st.selectbox("Раскраска (hue)", [
                                None] + cat_cols, format_func=none_label, key="rel_hue")
            trend = st.checkbox("Линия тренда", value=True)
        with right:
            if trend:
                g = sns.lmplot(data=filtered, x=x, y=y,
                               hue=hue2, height=4.5, aspect=1.5)
                st.pyplot(g.figure)
            else:
                fig, ax = plt.subplots(figsize=(8, 4.5))
                sns.scatterplot(data=filtered, x=x, y=y, hue=hue2, ax=ax)
                st.pyplot(fig)

    with tab_data:
        st.dataframe(filtered)
        with st.expander("Матрица корреляций"):
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(filtered[num_cols].corr(), annot=True, fmt=".2f", cmap="vlag",
                        center=0, vmin=-1, vmax=1, ax=ax)
            st.pyplot(fig)
        st.download_button(
            "Скачать отфильтрованный CSV",
            filtered.to_csv(index=False).encode("utf-8"),
            file_name="filtered.csv",
            mime="text/csv",
        )
