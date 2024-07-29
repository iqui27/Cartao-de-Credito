import streamlit as st
import PyPDF2
from openai import OpenAI
import os

# Configuração da API do OpenAI (substitua com sua chave real, ID da organização e ID do projeto)

client = OpenAI()


# Função para extrair texto do PDF
def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Função para analisar gastos usando a API do ChatGPT
def analyze_expenses(model, system_prompt, user_prompt, text):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"{user_prompt}\n\n{text}"}
        ]
    )
    return response.choices[0].message.content

# Interface do Streamlit
st.title("Analisador de Gastos Mensais")

# Campos para selecionar o modelo e editar os prompts
default_model = "gpt-3.5-turbo"
default_system_prompt = "Você é um assistente financeiro especializado em análise de gastos."
default_user_prompt = "Analise os seguintes gastos mensais e forneça um resumo detalhado, incluindo categorias de gastos, valores totais e sugestões para economia:"

# Inicializar os valores na sessão
if 'model' not in st.session_state:
    st.session_state.model = default_model
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = default_system_prompt
if 'user_prompt' not in st.session_state:
    st.session_state.user_prompt = default_user_prompt
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

# Alternar modo de edição
if st.button("Editar Campos"):
    st.session_state.edit_mode = not st.session_state.edit_mode

# Exibir campos para edição ou os valores atuais
if st.session_state.edit_mode:
    # Obter a lista de modelos disponíveis
    models = client.models.list()
    model_names = [model.id for model in models.data]
    
    model = st.selectbox("Modelo", model_names, index=model_names.index(st.session_state.model) if st.session_state.model in model_names else 0)
    system_prompt = st.text_area("Prompt do Sistema", value=st.session_state.system_prompt)
    user_prompt = st.text_area("Prompt do Usuário", value=st.session_state.user_prompt)
    
    if st.button("Salvar e Fechar"):
        st.session_state.model = model
        st.session_state.system_prompt = system_prompt
        st.session_state.user_prompt = user_prompt
        st.session_state.edit_mode = False
else:
    st.write(f"**Modelo:** {st.session_state.model}")
    st.write(f"**Prompt do Sistema:** {st.session_state.system_prompt}")
    st.write(f"**Prompt do Usuário:** {st.session_state.user_prompt}")

uploaded_file = st.file_uploader("Carregue seu PDF de gastos mensais", type="pdf")

if uploaded_file is not None:
    st.write("Arquivo carregado com sucesso!")
    
    if st.button("Analisar Gastos"):
        with st.spinner("Analisando seus gastos..."):
            # Extrair texto do PDF
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.write("Texto extraído do PDF:")
            st.write(pdf_text)
            
            # Analisar gastos usando a API do ChatGPT
            analysis = analyze_expenses(st.session_state.model, st.session_state.system_prompt, st.session_state.user_prompt, pdf_text)
            st.write("Análise realizada:")
            
            # Exibir resultados
            st.subheader("Análise de Gastos")
            st.write(analysis)
            
            # Adicionar um botão para baixar a análise
            st.download_button(
                label="Baixar Análise",
                data=analysis.encode('utf-8'),  # Convertendo a string para bytes
                file_name="analise_gastos.txt",
                mime="text/plain"
            )