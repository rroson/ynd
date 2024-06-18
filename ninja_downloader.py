"""
Youtube Ninja Downloader. Baixe audio e vídeo do Youtube de maneira rápida e eficiente.
"""
import streamlit as st
from pytube import YouTube
import re
import os
# from pytube.cli import on_progress

def download_youtube(lista_downloads, nome_arquivo, dados_video):
    if len(lista_downloads) == 0:
        return(0)
    else:
        home = os.path.expanduser('~')
        if os.path.join(home, 'Downloads'):
            diretorio = os.path.join(home, 'Downloads')
        else:
            diretorio = home
        for itag, stream in lista_downloads.items():
            if itag == 139:
                nome_arquivo = f"{nome_arquivo}.m4a"
            else:
                nome_arquivo = f"{nome_arquivo}_{stream}.mp4"
            
            dados_video.streams.get_by_itag(itag).download(output_path=diretorio, filename=nome_arquivo)
        
        return(1)

col_a, col_b = st.columns([2, 3])
with col_a:
    st.image('./ynd/resources/ynd_256x256.png')
with col_b:
    style = "<style>h1 {text-align: center; font-size: 65px}</style>"
    st.markdown(style, unsafe_allow_html=True)
    st.title("Youtube Ninja Downloader")

link = st.text_input(
    'Cole o link do Youtube aqui e pressione Enter',
    placeholder='Cole o link aqui...',
)

if link:
    st.text('Confira as informações abaixo...')
    try:
        dados_video = YouTube(link)
    except:
        st.warning('Link inválido')

    col_a, col_b = st.columns(2)
    with col_a:
        st.image(dados_video.thumbnail_url)
    with col_b:
        st.markdown(f"[{dados_video.title}]({dados_video.watch_url})")
    st.info(f"Duração: {dados_video.length} segundos")
    
    lista_streaming = list(dados_video.streams.filter(progressive=True))
    audio = dados_video.streams.filter(only_audio=True).first()
    
    st.divider()
    st.subheader("Marque as opções que deseja baixar e clique no botão Download:")
    nome_arquivo = re.sub('[\\/:"*.@#!?<>|]+', '-', dados_video.title)
    st.text(f"Nome do arquivo: {nome_arquivo}")

    lista_downloads = {}

    with st.container(border=True):
        itens = 1
        checked_audio = st.checkbox(f"{itens} - Tipo: {audio.mime_type}  -  Itag: {audio.itag}", value=False)
        if checked_audio:
            lista_downloads[audio.itag] = "Arquivo de Audio .m4a"
        for i in range(len(lista_streaming)):
            itens += 1
            checked = st.checkbox(f"{itens} - Tipo: {lista_streaming[i].mime_type}  -  Itag: {lista_streaming[i].itag}  -  Resolução: {lista_streaming[i].resolution}", value=False)
            if checked:
                lista_downloads[lista_streaming[i].itag] = lista_streaming[i].resolution[-4:]

    retorno = st.button(
        "Download",
        on_click=download_youtube,
        args=(lista_downloads, nome_arquivo, dados_video),
        type="primary",
    )

    if retorno:
        if retorno == False:
            st.warning("Nenhum item selecionado!")
        else:
            st.success("Download(s) concluído na pasta Downloads!")
            # reiniciar a pagina da aplicação removendo todos os widgets
            


    #Mostrar lista de downloads na tela
    st.text("Lista de downloads:")
    for itag, stream in lista_downloads.items():
        st.text(f"Itag {itag}: Baixar Vídeo: {stream}")
    



    

