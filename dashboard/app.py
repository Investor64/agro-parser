# dashboard/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# ─────────────────────────────────────────────────────────────
# Настройки страницы
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🥕 АгроЦены | Краснодар",
    page_icon="🥕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# Константы
# ─────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000/api"
TARGET_PRODUCTS = ["лук", "чеснок", "морковь", "картофель", "клубника", "помидоры", "огурцы"]

# ─────────────────────────────────────────────────────────────
# Функции работы с API
# ─────────────────────────────────────────────────────────────
def login_user(username: str, password: str) -> str | None:
    """Авторизация и получение токена"""
    try:
        response = requests.post(
            f"{API_BASE}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
    except:
        pass
    return None

def get_prices(token: str, product: str = None, days: int = 30) -> list:
    """Получить данные о ценах"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"days": days}
    if product:
        params["product"] = product
    
    try:
        response = requests.get(f"{API_BASE}/prices/", headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def get_stats(token: str, product: str, days: int = 30) -> dict | None:
    """Получить статистику по товару"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(
            f"{API_BASE}/prices/stats/{product}",
            headers=headers,
            params={"days": days}
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def export_to_excel(df: pd.DataFrame, filename: str) -> bytes:
    """Экспорт DataFrame в Excel (в памяти)"""
    from io import BytesIO
    
    # Создаём копию DataFrame для экспорта
    df_export = df.copy()
    
    # Убираем timezone из datetime колонок (Excel не поддерживает)
    if 'collected_at' in df_export.columns:
        df_export['collected_at'] = pd.to_datetime(df_export['collected_at']).dt.tz_localize(None)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_export.to_excel(writer, index=False, sheet_name="Цены")
    return output.getvalue()

# ─────────────────────────────────────────────────────────────
# Управление сессией
# ─────────────────────────────────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None

# ─────────────────────────────────────────────────────────────
# Страница логина
# ─────────────────────────────────────────────────────────────
def login_page():
    st.title("🔐 Вход в систему")
    st.info("Введите учётные данные для доступа к дашборду")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        username = st.text_input("👤 Логин", key="login_user")
        password = st.text_input("🔑 Пароль", type="password", key="login_pass")
    
    if st.button("Войти", type="primary", use_container_width=True):
        token = login_user(username, password)
        if token:
            st.session_state.token = token
            st.session_state.username = username
            st.rerun()
        else:
            st.error("❌ Неверный логин или пароль")
    
    st.markdown("---")
    st.caption("💡 Тестовый доступ: `dan_test_001` / `pass123`")

# ─────────────────────────────────────────────────────────────
# Основной дашборд
# ─────────────────────────────────────────────────────────────
def dashboard_page():
    # Хедер
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🥕 Мониторинг цен | Краснодарский край")
    with col2:
        if st.button("🚪 Выйти"):
            st.session_state.token = None
            st.session_state.username = None
            st.rerun()
    
    # Сайдбар с фильтрами
    with st.sidebar:
        st.header("🔍 Фильтры")
        
        product = st.selectbox("Товар", ["Все"] + TARGET_PRODUCTS)
        days = st.slider("Период (дни)", 7, 90, 30, step=7)
        source = st.multiselect("Источники", ["agroserver", "rosstat", "foodcity", "manual"], default=["agroserver", "rosstat"])
        
        st.markdown("---")
        st.caption(f"👤 Пользователь: `{st.session_state.username}`")
        st.caption(f"🕐 Обновлено: {datetime.now().strftime('%H:%M')}")
    
    # Загрузка данных
    with st.spinner("📊 Загрузка данных..."):
        prices = get_prices(st.session_state.token, product if product != "Все" else None, days)
    
    if not prices:
        st.warning("⚠️ Нет данных за выбранный период")
        return
    
    # Преобразование в DataFrame
    df = pd.DataFrame(prices)
    df["collected_at"] = pd.to_datetime(df["collected_at"])
    
    # Фильтр по источникам
    if source:
        df = df[df["source"].isin(source)]
    
    # ─────────────────────────────────────────────────────────
    # Метрики (карточки)
    # ─────────────────────────────────────────────────────────
    if not df.empty:
        current = df["price"].iloc[-1]
        avg = df["price"].mean()
        min_p = df["price"].min()
        max_p = df["price"].max()
        change = ((df["price"].iloc[-1] / df["price"].iloc[0]) - 1) * 100 if len(df) > 1 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Текущая цена", f"{current:.1f} ₽/кг")
        col2.metric("📈 Средняя", f"{avg:.1f} ₽/кг")
        col3.metric("📉 Изменение", f"{change:+.1f}%", delta_color="inverse")
        col4.metric("📊 Диапазон", f"{min_p:.1f}–{max_p:.1f} ₽")
    
    # ─────────────────────────────────────────────────────────
    # Основной график
    # ─────────────────────────────────────────────────────────
    st.subheader("📈 Динамика цен")
    
    if not df.empty:
        fig = px.line(
            df.sort_values("collected_at"),
            x="collected_at",
            y="price",
            color="source",
            title=f"Цена: {product if product != 'Все' else 'Все товары'}",
            labels={"price": "Цена (₽/кг)", "collected_at": "Дата", "source": "Источник"},
            markers=True
        )
        fig.update_layout(hovermode="x unified", height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # ─────────────────────────────────────────────────────────
    # Статистика по товарам (если выбран "Все")
    # ─────────────────────────────────────────────────────────
    if product == "Все":
        st.subheader("📊 Сводка по товарам")
        
        stats_data = []
        for prod in TARGET_PRODUCTS:
            stats = get_stats(st.session_state.token, prod, days)
            if stats:
                stats_data.append(stats)
        
        if stats_data:
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(
                stats_df[["product", "current_price", "avg_price", "change_percent"]].round(2),
                use_container_width=True,
                column_config={
                    "product": "Товар",
                    "current_price": st.column_config.NumberColumn("Цена (₽)", format="%.1f"),
                    "avg_price": st.column_config.NumberColumn("Средняя (₽)", format="%.1f"),
                    "change_percent": st.column_config.NumberColumn("Изменение (%)", format="%.1f%%")
                }
            )
    
    # ─────────────────────────────────────────────────────────
    # Таблица с данными + Экспорт
    # ─────────────────────────────────────────────────────────
    with st.expander("📋 Исходные данные", expanded=False):
        st.dataframe(
            df[["collected_at", "product", "price", "source", "category"]].sort_values("collected_at", ascending=False),
            use_container_width=True
        )
        
        # Кнопка экспорта
        if not df.empty:
            excel_data = export_to_excel(
                df[["collected_at", "product", "category", "price", "currency", "unit", "source", "region"]],
                f"agro_prices_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )
            st.download_button(
                label="📥 Скачать Excel-отчёт",
                data=excel_data,
                file_name=f"agro_prices_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

# ─────────────────────────────────────────────────────────────
# Главный вход
# ─────────────────────────────────────────────────────────────
def main():
    if st.session_state.token is None:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()