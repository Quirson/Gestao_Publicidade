"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SISTEMA DE GESTÃO DE PUBLICIDADE E MARKETING - INC MOÇAMBIQUE              ║
║  Grupo: Eden Magnus, Francisco Guamba, Malik Dauto, Quirson Ngale           ║
║  Outubro 2025 - Base de Dados Oracle                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import tkinter as tko
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import cx_Oracle
from datetime import datetime
import threading
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkcalendar import DateEntry
import re
# ═════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÕES GLOBAIS
# ═════════════════════════════════════════════════════════════════════════════

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Cores do tema
COLORS = {
    'primary': '#1f538d',  # Azul profissional
    'secondary': '#c41e3a',  # Vermelho destaque
    'accent': '#2d5aa6',  # Azul claro
    'success': '#28a745',  # Verde
    'warning': '#ffc107',  # Amarelo
    'danger': '#dc3545',  # Vermelho perigo
    'dark': '#1a1a1a',  # Fundo escuro
    'light': '#f8f9fa',  # Claro
    'text': '#ffffff',  # Texto branco
    'text_secondary': '#b0b0b0'  # Texto secundário
}

# Configuração do banco de dados
DB_CONFIG = {
    'user': 'Gestao_Publicidade',
    'password': 'ISCTEM',
    'dsn': 'localhost:1521/XEPDB1'
}


# ═════════════════════════════════════════════════════════════════════════════
# CLASSE DE CONEXÃO COM BANCO DE DADOS
# ═════════════════════════════════════════════════════════════════════════════

