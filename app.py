import streamlit as st
import json
import os

ARQUIVO_DADOS = 'dados_peixes.json'

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

if 'peixes' not in st.session_state:
    st.session_state.peixes = carregar_dados()

st.title("🐟 Catálogo de Espécies de Peixes")
st.sidebar.title("Navegação")
opcao = st.sidebar.radio("Escolha uma opção:", ["Listar Espécies", "Pesquisar", "Cadastrar", "Alterar/Excluir"])

if opcao == "Listar Espécies":
    st.header("Catálogo Completo")
    for peixe in st.session_state.peixes:
        st.subheader(f"{peixe['nome_popular']} ({peixe['nome_cientifico']})")
        st.write(f"**Habitat:** {peixe['habitat']} | **Tamanho:** {peixe['tamanho']} | **Peso:** {peixe['peso']}")
        st.divider()

elif opcao == "Pesquisar":
    st.header("Buscar no Banco de Dados")
    busca = st.text_input("Digite o nome popular ou científico:")
    if busca:
        resultados = [p for p in st.session_state.peixes if busca.lower() in p['nome_popular'].lower() or busca.lower() in p['nome_cientifico'].lower()]
        if resultados:
            for peixe in resultados:
                st.success(f"{peixe['nome_popular']} - {peixe['nome_cientifico']} | Habitat: {peixe['habitat']}")
        else:
            st.warning("Espécie não encontrada.")

elif opcao == "Cadastrar":
    st.header("Cadastrar Nova Espécie")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome Popular")
        cientifico = st.text_input("Nome Científico")
        habitat = st.text_input("Habitat (ex: Água doce, Marinho)")
        tamanho = st.text_input("Tamanho Estimado")
        peso = st.text_input("Peso Médio")
        submit = st.form_submit_button("Salvar Espécie")

        if submit:
            novo = {"nome_popular": nome, "nome_cientifico": cientifico, "habitat": habitat, "tamanho": tamanho, "peso": peso}
            st.session_state.peixes.append(novo)
            salvar_dados(st.session_state.peixes)
            st.success(f"{nome} cadastrado com sucesso!")

elif opcao == "Alterar/Excluir":
    st.header("Gerenciar Catálogo")
    nomes_peixes = [p['nome_popular'] for p in st.session_state.peixes]
    selecionado = st.selectbox("Selecione a espécie para editar ou apagar:", nomes_peixes)

    if selecionado:
        idx = nomes_peixes.index(selecionado)
        peixe_atual = st.session_state.peixes[idx]
        novo_nome = st.text_input("Nome Popular", peixe_atual['nome_popular'])
        novo_cientifico = st.text_input("Nome Científico", peixe_atual['nome_cientifico'])
        
        col1, col2 = st.columns(2)
        if col1.button("Atualizar"):
            st.session_state.peixes[idx]['nome_popular'] = novo_nome
            st.session_state.peixes[idx]['nome_cientifico'] = novo_cientifico
            salvar_dados(st.session_state.peixes)
            st.rerun()
        if col2.button("Excluir"):
            st.session_state.peixes.pop(idx)
            salvar_dados(st.session_state.peixes)
            st.rerun()
