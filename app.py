import streamlit as st
import json
import os
import pypdf
import base64
from datetime import datetime

CONFIG_FILE = "certificate_config.json"

DEFAULT_CONFIG = {
    "doc_types": ["Сертификат о соответствии", "Декларация о соответствии", "Отказное письмо", "Свидетельство о государственной регистрации"],
    "regulations": ["ГОСТ 32585-2013", "ТР ТС 004/2011", "ТР ТС 010/2011", "ТР ТС 020/2011"],
    "brands": ["Frap", "Smeg", "Gorenje", "Miele", "Bosch"],
    "products": ["латунные фитинги", "смесители", "стиральная машина", "водонагреватель"]
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

st.set_page_config(layout="wide", page_title="Генератор наименований сертификатов PDF")

st.title("📄 Генератор наименований для сертификатов PDF")

config = load_config()

# Разделение экрана на две колонки: Слева — просмотр PDF и информация, Справа — форма и превью
col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.subheader("📁 Исходный документ и просмотр")
    uploaded_file = st.file_uploader("Выберите PDF файл (по одному файлу)", type=["pdf"])
    
    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()
            reader = pypdf.PdfReader(uploaded_file)
            num_pages = len(reader.pages)
            file_size = len(file_bytes) / 1024 # КБ
            
            st.success("Файл успешно загружен!")
            st.markdown(f"""
            - **Имя:** {uploaded_file.name}
            - **Размер:** {file_size:.1f} КБ
            - **Количество страниц:** {num_pages}
            """)
            
            # Отображение содержимого PDF прямо в интерфейсе с помощью iframe (base64)
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Временное сохранение для скачивания
            with open("temp_uploaded.pdf", "wb") as f:
                f.write(file_bytes)
                
        except Exception as e:
            st.error(f"Ошибка чтения файла: {e}")
    else:
        st.info("Загрузите PDF-файл, чтобы увидеть его содержимое здесь.")

with col_right:
    st.subheader("⚙️ Параметры наименования по маске")
    
    # 1. Тип документа
    selected_doc_type = st.selectbox("Тип документа", config["doc_types"])
    custom_doc_type = st.text_input("Или введите свой тип документа:", "")
    final_doc_type = custom_doc_type.strip() if custom_doc_type.strip() else selected_doc_type
    skip_doc_type = st.checkbox("Пропустить тип документа", value=False, key="skip_doc")
    
    st.markdown("---")
    
    # 2. Тип регламента
    selected_reg = st.selectbox("Тип регламента", config["regulations"])
    custom_reg = st.text_input("Или введите свой регламент:", "")
    final_reg = custom_reg.strip() if custom_reg.strip() else selected_reg
    skip_reg = st.checkbox("Пропустить тип регламента", value=False, key="skip_reg")

    st.markdown("---")

    # 3. Бренд
    selected_brand = st.selectbox("Бренд", config["brands"])
    custom_brand = st.text_input("Или введите свой бренд:", "")
    final_brand = custom_brand.strip() if custom_brand.strip() else selected_brand
    skip_brand = st.checkbox("Пропустить бренд", value=False, key="skip_brand")

    st.markdown("---")

    # 4. Тип продукции
    selected_prod = st.selectbox("Тип продукции", config["products"])
    custom_prod = st.text_input("Или введите свой тип продукции:", "")
    final_prod = custom_prod.strip() if custom_prod.strip() else selected_prod
    skip_prod = st.checkbox("Пропустить тип продукции", value=False, key="skip_prod")

    st.markdown("---")

    # 5. Дата истечения
    default_date = datetime.now().strftime("%Y1231")
    expiry_date = st.text_input("Дата истечения (ГГГММДД, без пробелов):", value=default_date)
    skip_date = st.checkbox("Пропустить дату истечения", value=False, key="skip_date")

    # Кнопка сохранения новых введенных данных в JSON
    if st.button("💾 Сохранить новые пункты в память (JSON)"):
        updated = False
        if custom_doc_type.strip() and custom_doc_type.strip() not in config["doc_types"]:
            config["doc_types"].append(custom_doc_type.strip())
            updated = True
        if custom_reg.strip() and custom_reg.strip() not in config["regulations"]:
            config["regulations"].append(custom_reg.strip())
            updated = True
        if custom_brand.strip() and custom_brand.strip() not in config["brands"]:
            config["brands"].append(custom_brand.strip())
            updated = True
        if custom_prod.strip() and custom_prod.strip() not in config["products"]:
            config["products"].append(custom_prod.strip())
            updated = True
        
        if updated:
            save_config(config)
            st.success("Новые значения успешно сохранены в файл конфигурации!")
            st.rerun()
        else:
            st.info("Новые уникальные значения не найдены.")

    # Формирование итогового наименования
    parts = []
    if not skip_doc_type and final_doc_type:
        parts.append(final_doc_type)
    if not skip_reg and final_reg:
        parts.append(final_reg)
    if not skip_brand and final_brand:
        parts.append(final_brand)
    if not skip_prod and final_prod:
        parts.append(final_prod)
    if not skip_date and expiry_date:
        parts.append(expiry_date.strip())

    result_name = " ".join(parts) if parts else "document"

    st.markdown("---")
    st.subheader("📌 Итоговое наименование:")
    st.code(result_name + ".pdf", language="")

    # Кнопка скачивания файла с новым именем
    if uploaded_file is not None:
        with open("temp_uploaded.pdf", "rb") as f:
            pdf_bytes_dl = f.read()
        st.download_button(
            label="📥 Сохранить файл под новым именем",
            data=pdf_bytes_dl,
            file_name=result_name + ".pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Для скачивания файла сначала загрузите PDF-файл слева.")
