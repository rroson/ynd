"""
Youtube Ninja Downloader. Baixe audio e vídeo do Youtube de maneira rápida e eficiente.
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga import ImageView, Image
import xerox
from pytube import YouTube
import re
import os
import asyncio
import random
# import threading
from concurrent.futures import ThreadPoolExecutor

PADRAO_ITAG = "itag=\"(.*?)\"" #Itag para Download
PADRAO_MIME = "mime_type=\"(.*?)\"" #Tipo vídeo
PADRAO_RES = "res=\"(.*?)\"" #Resolução
PADRAO_ABR = "abr=\"(.*?)\"" #Resolução Audio

class ydn(toga.App):

    def startup(self):
        self.dados_video = ''
        self.titulo = ''
        self.nome_arquivo = ''
        self.porcentagem_conclusao = 0.0
        self.progress = toga.ProgressBar(max=100, value=self.porcentagem_conclusao)
        # Obtem o diretorio onde o arquivo foi executado
        # self.diretorio_corrente = os.path.dirname(__file__)
        self.home = os.path.expanduser('~')
        if os.path.join(self.home, 'Downloads'):
            self.diretorio = os.path.join(self.home, 'Downloads')
        else:
            self.diretorio = self.home
        self.lista_streaming = []
        self.porcentagem = ''
        imagem_icone_celular = Image('./resources/icone_celular.png')
        self.icon_cel = ImageView(image=imagem_icone_celular)
        imagem_icone_monitor = Image('./resources/icone_monitor.png')
        self.icon_monitor = ImageView(image=imagem_icone_monitor)

        imagem_logo = Image('./resources/ynd_500x500.png')
        self.img = ImageView(image=imagem_logo, style=Pack(width=125, height=125))
        self.titulo = toga.Label(
            'Youtube Ninja Downloader', style=Pack(font_size=36, padding=10, font_family="cursive"))
        self.logo_box = toga.Box(
            children=[self.img, self.titulo],
            style=Pack(direction=ROW, padding=10, alignment="center")
        )
        
        self.botao_colar = toga.Button(
            "Colar Link -->",
            on_press=self.colar_link,
            style=Pack(padding=5, width=120, font_size=12)
        )
        self.link_entrada = toga.TextInput(
            placeholder='Cole o link aqui...', style=Pack(flex=1, font_size=12))
        self.botao_listar_videos = toga.Button(
            "Listar Vídeos",
            on_press=self.listar_videos,
            style=Pack(padding=5, width=120, font_size=12)
        )
        self.url_box = toga.Box(
            children=[self.botao_colar, self.link_entrada, self.botao_listar_videos],
            style=Pack(direction=ROW, alignment="center")
        )

        self.main_box = toga.Box(
            children=[self.logo_box, self.url_box],
            style=Pack(direction=COLUMN, padding=10, flex=1, alignment="center")
        )

        # self.main_window = toga.MainWindow(title=self.formal_name, size=(700, 570))
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()
        self.img.refresh()

    def colar_link(self, widget):
        self.texto_clipboard = xerox.paste()
        self.link_entrada.value=self.texto_clipboard
    
    async def mensagem(self, mensagem):
        self.mensagem_label = toga.Label(
            text=mensagem,
            style=Pack(font_size=20, padding=10)
        )
        self.mensagem_label_box = toga.Box(
            children=[self.mensagem_label],
            style=Pack(alignment="center")
        )
        self.main_box.add(self.mensagem_label_box)

    async def listar_videos(self, widget):

        await self.mensagem("Obtendo informações do Vídeo! Aguarde...")
        await asyncio.sleep(0.2)

        try:
            # self.dados_video = YouTube(self.link_entrada.value, use_oauth=True, allow_oauth_cache=True)
            self.dados_video = YouTube(self.link_entrada.value)
        except:
            self.main_window.info_dialog(
                title="Link Incorreto!",
                message=f"Algo não está correto com o link do Youtube ou houve um erro de leitura do vídeo.",
            )
            self.main_box.remove(self.mensagem_label_box)
            self.link_entrada.clear()
            self.link_entrada.focus()
            return

        self.botao_colar.enabled = False
        self.link_entrada.enabled = False
        self.botao_listar_videos.enabled = False
        
        try:
            self.lista_streaming = self.dados_video.streams.filter(progressive=True)
            self.dados_video.register_on_progress_callback(self.progresso_download_video)
            self.audio = self.dados_video.streams.filter(only_audio=True).first()
            self.itag_audio = re.search(PADRAO_ITAG, str(self.audio)).group(1)
            self.itag_abr = re.search(PADRAO_ABR, str(self.audio)).group(1)
            self.titulo = self.dados_video.title   
        except:
            self.main_window.info_dialog(
                title="Erro ao obter dados do vídeo!",
                message=f"Por favor tente novamente.",
            )
            self.botao_colar.enabled = True
            self.link_entrada.enabled = True
            self.botao_listar_videos.enabled = True
            self.main_box.remove(self.mensagem_label_box)
            self.link_entrada.clear()
            self.link_entrada.focus()
            return
        
        self.nome_arquivo = re.sub('[\\/:"*.@#!?<>|]+', '-', self.titulo)
        self.lista_para_download = {}
        opcoes = []

        opcao_switch = toga.Switch(
            text=f"Itag: {self.itag_audio} - Tipo: Audio m4a - Qualidade: {self.itag_abr}",
            value=False,
            on_change=lambda switch, itag=self.itag_audio, resolucao=self.itag_abr: self.downloads_selecionados(itag, resolucao),
            style=Pack(padding=(3, 5, 3, 5), font_size=14)
        )
        opcoes.append(opcao_switch)

        for item in self.lista_streaming:
            self.itag = re.search(PADRAO_ITAG, str(item)).group(1)
            mime_type = re.search(PADRAO_MIME, str(item)).group(1)
            self.resolucao = re.search(PADRAO_RES, str(item)).group(1)

            opcao_switch = toga.Switch(
                text=f"Itag: {self.itag} - Tipo: {mime_type} - Qualidade: {self.resolucao}",
                value=False,
                on_change=lambda switch, resolucao=self.resolucao, itag=self.itag: self.downloads_selecionados(itag, resolucao),
                style=Pack(padding=(3, 5, 3, 5), font_size=14)
            )
            opcoes.append(opcao_switch)

        self.opcoes_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, alignment="center", width=500)
        )

        self.opcoes_box.add(
            toga.Label(
                text="Escolha os arquivos que deseja baixar:",
                style=Pack(font_size=20, alignment="center", padding=10)
            )
        )

        for opcao in opcoes:
            self.opcoes_box.add(opcao)

        self.listagem_videos_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, alignment="center")
        )

        self.titulo_video_label = toga.Label(
            'Título:',
            style=Pack(font_size=16, alignment="center")
        )
        self.titulo_video_nome = toga.Label(
            self.titulo,
            style=Pack(font_size=12)
        )
        self.labels_box = toga.Box(
            children=[self.titulo_video_label, self.titulo_video_nome],
            style=Pack(direction=COLUMN)
        )
        self.botao_download = toga.Button(
            "Download",
            on_press=self.confirma_downloads,
            style=Pack(padding=(20, 30, 20, 30), width=120, font_size=12)
        )
        self.botao_cancelar = toga.Button(
            "Nova Pesquisa",
            on_press=self.limpa_download,
            style=Pack(padding=(20, 30, 20, 30), width=150, font_size=12)
        )
        # botao_abrir_pasta = toga.Button(
        #     "Abrir Pasta",
        #     on_press=self.abrir_pasta,
        #     style=Pack(padding=5, width=120, font_size=12),
        # )
        self.botoes_box = toga.Box(
            children=[self.botao_cancelar, self.botao_download, self.progress],
            style=Pack(direction=ROW, alignment="center")
        )

        self.listagem_videos_box.add(
            self.labels_box,
            self.opcoes_box,
            self.botoes_box
        )

        self.main_box.remove(self.mensagem_label_box)
        self.listagem_videos_box.add(self.opcoes_box)
        self.main_box.add(self.listagem_videos_box)
    
    def abrir_pasta(self, widget=None):
        if os.name == "posix":  # Linux / macOS
            os.system(f"open \"{self.diretorio}\"")
        elif os.name == "nt":  # Windows
            os.system(f"explorer \"{self.diretorio}\"")
    
    def downloads_selecionados(self, itag, resolucao):
        if itag in self.lista_para_download:
            self.lista_para_download.pop(itag)
        else:
            self.lista_para_download[itag] = resolucao
    
    def confirma_downloads(self, widget):
        if self.lista_para_download == {}:
            self.main_window.error_dialog(
                title="Nenhum download foi selecionado",
                message="Escolha os arquivos que deseja baixar clicando sobre eles.",
            )
        else:     
            self.main_window.question_dialog(
                title="Confirmação de downloads",
                message="Deseja baixar o(s) arquivo(s) selecionado(s)?",
                on_result=self.download_arquivo,
            )

    def limpa_download(self, widget):
        self.main_box.remove(self.listagem_videos_box)
        self.main_box.remove(self.mensagem_label_box)
        self.main_box.remove(self.progress)
        self.botao_colar.enabled = True
        self.link_entrada.enabled = True
        self.botao_listar_videos.enabled = True
        self.botao_cancelar.enabled = True
        self.botao_download.enabled = True
        self.link_entrada.clear()
        self.link_entrada.focus()
        return

    async def download_arquivo(self, widget, result):
        if result:
            self.botao_cancelar.enabled = False
            self.botao_download.enabled = False
            executor = ThreadPoolExecutor()

            for itag in self.lista_para_download:
                resolucao = self.lista_para_download[itag]
                if itag == "139":
                    self.nome_arquivo_video = f"{self.nome_arquivo}({resolucao}).m4a"
                    self.stream = self.dados_video.streams.get_by_itag(self.itag_audio)
                else:
                    self.nome_arquivo_video = f"{self.nome_arquivo}({resolucao}).mp4"
                    self.stream = self.dados_video.streams.get_by_itag(itag)

                self.progress.start()
                #await asyncio.sleep(random.random() * 3)
                await asyncio.get_event_loop().run_in_executor(executor, self.stream.download, self.diretorio, self.nome_arquivo_video)
                self.progresso_download_video(self.stream, None, 0)

            self.main_window.info_dialog(
                title="Download Finalizado",
                message=f"O arquivo foi baixado na pasta: {self.diretorio}",
            )
            # self.abrir_pasta()
            self.limpa_download(widget)

        else:
            return
    
    def download_thread(self):
        self.stream.download(output_path=self.diretorio, filename=self.nome_arquivo_video)

    def progresso_download_video(self, stream, chunk, bytes_remaining):
        tamanho_arquivo = stream.filesize
        bytes_downloaded = tamanho_arquivo - bytes_remaining
        self.porcentagem_conclusao = bytes_downloaded / tamanho_arquivo * 100
        self.progress.value = self.porcentagem_conclusao
        if self.porcentagem_conclusao >= 100:
            self.progress.stop()
            self.progress.value = 0


def main():
    return ydn(icon='./resources/Youtube_Ninja_Downloader.ico')
