"""
CLI para fazer o download de uma playlist de audios do YouTube na pasta corrente.
"""

import os
import re
from pytube import Playlist
from pytube.innertube import _default_clients
from pytube import cipher

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

def download_playlist(playlist_url):
    playlist = Playlist(playlist_url)

    for video in playlist.videos:
        print(f"Downloading: {video.title}")
        
        # Baixa a melhor stream de áudio disponível (pode não ser exatamente .m4a)
        audio_stream = video.streams.filter(only_audio=True).order_by('abr').desc().first()
        audio_stream.download(filename_prefix="audio_")

        print(f"Downloaded: {video.title}")

if __name__ == "__main__":
    playlist_url = input("Digite o link da playlist do YouTube: ")
    download_playlist(playlist_url)
    print("Todos os arquivos foram baixados com sucesso!")
