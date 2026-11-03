import streamlit as st
import json
import os

ARQUIVO_DADOS = 'dados_peixes.json'
PASTA_IMAGENS = 'imagens'

# Garante que a pasta 'imagens' seja criada automaticamente se não existir
if not os.path.exists(PASTA_IMAGENS):
    os.makedirs(PASTA_IMAGENS)

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def salvar_imagem_local(imagem_upload, nome_peixe):
    """Salva a foto upada pelo usuário na pasta local do servidor"""
    if imagem_upload is not None:
        extensao = imagem_upload.name.split('.')[-1]
        # Cria um nome de arquivo sem espaços (ex: acará-bandeira.jpg)
        nome_arquivo = f"{nome_peixe.replace(' ', '_').lower()}.{extensao}"
        caminho_completo = os.path.join(PASTA_IMAGENS, nome_arquivo)
        
        with open(caminho_completo, "wb") as f:
            f.write(imagem_upload.getbuffer())
            
        # Retorna o caminho com barras normais para funcionar bem no GitHub/Streamlit
        return caminho_completo.replace('\\', '/')
    return ""

if 'peixes' not in st.session_state:
    st.session_state.peixes = carregar_dados()

st.title("🐟 Catálogo de Espécies de Peixes")
st.sidebar.title("Navegação")
opcao = st.sidebar.radio("Escolha uma opção:", ["Listar Espécies", "Pesquisar", "Cadastrar", "Alterar/Excluir"])

if opcao == "Listar Espécies":
    st.header("Catálogo Completo")
    for peixe in st.session_state.peixes:
        st.subheader(f"{peixe['nome_popular']} ({peixe['nome_cientifico']})")
        
        if peixe.get("imagem") and os.path.exists(peixe["imagem"]):
            st.image(peixe["imagem"], width=400)
        elif peixe.get("imagem"):
            st.caption(f"⚠️ Imagem não encontrada no servidor.")
                
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
                if peixe.get("imagem") and os.path.exists(peixe["imagem"]):
                    st.image(peixe["imagem"], width=300)
        else:
            st.warning("Espécie não encontrada.")

elif opcao == "Cadastrar":
    st.header("Cadastrar Nova Espécie")
    
    nome = st.text_input("Nome Popular")
    cientifico = st.text_input("Nome Científico")
    habitat = st.text_input("Habitat (ex: Água doce, Marinho)")
    tamanho = st.text_input("Tamanho Estimado")
    peso = st.text_input("Peso Médio")
    
    # Campo de Upload (aceita arrastar, clicar ou colar dependendo do navegador)
    imagem_upload = st.file_uploader("Envie a foto do peixe (Arraste ou Clique)", type=["png", "jpg", "jpeg"])
    
    # Pré-visualização instantânea!
    if imagem_upload is not None:
        st.image(imagem_upload, width=300, caption="Pré-visualização da imagem")
    
    if st.button("Salvar Espécie"):
        if nome:
            caminho_imagem = salvar_imagem_local(imagem_upload, nome) if imagem_upload else ""
            
            novo = {
                "nome_popular": nome, 
                "nome_cientifico": cientifico, 
                "habitat": habitat, 
                "tamanho": tamanho, 
                "peso": peso,
                "imagem": caminho_imagem
            }
            st.session_state.peixes.append(novo)
            salvar_dados(st.session_state.peixes)
            st.success(f"{nome} cadastrado com sucesso!")
        else:
            st.error("O Nome Popular é obrigatório para cadastrar!")

elif opcao == "Alterar/Excluir":
    st.header("Gerenciar Catálogo")
    nomes_peixes = [p['nome_popular'] for p in st.session_state.peixes]
    
    if nomes_peixes:
        selecionado = st.selectbox("Selecione a espécie para editar ou apagar:", nomes_peixes)

        if selecionado:
            idx = nomes_peixes.index(selecionado)
            peixe_atual = st.session_state.peixes[idx]
            
            novo_nome = st.text_input("Nome Popular", peixe_atual['nome_popular'])
            novo_cientifico = st.text_input("Nome Científico", peixe_atual['nome_cientifico'])
            
            st.write("---")
            st.write("**Imagem Atual:**")
            if peixe_atual.get("imagem") and os.path.exists(peixe_atual["imagem"]):
                st.image(peixe_atual["imagem"], width=200)
            else:
                st.caption("Sem imagem cadastrada.")
                
            nova_imagem_upload = st.file_uploader("Substituir foto (deixe vazio para manter a atual)", type=["png", "jpg", "jpeg"])
            
            if nova_imagem_upload is not None:
                st.image(nova_imagem_upload, width=200, caption="Pré-visualização da NOVA imagem")
            
            col1, col2 = st.columns(2)
            if col1.button("Atualizar Espécie"):
                st.session_state.peixes[idx]['nome_popular'] = novo_nome
                st.session_state.peixes[idx]['nome_cientifico'] = novo_cientifico
                
                # Só muda a imagem se o usuário tiver feito upload de uma nova
                if nova_imagem_upload is not None:
                    st.session_state.peixes[idx]['imagem'] = salvar_imagem_local(nova_imagem_upload, novo_nome)
                    
                salvar_dados(st.session_state.peixes)
                st.success("Atualizado!")
                st.rerun()
                
            if col2.button("Excluir Espécie"):
                st.session_state.peixes.pop(idx)
                salvar_dados(st.session_state.peixes)
                st.rerun()
    else:
        st.info("Nenhuma espécie cadastrada no momento.")
