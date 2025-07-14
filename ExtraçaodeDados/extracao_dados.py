import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime

def show_extracao_dados():
    st.title("Extração de Dados de PDFs e DOCX")

    uploaded_file = st.file_uploader("Escolha um arquivo PDF ou DOCX", type=["pdf", "docx"])

    if uploaded_file is not None:
        file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
        st.write(file_details)

        # Salvar o arquivo temporariamente
        temp_file_path = os.path.join("temp", uploaded_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("Arquivo carregado com sucesso!")

        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(temp_file_path)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = extract_text_from_docx(temp_file_path)
        else:
            text = "Tipo de arquivo não suportado para extração de texto."

        st.subheader("Texto Extraído:")
        st.text_area("Conteúdo do arquivo", text, height=300)

        st.subheader("Extração de Informações Específicas:")
        
        # Exemplo: Extrair datas
        dates = re.findall(r'\d{2}/\d{2}/\d{4}', text)
        if dates:
            st.write("Datas encontradas:", dates)
        else:
            st.write("Nenhuma data encontrada no formato DD/MM/AAAA.")

        # Exemplo: Extrair valores monetários (R$ X.XXX,XX)
        money_values = re.findall(r'R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}', text)
        if money_values:
            st.write("Valores monetários encontrados:", money_values)
        else:
            st.write("Nenhum valor monetário encontrado no formato R$ X.XXX,XX.")

        # Exemplo: Extrair CPFs (XXX.XXX.XXX-XX)
        cpfs = re.findall(r'\d{3}\.\d{3}\.\d{3}-\d{2}', text)
        if cpfs:
            st.write("CPFs encontrados:", cpfs)
        else:
            st.write("Nenhum CPF encontrado.")

        # Exemplo: Extrair CNPJs (XX.XXX.XXX/XXXX-XX)
        cnpjs = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', text)
        if cnpjs:
            st.write("CNPJs encontrados:", cnpjs)
        else:
            st.write("Nenhum CNPJ encontrado.")

        # Limpar arquivo temporário
        os.remove(temp_file_path)
        os.rmdir("temp") # Tentar remover a pasta se estiver vazia

def extract_text_from_pdf(pdf_path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Erro ao extrair texto do PDF: {e}"

def extract_text_from_docx(docx_path):
    try:
        from docx import Document
        document = Document(docx_path)
        text = ""
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Erro ao extrair texto do DOCX: {e}"

if __name__ == "__main__":
    show_extracao_dados()