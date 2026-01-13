import streamlit as st
import pandas as pd
from datetime import date, timedelta

st.set_page_config(page_title="Calculadora Prescrição Conselhos", layout="wide")

st.title("⚖️ Calculadora de Prescrição - Conselhos Profissionais")

# --- 1. SELEÇÃO EM MASSA ---
st.header("1. Selecione as Anuidades Devidas")
col1, col2 = st.columns(2)
with col1:
    ano_inicial = st.number_input("Ano Inicial", 2000, 2026, 2010)
with col2:
    ano_final = st.number_input("Ano Final", 2000, 2026, 2024)

if "dados_anuidades" not in st.session_state:
    st.session_state.dados_anuidades = {}

if st.button("Gerar Tabela de Anuidades"):
    # Cria um dicionário para armazenar os dados de cada ano
    for ano in range(ano_inicial, ano_final + 1):
        if ano not in st.session_state.dados_anuidades:
            st.session_state.dados_anuidades[ano] = {
                "vencimento": date(ano, 3, 31),
                "situacao": "Normal",
                "data_evento": date(ano, 3, 31)
            }
    st.rerun()

# --- 2. EDIÇÃO E CÁLCULO ---
if st.session_state.dados_anuidades:
    st.header("2. Detalhar Marcos do Art. 174 CTN")
    st.info("Ajuste a situação de cada ano abaixo para recalcular a prescrição.")
    
    lista_final = []
    
    # Criar a interface de edição linha por linha
    for ano in sorted(st.session_state.dados_anuidades.keys()):
        with st.expander(f"Anuidade {ano}", expanded=False):
            c1, c2, c3 = st.columns(3)
            
            with c1:
                venc = st.date_input(f"Vencimento {ano}", st.session_state.dados_anuidades[ano]["vencimento"], key=f"v_{ano}")
                st.session_state.dados_anuidades[ano]["vencimento"] = venc
            
            with c2:
                sit = st.selectbox(f"Situação {ano}", 
                                   ["Normal", "Em execução fiscal (Suspende)", "Parcelamento (Interrompe)", "Protesto (Interrompe)"],
                                   key=f"s_{ano}")
                st.session_state.dados_anuidades[ano]["situacao"] = sit
                
            with c3:
                # Só mostra campo de data se não for normal
                if sit != "Normal":
                    dt_ev = st.date_input(f"Data do Evento {ano}", st.session_state.dados_anuidades[ano]["data_evento"], key=f"d_{ano}")
                    st.session_state.dados_anuidades[ano]["data_evento"] = dt_ev
                else:
                    st.session_state.dados_anuidades[ano]["data_evento"] = venc

        # --- LÓGICA DE CÁLCULO ---
        status_prescricao = ""
        inicio_contagem = st.session_state.dados_anuidades[ano]["data_evento"]
        hoje = date.today()
        
        # Regra 1: Antes da Lei 12.514/11 (31/10/2011)
        if venc < date(2006, 10, 31):
            status_prescricao = "🔴 Prescrito (Regra anterior a 2011)"
        
        # Regra 2: Lei 12.514/11 (Lógica de Bloco ou Individual pós-bloco)
        # Por enquanto, mantemos a contagem individual para visualização clara do Art. 174
        else:
            prazo = inicio_contagem + timedelta(days=5*365)
            if sit == "Em execução fiscal (Suspende)":
                status_prescricao = "🟡 Suspenso por Execução Fiscal"
            elif hoje > prazo:
                status_prescricao = f"🔴 Prescrito em {prazo.strftime('%d/%m/%Y')}"
            else:
                status_prescricao = f"🟢 Prazo corre até {prazo.strftime('%d/%m/%Y')}"

        lista_final.append({
            "Ano": ano,
            "Vencimento": venc,
            "Situação": sit,
            "Marco Inicial": inicio_contagem,
            "Resultado": status_prescricao
        })

    # --- 3. EXIBIÇÃO DO QUADRO RESUMO ---
    st.header("3. Quadro Resumo de Prescrição")
    df_final = pd.DataFrame(lista_final)
    st.table(df_final)

    if st.button("Limpar Tudo"):
        st.session_state.dados_anuidades = {}
        st.rerun()