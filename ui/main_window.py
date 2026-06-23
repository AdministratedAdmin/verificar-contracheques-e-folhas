import sys
import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QComboBox,
    QTextEdit, QFileDialog, QToolButton
)

from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtGui import QIcon

from funcoes.contracheque import analisar_contracheque
from funcoes.folha_pagamento import analisar_folha_pagamento

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
icone = os.path.join(diretorio_atual, "icons/contracheque.png")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._configurar_janela()
        self._criar_widgets()
        self._criar_layout()
        self._conectar_sinais()
        self._estilizar()
        self.arquivo = None

    # ----------------------------
    # Configuração
    # ----------------------------
    def _configurar_janela(self):
        self.setWindowTitle("Analisador")
        self.resize(700, 500)
        self.setWindowIcon(QIcon(icone))
    # ----------------------------
    # Widgets
    # ----------------------------
    def _criar_widgets(self):
        self.lbl_arquivo = QLabel("Nenhum contrato selecionado")

        self.escolha = QComboBox()

        self.escolha_opcoes = {
            "Contracheque - EuroSeg": analisar_contracheque,
            "Folha de Pagamento - Produtiva": analisar_folha_pagamento
        }

        # 🔹 POPULA o ComboBox
        self.escolha.addItems(self.escolha_opcoes.keys())

        self.btn_upload = QPushButton("Carregar arquivo")
        self.btn_upload.setIcon(QIcon("ui/icons/upload.png"))

        self.btn_executar = QPushButton("Executar")
        self.btn_executar.setIcon(QIcon("ui/icons/engrenagens.png"))

        self.btn_executar.setObjectName("btnExecutar")

        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)

    # ----------------------------
    # Layout
    # ----------------------------
    def _criar_layout(self):
        central = QWidget()
        layout = QVBoxLayout()

        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(self.lbl_arquivo)
        layout.addWidget(self.btn_upload)
        layout.addWidget(self.escolha)
        layout.addWidget(self.btn_executar)
        layout.addWidget(self.resultado)

        central.setLayout(layout)
        self.setCentralWidget(central)

    # ----------------------------
    # Conexões
    # ----------------------------
    def _conectar_sinais(self):
        self.btn_upload.clicked.connect(self.selecionar_arquivo)
        self.btn_executar.clicked.connect(self.executar)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS  # quando compilado
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def _estilizar(self):
        qss_path = self.resource_path("ui/estilizacao.qss")

        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Arquivo de estilização não encontrado:", qss_path)

    # ----------------------------
    # Lógica
    # ----------------------------
    def executar(self):
        tipo = self.escolha.currentText()

        if not self.arquivo:
            self.resultado.setText("Selecione um arquivo!")
            return

        if tipo not in self.escolha_opcoes:
            self.resultado.setText("Selecione um tipo!")
            return

        algoritmo = self.escolha_opcoes[tipo]

        try:
            resultado = algoritmo(self.arquivo)
            self.resultado.setText(resultado)
        except Exception as e:
            self.resultado.setText(f"Erro ao executar análise:\n{e}")



    def selecionar_arquivo(self):
        arquivo_escolhido, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar contrato",
            "",
            "PDF (*.pdf);;Word (*.docx);;Todos os arquivos (*)"
        )

        if arquivo_escolhido:
            self.arquivo = arquivo_escolhido
            self.lbl_arquivo.setText(arquivo_escolhido)
