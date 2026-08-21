# TypeClipboard

Pequeno app para macOS que **digita uma senha ou texto como se fosse o teclado**.

Serve para aqueles consoles onde `Cmd+V` / `Ctrl+V` simplesmente não funciona:
noVNC e SPICE do **Proxmox**, iDRAC, iLO, IPMI, VMware Remote Console, consoles
de switches, instaladores de sistema operacional, etc.

## Como funciona

1. Abra o app
2. Digite (ou cole) a senha no campo
3. Clique em **COLAR**
4. Você tem alguns segundos para clicar no campo de destino do console
5. O texto é digitado caractere por caractere

## Instalação

```bash
git clone https://github.com/evertonpasqualin/typeclipboard.git
cd typeclipboard
chmod +x install.sh
./install.sh
```

O instalador:

- procura um Python 3 com Tkinter (python.org ou Homebrew)
- cria um ambiente virtual isolado em `~/Library/Application Support/TypeClipboard`
- instala o `pyautogui` (nada é instalado no Python do sistema)
- gera o app `~/Applications/TypeClipboard.app`

### Permissão obrigatória

Na primeira execução o macOS vai bloquear a simulação de teclado. Vá em:

**Ajustes do Sistema → Privacidade e Segurança → Acessibilidade** → ative
**TypeClipboard**.

Feche e abra o app novamente depois de autorizar.

> Se o macOS disser que o app é de "desenvolvedor não identificado", clique com o
> botão direito no app → **Abrir** → **Abrir**.

## Requisitos

- macOS 11 ou superior
- Python 3.9+ com Tkinter
  - recomendado: instalador oficial do [python.org](https://www.python.org/downloads/macos/)
  - ou Homebrew: `brew install python python-tk`

## Rodar sem instalar

```bash
pip3 install pyautogui
python3 typeclipboard_gui.py
```

Nesse caso a permissão de Acessibilidade precisa ser dada ao **Terminal**.

## Opções da janela

| Opção | O que faz |
|---|---|
| Mostrar texto | tira a máscara de senha do campo |
| Enter no final | pressiona Enter depois de digitar |
| Esconder janela ao digitar | some com a janela durante a digitação |
| Contagem regressiva | tempo para você clicar no destino (1–30s) |
| `Esc` | cancela a contagem |

## Desinstalar

```bash
./uninstall.sh
```

## Segurança

O texto digitado **não é salvo em lugar nenhum**: fica só na memória enquanto a
janela está aberta e é apagado do campo ao final. O app não faz nenhuma conexão
de rede.

Mesmo assim, tenha em mente que ele simula teclas no sistema todo — use com
consciência e sempre confira em qual janela você clicou antes da contagem acabar.

## Licença

MIT — veja [LICENSE](LICENSE).

Feito por Everton Pasqualin.
