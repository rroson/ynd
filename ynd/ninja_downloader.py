"""
Youtube Ninja Downloader. Baixe audio e vídeo do Youtube de maneira rápida e eficiente.
"""
import streamlit as st
from pytube import YouTube
from pytube.innertube import _default_clients
from pytube import cipher
from moviepy.editor import VideoFileClip, AudioFileClip
import re
import os

_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = "19.08.35"
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

def get_throttling_function_name(js: str) -> str:
    """Extract the name of the function that computes the throttling parameter.

    :param str js:
        The contents of the base.js asset file.
    :rtype: str
    :returns:
        The name of the function used to compute the throttling parameter.
    """
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    #logger.debug('Finding throttling function name')
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            #logger.debug("finished regex search, matched: %s", pattern)
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]

    raise re.error("Erro ao processar a expressão regular")

cipher.get_throttling_function_name = get_throttling_function_name

def unir_video_audio(arquivo_video, arquivo_audio, diretorio):
    diretorio = diretorio
    video_filename = arquivo_video
    audio_filename = arquivo_audio

    video_path = os.path.join(diretorio, video_filename)
    audio_path = os.path.join(diretorio, audio_filename)

    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path)

    video_with_audio = video.set_audio(audio)

    output_filename = f"{arquivo_video[:-4]}_video_com_audio.mp4"
    output_path = os.path.join(diretorio, output_filename)
    video_with_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")

    video.close()
    audio.close()

    os.remove(video_path)
    os.remove(audio_path)


def download_youtube(lista_downloads, nome_arquivo, dados_video):
    key = 0
    if len(lista_downloads) == 0:
        return(0)
    else:
        home = os.path.expanduser('~')
        if os.path.join(home, 'Downloads'):
            diretorio = os.path.join(home, 'Downloads')
        else:
            diretorio = home
        for itag, stream in lista_downloads.items():
            if itag == 140:
                nome_arquivo_audio = f"{nome_arquivo}.m4a"
                dados_video.streams.get_by_itag(itag).download(output_path=diretorio, filename=nome_arquivo_audio)
                key += 1
            else:
                nome_arquivo_video = f"{nome_arquivo}_{stream}.mp4"
                dados_video.streams.get_by_itag(itag).download(output_path=diretorio, filename=nome_arquivo_video)
                key += 1
        if key == 2:
            unir_video_audio(nome_arquivo_video, nome_arquivo_audio, diretorio)

        return(1)

col_a, col_b = st.columns([2, 3])
with col_a:
    st.image('./resources/ynd_256x256.png')
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
        st.stop()

    col_a, col_b = st.columns(2)
    with col_a:
        st.image(dados_video.thumbnail_url)
    with col_b:
        st.markdown(f"[{dados_video.title}]({dados_video.watch_url})")
    st.info(f"Duração: {dados_video.length} segundos")
    
    try:
        lista_streaming = dados_video.streams.filter(file_extension='mp4').order_by('resolution')
        # lista_streaming = dados_video.streams.filter(progressive=True)
    except Exception as err:
        st.warning(f"Unexpected {err=}, {type(err)=}")
        raise
        
    audio = dados_video.streams.filter(only_audio=True).first()
    
    st.divider()
    st.subheader("Marque as opções que deseja baixar e clique no botão Download:")
    nome_arquivo = re.sub('[\\/:"*.@#!?<>|]+', '-', dados_video.title)
    st.text(f"Nome do arquivo: {nome_arquivo}")

    lista_downloads = {}

    with st.container(border=True):
        checked_audio = st.checkbox(f"{1} - Tipo: {audio.mime_type}  -  Itag: {audio.itag}", value=False)
        if checked_audio:
            lista_downloads[audio.itag] = "Arquivo_de_Audio"
        for i in range(len(lista_streaming)):
            checked = st.checkbox(f"{i} - Tipo: {lista_streaming[i].mime_type}  -  Itag: {lista_streaming[i].itag}  -  Resolução: {lista_streaming[i].resolution}", value=False)
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
    



    

