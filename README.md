# Arquivo: README.md

# YouTube Downloader Pro

YouTube Downloader Pro é uma aplicação gráfica premium que permite baixar vídeos e áudios do YouTube com facilidade e segurança. Desenvolvido com Python, Tkinter e ttkbootstrap, o aplicativo oferece uma interface moderna e recursos avançados, como seleção de formato de download, monitoramento em tempo real do progresso e cancelamento do download.

## Funcionalidades
- **Suporte a múltiplos formatos:** Baixe somente o vídeo, somente o áudio ou vídeo e áudio juntos.
- **Interface amigável:** Layout moderno com tema "cyborg" utilizando ttkbootstrap.
- **Monitoramento de progresso:** Barra de progresso e atualização de status durante o download.
- **Cancelamento de download:** Possibilidade de interromper o download a qualquer momento.
- **Notificações:** Aviso na tela e notificação do sistema quando o download for concluído.
- **Instalação automática de dependências:** O aplicativo instala e verifica dependências necessárias, como `yt-dlp` e `ffmpeg`.

## Requisitos
- Python 3.x
- Módulos Python: os, sys, subprocess, logging, re, shutil, threading, tkinter, shlex, time, ttkbootstrap, plyer

## Instalação
1. Certifique-se de ter o Python 3.x instalado no seu sistema.
2. Instale as dependências necessárias executando:
   ```
   pip install yt-dlp ttkbootstrap plyer imageio[ffmpeg]
   ```
3. Faça o download deste repositório e execute o arquivo `You.py`.

## Uso
1. Execute o aplicativo:
   ```
   python You.py
   ```
2. Insira a URL do vídeo do YouTube no campo indicado.
3. Selecione o formato desejado (somente vídeo, somente áudio ou vídeo e áudio).
4. Escolha a pasta de destino ou utilize a pasta padrão.
5. Clique em "INICIAR DOWNLOAD" para iniciar o processo.
6. Caso necessário, utilize o botão "CANCELAR DOWNLOAD" para abortar a operação.

## Observações
- O aplicativo atualiza automaticamente o PATH para incluir os scripts necessários.
- Em caso de falha na instalação do `yt-dlp` ou `ffmpeg`, serão apresentadas mensagens de erro e instruções de instalação.
- Desenvolvido com dedicação por **DevFerreiraG**.

---
