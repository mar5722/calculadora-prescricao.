import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fpdf import FPDF

st.set_page_config(page_title="Calculadora de Prescrição Tributária", layout="wide")

# Inicialização da memória
if 'debitos' not in st.session_state:
    st.session_state.debitos = []

# --- FUNÇÃO PARA GERAR PDF ---
def gerar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Relatorio de Analise de Prescricao Tributaria", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, f"Gerado em: {date.today().strftime('%d/%m/%Y')}", ln=True, align='C')
    pdf.ln(10)

    # Cabeçalho da Tabela
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, "Ano", 1)
    pdf.cell(30, 10, "Vencimento", 1)
    pdf.cell(30, 10, "Valor", 1)
    pdf.cell(100, 10, "Status/Fundamentacao", 1)
    pdf.ln()

    # Dados
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
        pdf.cell(20, 10, str(row['Ano']), 1)
        pdf.cell(30, 10, row['Vencimento'].strftime('%d/%m/%Y'), 1)
        pdf.cell(30, 10, f"R$ {row['Valor']:.2f}", 1)
        pdf.cell(100, 10, str(row['Status']), 1)
        pdf.ln()
    
    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
st.title("⚖️ Calculadora de Prescrição - Conselhos Profissionais")

with st.sidebar:
    st.header("Entrada de Dados")
    ano = st.number_input("Ano da Anuidade", 2000, 2026, 2024)
    valor = st.number_input("Valor Original (R$)", min_value=0.0, value=500.0)
    vencimento = st.date_input("Data de Vencimento")
    evento = st.selectbox("Evento (Art. 174 CTN)", ["Nenhum", "Despacho de Citação", "Parcelamento/Confissão"])
    data_evento = st.date_input("Data do Evento")
    
    if st.button("Adicionar Débito"):
        st.session_state.debitos.append({
            "Ano": ano, "Valor": valor, "Vencimento": vencimento,
            "Evento": evento, "Data_Evento": data_evento
        })

# --- LÓGICA DE CÁLCULO ---
alcada_atual = st.number_input("Valor de Alçada Vigente (INPC)", value=2500.0)

if st.session_state.debitos:
    # (A lógica de cálculo é a mesma que definimos anteriormente)
    df = pd.DataFrame(st.session_state.debitos).sort_values("Vencimento")
    df['Status'] = ""
    hoje = date.today()
    bloco = []
    
    for i, row in df.iterrows():
        inicio_contagem = row['Data_Evento'] if row['Evento'] != "Nenhum" else row['Vencimento']
        
        if row['Vencimento'] < date(2006, 10, 31):
            df.at[i, 'Status'] = "Prescrito (Pre-2011)"
        elif row['Vencimento'] < date(2021, 8, 27):
            bloco.append(i)
            if len(bloco) < 4:
                df.at[i, 'Status'] = f"Aguardando Bloco ({len(bloco)}/4)"
            else:
                prazo_final = inicio_contagem + timedelta(days=5*365)
                df.at[i, 'Status'] = "Em Cobranca" if hoje < prazo_final else "Prescrito (Bloco)"
        else:
            soma_atual = df[df['Ano'] >= 2021]['Valor'].sum()
            if soma_atual < alcada_atual:
                df.at[i, 'Status'] = "Impedida (Alcada Insuficiente)"
            else:
                prazo_final = inicio_contagem + timedelta(days=5*365)
                df.at[i, 'Status'] = "Em Cobranca (Alcada OK)" if hoje < prazo_final else "Prescrito"

    st.dataframe(df, use_container_width=True)

    # --- BOTÕES DE EXPORTAÇÃO ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Limpar Lista"):
            st.session_state.debitos = []
            st.rerun()
    with col2:
        pdf_data = gerar_pdf(df)
        st.download_button(label="📥 Baixar Relatório em PDF",
                           data=pdf_data,
                           file_name=f"relatorio_prescricao_{date.today()}.pdf",
                           mime="application/pdf")
else:
    st.info("Adicione os débitos na barra lateral para gerar o relatório.")