class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Estabelece conexão com o banco de dados Oracle"""
        try:
            if self._connection is None or not self._connection.ping():
                self._connection = cx_Oracle.connect(**DB_CONFIG)
            return self._connection
        except cx_Oracle.Error as error:
            messagebox.showerror("Erro de Conexão",
                                 f"Falha ao conectar ao banco de dados:\n{error}")
            return None

    def get_cursor(self):
        """Retorna um cursor para executar queries"""
        conn = self.connect()
        if conn:
            return conn.cursor()
        return None

    def execute_query(self, query, params=None, fetch=True):
        """Executa uma query e retorna os resultados"""
        cursor = self.get_cursor()
        if cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if fetch:
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    rows = cursor.fetchall()
                    return columns, rows
                else:
                    self._connection.commit()
                    return True
            except cx_Oracle.Error as error:
                self._connection.rollback()
                messagebox.showerror("Erro SQL", f"Erro ao executar query:\n{error}")
                return None
            finally:
                cursor.close()
        return None

    def close(self):
        """Fecha a conexão com o banco"""
        if self._connection:
            self._connection.close()
            self._connection = None


# ═════════════════════════════════════════════════════════════════════════════
# SPLASH SCREEN ANIMADA
# ═════════════════════════════════════════════════════════════════════════════

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Configuração da janela
        self.title("Sistema de Gestão de Publicidade")
        self.geometry("800x600")
        self.resizable(False, False)

        # Centralizar na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"800x600+{x}+{y}")

        # Remover borda
        self.overrideredirect(True)

        # Frame principal com gradiente simulado
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS['dark'], corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)

        # Logo/Título
        title_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        title_frame.pack(pady=50)

        logo_label = ctk.CTkLabel(
            title_frame,
            text="📢 INC",
            font=("Helvetica", 80, "bold"),
            text_color=COLORS['secondary']
        )
        logo_label.pack()

        title_label = ctk.CTkLabel(
            title_frame,
            text="SISTEMA DE GESTÃO DE\nPUBLICIDADE E MARKETING",
            font=("Helvetica", 24, "bold"),
            text_color=COLORS['primary']
        )
        title_label.pack(pady=10)

        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Instituto Nacional de Comunicação - Moçambique",
            font=("Helvetica", 14),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack()

        # Informações do grupo
        group_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        group_frame.pack(pady=30)

        group_title = ctk.CTkLabel(
            group_frame,
            text="DESENVOLVIDO POR:",
            font=("Helvetica", 12, "bold"),
            text_color=COLORS['text_secondary']
        )
        group_title.pack()

        members = [
            "Eden Magnus",
            "Francisco Guamba",
            "Malik Dauto",
            "Quirson Ngale"
        ]

        for member in members:
            member_label = ctk.CTkLabel(
                group_frame,
                text=f"• {member}",
                font=("Helvetica", 14),
                text_color=COLORS['text']
            )
            member_label.pack(pady=2)

        # Barra de progresso
        self.progress_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_frame.pack(side="bottom", pady=50)

        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            width=400,
            height=8,
            corner_radius=4,
            progress_color=COLORS['secondary']
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self.progress_frame,
            text="Inicializando...",
            font=("Helvetica", 11),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack()

        # Data
        date_label = ctk.CTkLabel(
            self.main_frame,
            text=f"Outubro 2025 - Oracle Database",
            font=("Helvetica", 10),
            text_color=COLORS['text_secondary']
        )
        date_label.pack(side="bottom", pady=10)

    def update_progress(self, value, status):
        """Atualiza a barra de progresso"""
        self.progress_bar.set(value)
        self.status_label.configure(text=status)
        self.update()


# ═════════════════════════════════════════════════════════════════════════════
# APLICAÇÃO PRINCIPAL
# ═════════════════════════════════════════════════════════════════════════════

class MainApplication(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela principal
        self.title("Sistema de Gestão de Publicidade - INC Moçambique")
        self.geometry("1400x800")

        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.winfo_screenheight() // 2) - (800 // 2)
        self.geometry(f"1400x800+{x}+{y}")

        # Configurar grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Banco de dados
        self.db = DatabaseConnection()

        # Variáveis
        self.current_view = None

        # Criar interface
        self.create_sidebar()
        self.create_top_bar()
        self.create_main_content()

        # Mostrar dashboard inicial
        self.show_dashboard()

    def create_sidebar(self):
        """Cria a barra lateral de navegação"""
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLORS['dark'])
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo/Título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['primary'], height=100)
        logo_frame.pack(fill="x", pady=0)

        logo_label = ctk.CTkLabel(
            logo_frame,
            text="📢 INC Sistema",
            font=("Helvetica", 20, "bold"),
            text_color=COLORS['text']
        )
        logo_label.pack(pady=30)

        # Menu de navegação
        menu_items = [
            ("🏠 Dashboard", self.show_dashboard, COLORS['primary']),
            ("👥 Anunciantes", self.show_anunciantes, COLORS['accent']),
            ("📢 Campanhas", self.show_campanhas, COLORS['accent']),
            ("📺 Espaços Publicitários", self.show_espacos, COLORS['accent']),
            ("🎨 Peças Criativas", self.show_pecas, COLORS['accent']),
            ("🏢 Agências", self.show_agencias, COLORS['accent']),
            ("🎯 Público-Alvo", self.show_publico, COLORS['accent']),
            ("💳 Pagamentos", self.show_pagamentos, COLORS['accent']),
            ("📊 Relatórios", self.show_relatorios, COLORS['secondary']),
        ]

        self.menu_buttons = {}
        for text, command, color in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                font=("Helvetica", 14),
                fg_color="transparent",
                hover_color=color,
                anchor="w",
                height=45
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.menu_buttons[text] = btn

        # Botão de sair (no final)
        exit_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Sair",
            command=self.quit_app,
            font=("Helvetica", 14),
            fg_color=COLORS['danger'],
            hover_color="#a02a2a",
            height=45
        )
        exit_btn.pack(side="bottom", fill="x", padx=10, pady=20)

    def create_top_bar(self):
        """Cria a barra superior"""
        self.top_bar = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=COLORS['primary'])
        self.top_bar.grid(row=0, column=1, sticky="ew")
        self.top_bar.grid_propagate(False)

        # Título da página atual
        self.page_title = ctk.CTkLabel(
            self.top_bar,
            text="Dashboard",
            font=("Helvetica", 24, "bold"),
            text_color=COLORS['text']
        )
        self.page_title.pack(side="left", padx=30, pady=15)

        # Info do usuário
        user_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        user_frame.pack(side="right", padx=30)

        date_label = ctk.CTkLabel(
            user_frame,
            text=datetime.now().strftime("%d/%m/%Y %H:%M"),
            font=("Helvetica", 12),
            text_color=COLORS['text']
        )
        date_label.pack(side="right", padx=10)

        user_label = ctk.CTkLabel(
            user_frame,
            text="👤 Admin",
            font=("Helvetica", 12, "bold"),
            text_color=COLORS['text']
        )
        user_label.pack(side="right", padx=10)

    def create_main_content(self):
        """Cria a área de conteúdo principal"""
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color="#2b2b2b")
        self.main_content.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

    def clear_content(self):
        """Limpa o conteúdo atual"""
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Mostra o dashboard principal"""
        self.clear_content()
        self.page_title.configure(text="Dashboard")

        # Container com scroll
        container = ctk.CTkScrollableFrame(self.main_content, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Cards de estatísticas
        stats_frame = ctk.CTkFrame(container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=10)

        # Buscar estatísticas do banco
        stats = self.get_dashboard_stats()

        cards_data = [
            ("📢 Campanhas Ativas", stats.get('campanhas', 0), COLORS['primary']),
            ("👥 Anunciantes", stats.get('anunciantes', 0), COLORS['accent']),
            ("💰 Receita Total", f"{stats.get('receita', 0):,.2f} MT", COLORS['success']),
            ("📺 Espaços Disponíveis", stats.get('espacos', 0), COLORS['secondary'])
        ]

        for i, (title, value, color) in enumerate(cards_data):
            card = self.create_stat_card(stats_frame, title, value, color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            stats_frame.grid_columnconfigure(i, weight=1)

        # Gráficos
        charts_frame = ctk.CTkFrame(container, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, pady=20)

        # Gráfico de campanhas
        self.create_campaigns_chart(charts_frame)

        # Tabela de campanhas recentes
        self.create_recent_campaigns_table(container)

    def create_stat_card(self, parent, title, value, color):
        """Cria um card de estatística"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=120)
        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Helvetica", 14),
            text_color=COLORS['text']
        )
        title_label.pack(pady=(20, 5))

        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=("Helvetica", 32, "bold"),
            text_color=COLORS['text']
        )
        value_label.pack()

        return card

    def get_dashboard_stats(self):
        """Busca estatísticas para o dashboard"""
        stats = {}

        # Total de campanhas
        result = self.db.execute_query("SELECT COUNT(*) FROM Campanha_Dados")
        if result:
            stats['campanhas'] = result[1][0][0] if result[1] else 0

        # Total de anunciantes
        result = self.db.execute_query("SELECT COUNT(*) FROM Anunciante_Dados")
        if result:
            stats['anunciantes'] = result[1][0][0] if result[1] else 0

        # Receita total
        result = self.db.execute_query("SELECT SUM(Precos_dinam) FROM Pagamentos")
        if result and result[1] and result[1][0][0]:
            stats['receita'] = float(result[1][0][0])
        else:
            stats['receita'] = 0

        # Espaços disponíveis
        result = self.db.execute_query(
            "SELECT COUNT(*) FROM Espaco_Dados WHERE Disponibilidade = 'Disponível'"
        )
        if result:
            stats['espacos'] = result[1][0][0] if result[1] else 0

        return stats

    def create_campaigns_chart(self, parent):
        """Cria gráfico de campanhas"""
        chart_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark'], corner_radius=10)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = ctk.CTkLabel(
            chart_frame,
            text="📊 Campanhas por Anunciante (Top 5)",
            font=("Helvetica", 16, "bold"),
            text_color=COLORS['text']
        )
        title.pack(pady=10)

        # Buscar dados
        query = """
        SELECT a.Nome_razao_soc, COUNT(c.Cod_camp) as total
        FROM Anunciante_Dados a
        LEFT JOIN Campanha_Dados c ON a.Num_id_fiscal = c.Num_id_fiscal
        GROUP BY a.Nome_razao_soc
        ORDER BY total DESC
        FETCH FIRST 5 ROWS ONLY
        """
        result = self.db.execute_query(query)

        if result and result[1]:
            names = [row[0][:20] for row in result[1]]
            values = [row[1] for row in result[1]]

            # Criar gráfico
            fig = Figure(figsize=(6, 4), facecolor=COLORS['dark'])
            ax = fig.add_subplot(111)
            ax.set_facecolor(COLORS['dark'])

            bars = ax.barh(names, values, color=[COLORS['primary'], COLORS['secondary'],
                                                 COLORS['accent'], COLORS['success'],
                                                 COLORS['warning']])

            ax.set_xlabel('Número de Campanhas', color=COLORS['text'])
            ax.tick_params(colors=COLORS['text'])
            ax.spines['bottom'].set_color(COLORS['text_secondary'])
            ax.spines['left'].set_color(COLORS['text_secondary'])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            fig.tight_layout()

            # Adicionar ao frame
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

    def create_recent_campaigns_table(self, parent):
        """Cria tabela de campanhas recentes"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark'], corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = ctk.CTkLabel(
            table_frame,
            text="📋 Campanhas Recentes",
            font=("Helvetica", 16, "bold"),
            text_color=COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        # Criar Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=COLORS['dark'],
                        foreground=COLORS['text'],
                        fieldbackground=COLORS['dark'],
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background=COLORS['primary'],
                        foreground=COLORS['text'],
                        borderwidth=0)
        style.map("Treeview", background=[('selected', COLORS['accent'])])

        columns = ('Código', 'Título', 'Anunciante', 'Orçamento', 'Data Início')
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        # Buscar dados
        query = """
        SELECT c.Cod_camp, c.Titulo, a.Nome_razao_soc, c.Orc_alocado, c.Data_inicio
        FROM Campanha_Dados c
        JOIN Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal
        ORDER BY c.Data_inicio DESC
        FETCH FIRST 10 ROWS ONLY
        """
        result = self.db.execute_query(query)

        if result and result[1]:
            for row in result[1]:
                tree.insert('', 'end', values=(
                    row[0],
                    row[1][:30],
                    row[2][:25],
                    f"{row[3]:,.2f} MT",
                    row[4].strftime('%d/%m/%Y') if row[4] else ''
                ))

        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def show_anunciantes(self):
        """Mostra módulo de Anunciantes"""
        self.clear_content()
        self.page_title.configure(text="Anunciantes")

        # Importar e inicializar módulo
        from crud_anunciantes import AnunciantesCRUD
        AnunciantesCRUD(self.main_content, self.db, self)

    def show_campanhas(self):
        """Mostra módulo de Campanhas"""
        self.clear_content()
        self.page_title.configure(text="Campanhas")

        # Importar e inicializar módulo
        from crud_campanhas import CampanhasCRUD
        CampanhasCRUD(self.main_content, self.db, self)

    def show_espacos(self):
        self.clear_content()
        self.page_title.configure(text="Espaços Publicitários")
        label = ctk.CTkLabel(self.main_content, text="Módulo Espaços - Em desenvolvimento",
                             font=("Helvetica", 20))
        label.pack(expand=True)

    def show_pecas(self):
        self.clear_content()
        self.page_title.configure(text="Peças Criativas")
        label = ctk.CTkLabel(self.main_content, text="Módulo Peças - Em desenvolvimento",
                             font=("Helvetica", 20))
        label.pack(expand=True)

    def show_agencias(self):
        self.clear_content()
        self.page_title.configure(text="Agências")
        label = ctk.CTkLabel(self.main_content, text="Módulo Agências - Em desenvolvimento",
                             font=("Helvetica", 20))
        label.pack(expand=True)

    def show_publico(self):
        self.clear_content()
        self.page_title.configure(text="Público-Alvo")
        label = ctk.CTkLabel(self.main_content, text="Módulo Público-Alvo - Em desenvolvimento",
                             font=("Helvetica", 20))
        label.pack(expand=True)

    def show_pagamentos(self):
        self.clear_content()
        self.page_title.configure(text="Pagamentos")
        label = ctk.CTkLabel(self.main_content, text="Módulo Pagamentos - Em desenvolvimento",
                             font=("Helvetica", 20))
        label.pack(expand=True)

    def show_relatorios(self):
        self.clear_content()
        self.page_title.configure(text="Relatórios")
        label = ctk.CTkLabel(self.main_content, text="Módulo Relatórios - Em desenvolvimento",
                             font=("Helvetica", 20))
        label.pack(expand=True)

    def quit_app(self):
        """Encerra a aplicação"""
        if messagebox.askyesno("Confirmar Saída", "Deseja realmente sair do sistema?"):
            self.db.close()
            self.quit()

    def show_espacos(self):
        """Mostra módulo de Espaços"""
        self.clear_content()
        self.page_title.configure(text="Espaços Publicitários")
        from crud_espacos import EspacosCRUD
        EspacosCRUD(self.main_content, self.db, self)

    def show_pecas(self):
        """Mostra módulo de Peças"""
        self.clear_content()
        self.page_title.configure(text="Peças Criativas")
        from crud_pecas import PecasCRUD
        PecasCRUD(self.main_content, self.db, self)

    def show_pagamentos(self):
        """Mostra módulo de Pagamentos"""
        self.clear_content()
        self.page_title.configure(text="Pagamentos")
        from crud_pagamentos import PagamentosCRUD
        PagamentosCRUD(self.main_content, self.db, self)


# ═════════════════════════════════════════════════════════════════════════════
# INICIALIZAÇÃO DA APLICAÇÃO
# ═════════════════════════════════════════════════════════════════════════════

def start_application():
    """Inicia a aplicação com splash screen"""
    # Criar janela principal (oculta)
    app = MainApplication()
    app.withdraw()

    # Criar splash screen
    splash = SplashScreen(app)

    # Simular carregamento
    steps = [
        (0.2, "Conectando ao banco de dados..."),
        (0.4, "Carregando módulos..."),
        (0.6, "Inicializando interface..."),
        (0.8, "Preparando dashboard..."),
        (1.0, "Concluído!")
    ]

    def load():
        for progress, status in steps:
            time.sleep(0.5)
            splash.after(0, lambda: splash.update_progress(progress, status))

        time.sleep(0.5)
        splash.destroy()
        app.deiconify()

    # Executar carregamento em thread separada
    thread = threading.Thread(target=load, daemon=True)
    thread.start()

    app.mainloop()


if __name__ == "__main__":
    start_application()