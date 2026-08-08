import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
# Configuração da página do Streamlit
st.set_page_config(
    page_title="Assistente de Voo - Cockpit IA",
    page_icon="✈️",
    layout="centered"
)

# Recuperação segura da chave de API das variáveis de ambiente do Render
api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    st.error("Erro crítico: A chave de API (GROQ_API_KEY) não foi encontrada nas variáveis de ambiente do servidor.")
    st.stop()

# Inicialização do cliente Groq
client = Groq(api_key=api_key)

# Interface de Comunicação de Bordo
st.title("✈️ Sistema de Comunicação de Bordo")
st.markdown("Comandante virtual em linha. Como posso auxiliar em nosso plano de voo hoje?")

# Histórico de mensagens na sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Você é um comandante e piloto de aviação comercial sênior com mais de "
                "15 anos de experiência em voos internacionais. Responda com precisão técnica, "
                "clareza didática e termos autênticos da aviação explicados de forma acessível."
            )
        }
    ]

# Exibição das mensagens anteriores
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Entrada do usuário pelo chat
if prompt := st.chat_input("Digite sua dúvida ou comando de voo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta do Assistente / Comandante
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Chamada à API Groq
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=0.7,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in completion:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Atenção na cabine: Ocorreu uma falha de comunicação com os sistemas de bordo ({e})."
            message_placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})