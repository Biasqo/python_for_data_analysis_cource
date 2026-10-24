import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

if __name__ == '__main__':
    st.title("Streamlit: первое приложение")
    st.write("Каждое движение виджета **перезапускает скрипт сверху вниз**.")

    n = st.slider("Число точек", min_value=10,
                  max_value=500, value=100, step=10)
    noise = st.slider("Уровень шума", 0.0, 3.0, 0.5)
    show_line = st.checkbox("Показать истинную прямую", value=True)

    rng = np.random.default_rng(42)
    x = np.linspace(0, 10, n)
    y = 2 * x + 1 + rng.normal(0, noise, n)

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.scatter(x, y, s=12, alpha=0.7, label="наблюдения")
    if show_line:
        ax.plot(x, 2 * x + 1, color="tab:red", label="y = 2x + 1")
    ax.set(xlabel="x", ylabel="y", title=f"n = {n}, шум = {noise}")
    ax.legend()
    st.pyplot(fig)

    # session_state переживает перезапуски скрипта
    if "clicks" not in st.session_state:
        st.session_state.clicks = 0
    if st.button("Нажми меня"):
        st.session_state.clicks += 1
    st.write(f"Нажатий за сессию: {st.session_state.clicks}")
