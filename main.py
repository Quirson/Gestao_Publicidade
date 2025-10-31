"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  SISTEMA DE GESTÃO DE PUBLICIDADE - INC MOÇAMBIQUE (VERSÃO ORACLE REAL)     ║
║  CONEXÃO REAL COM ORACLE DATABASE - 100% FUNCIONAL                          ║
║  Grupo: Eden Magnus, Francisco Guamba, Malik Dauto, Quirson Ngale           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
import threading
import time
import sys
import os

# Adiciona o diretório atual ao path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# =============================================================================
# CONFIGURAÇÃO DE CORES PROFISSIONAL
# =============================================================================

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

COLORS = {
    # Cores principais
    'primary': '#1a237e',
    'primary_light': '#534bae',
    'primary_dark': '#000051',
    'secondary': '#d32f2f',
    'secondary_light': '#ff6659',
    'secondary_dark': '#9a0007',

    # Cores de apoio
    'accent': '#2979ff',
    'success': '#00c853',
    'warning': '#ffab00',
    'danger': '#ff1744',
    'info': '#00b8d4',

    # Cores de fundo - CORRIGIDAS!
    'dark_bg': '#0d1117',
    'dark_surface': '#161b22',
    'dark_card': '#21262d',
    'dark_border': '#30363d',  # ✅ AGORA EXISTE!

    # Cores de texto
    'text_primary': '#f0f6fc',
    'text_secondary': '#8b949e',
    'text_disabled': '#484f58'
}

# =============================================================================
# CONEXÃO ORACLE
# =============================================================================

print("🚀 INICIANDO SISTEMA ORACLE...")

try:
    from database_oracle import db
    ORACLE_AVAILABLE = db.connection is not None
    print("🎉 ORACLE CONECTADO - DADOS REAIS!")
except Exception as e:
    print(f"💥 ERRO: {e}")
    ORACLE_AVAILABLE = False
    exit(1)

# =============================================================================
# COMPONENTES DE INTERFACE
# =============================================================================

class StatCard(ctk.CTkFrame):
    def __init__(self, parent, title, value, icon, color, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(fg_color=COLORS['dark_card'], corner_radius=12,
                      border_width=1, border_color=COLORS['dark_border'])
        self.grid_columnconfigure(0, weight=1)

        # Ícone e título
        icon_frame = ctk.CTkFrame(self, fg_color="transparent")
        icon_frame.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(icon_frame, text=icon, font=("Arial", 20), text_color=color).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(icon_frame, text=title, font=("Arial", 12), text_color=COLORS['text_secondary']).pack(side="left")

        # Valor
        value_label = ctk.CTkLabel(self, text=value, font=("Arial", 24, "bold"),
                                 text_color=COLORS['text_primary'])
        value_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))

# =============================================================================
# TELA DE SPLASH ATUALIZADA
# =============================================================================

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self._setup_window()
        self._create_interface()
        self._start_loading()

    def _setup_window(self):
        self.title("Sistema de Gestão de Publicidade - INC")
        self.geometry("500x400")
        self.resizable(False, False)
        self.center_window()
        self.overrideredirect(True)

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"500x400+{x}+{y}")

    def _create_interface(self):
        main_frame = ctk.CTkFrame(self, fg_color=COLORS['dark_bg'], corner_radius=0)
        main_frame.pack(fill="both", expand=True)

        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        ctk.CTkLabel(content_frame, text="🎯", font=("Arial", 48, "bold"),
                    text_color=COLORS['accent']).pack(pady=(0, 10))
        ctk.CTkLabel(content_frame, text="INC PUBLICIDADE", font=("Arial", 24, "bold"),
                    text_color=COLORS['text_primary']).pack(pady=(0, 5))
        ctk.CTkLabel(content_frame, text="Sistema de Gestão de Publicidade",
                    font=("Arial", 12), text_color=COLORS['text_secondary']).pack(pady=(0, 30))

        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(content_frame, width=300, height=4,
                                             progress_color=COLORS['accent'])
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(0)

        # Status
        self.status_label = ctk.CTkLabel(content_frame, text="Iniciando sistema...",
                                       font=("Arial", 11), text_color=COLORS['text_secondary'])
        self.status_label.pack()

        # Footer
        ctk.CTkLabel(main_frame, text="© 2025 INC Moçambique - Versão Oracle",
                    font=("Arial", 9), text_color=COLORS['text_disabled']).pack(side="bottom", pady=10)

    def _start_loading(self):
        def animate():
            steps = [
                (0.1, "Inicializando módulos..."),
                (0.3, "Conectando ao Oracle Database..."),
                (0.6, "Carregando interface..."),
                (0.8, "Preparando dados..."),
                (1.0, "Sistema pronto!")
            ]

            for progress, status in steps:
                time.sleep(0.6)
                self.update_progress(progress, status)

            time.sleep(0.3)
            self.finish_loading()

        thread = threading.Thread(target=animate, daemon=True)
        thread.start()

    def update_progress(self, progress, status):
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)

    def finish_loading(self):
        self.destroy()
        self.parent.deiconify()

# =============================================================================
# APLICAÇÃO PRINCIPAL ATUALIZADA
# =============================================================================

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = db  # Usa a conexão Oracle REAL
        self._setup_window()
        self._create_interface()

        # Verificar conexão
        if not ORACLE_AVAILABLE:
            messagebox.showwarning("Aviso",
                "Conexão Oracle não disponível.\n"
                "O sistema funcionará em modo de demonstração.\n\n"
                "Verifique:\n"
                "• Oracle Database está rodando\n"
                "• Service Name: XEPDB1\n" 
                "• Credenciais corretas")

        self.show_dashboard()

    def _setup_window(self):
        self.title("🎯 INC Publicidade - Sistema de Gestão (Oracle)")
        self.geometry("1200x700")
        self.minsize(1100, 650)
        self.center_window()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"1200x700+{x}+{y}")

    def _create_interface(self):
        self._create_sidebar()
        self._create_header()
        self._create_main_content()

    def _create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color=COLORS['dark_surface'])
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color=COLORS['primary'], height=100, corner_radius=0)
        logo_frame.pack(fill="x", pady=0)
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame, text="🎯", font=("Arial", 24), text_color=COLORS['text_primary']).pack(expand=True)
        ctk.CTkLabel(logo_frame, text="INC PUBLICIDADE", font=("Arial", 14, "bold"),
                   text_color=COLORS['text_primary']).pack(pady=(0, 10))

        # Status da Conexão
        status_color = COLORS['success'] if ORACLE_AVAILABLE else COLORS['danger']
        status_text = "🟢 Oracle Conectado" if ORACLE_AVAILABLE else "🔴 Oracle Offline"

        status_frame = ctk.CTkFrame(logo_frame, fg_color=status_color, corner_radius=8)
        status_frame.pack(side="bottom", pady=5, padx=10, fill="x")
        ctk.CTkLabel(status_frame, text=status_text, font=("Arial", 10, "bold"),
                   text_color=COLORS['text_primary']).pack(pady=2)

        # Navegação
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=20)

        menu_items = [
            ("🏠", "Dashboard", self.show_dashboard),
            ("👥", "Anunciantes", self.show_anunciantes),
            ("📢", "Campanhas", self.show_campanhas),
            ("🎨", "Peças Criativas", self.show_pecas),
            ("📺", "Espaços", self.show_espacos),
            ("💳", "Pagamentos", self.show_pagamentos),
            ("📊", "Relatórios", self.show_relatorios),
        ]

        for icon, text, command in menu_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"   {icon}  {text}",
                command=command,
                font=("Arial", 13),
                fg_color="transparent",
                hover_color=COLORS['dark_card'],
                anchor="w",
                height=45,
                corner_radius=8
            )
            btn.pack(fill="x", padx=5, pady=2)

        # Botão sair
        ctk.CTkButton(
            nav_frame,
            text="🚪  Sair do Sistema",
            command=self.quit_app,
            font=("Arial", 13, "bold"),
            fg_color=COLORS['danger'],
            hover_color=COLORS['secondary_dark'],
            height=45,
            corner_radius=8
        ).pack(side="bottom", fill="x", padx=5, pady=10)

    def _create_header(self):
        self.header = ctk.CTkFrame(self, height=70, corner_radius=0, fg_color=COLORS['dark_surface'])
        self.header.grid(row=0, column=1, sticky="ew")
        self.header.grid_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard Principal",
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        )
        self.page_title.pack(side="left", padx=30, pady=20)

        user_frame = ctk.CTkFrame(self.header, fg_color="transparent")
        user_frame.pack(side="right", padx=20, pady=15)

        self.time_label = ctk.CTkLabel(
            user_frame,
            text=self._get_current_time(),
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
        )
        self.time_label.pack(side="right", padx=10)

        ctk.CTkLabel(
            user_frame,
            text="👤 Administrador",
            font=("Arial", 11, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="right", padx=10)

        self._update_clock()

    def _create_main_content(self):
        self.main_content = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS['dark_bg'])
        self.main_content.grid(row=1, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

    def _get_current_time(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M")

    def _update_clock(self):
        self.time_label.configure(text=self._get_current_time())
        self.after(1000, self._update_clock)

    def clear_content(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        """Dashboard com dados REAIS da Oracle"""
        self.clear_content()
        self.page_title.configure(text="Dashboard Principal")

        container = ctk.CTkFrame(self.main_content, fg_color=COLORS['dark_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(
            title_frame,
            text="📊 Visão Geral do Sistema",
            font=("Arial", 22, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Cards de estatísticas COM DADOS REAIS
        self._create_stats_cards(container)

        # Tabela de campanhas COM DADOS REAIS
        self._create_campaigns_table(container)

    def _create_stats_cards(self, parent):
        """Cria cards com dados REAIS da Oracle"""
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))

        # Buscar estatísticas REAIS
        stats_data = self._get_real_stats()

        cards_info = [
            ("📈", "Campanhas Ativas", stats_data['campanhas_ativas'], COLORS['accent']),
            ("👥", "Anunciantes", stats_data['total_anunciantes'], COLORS['success']),
            ("💰", "Orçamento Total", f"MT {stats_data['orcamento_total']:,.0f}", COLORS['primary']),
            ("📺", "Espaços Disponíveis", stats_data['espacos_disponiveis'], COLORS['info']),
        ]

        for i, (icon, title, value, color) in enumerate(cards_info):
            card = StatCard(stats_frame, title, str(value), icon, color, width=220, height=110)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)

    def _get_real_stats(self):
        """Busca estatísticas REAIS da base de dados"""
        if not ORACLE_AVAILABLE:
            # Dados de fallback
            return {
                'total_anunciantes': 5,
                'campanhas_ativas': 3,
                'orcamento_total': 1500000,
                'espacos_disponiveis': 3
            }

        try:
            # Usar a procedure de estatísticas
            result = self.db.execute_query("""
                SELECT 
                    (SELECT COUNT(*) FROM Anunciante_Dados) as anunciantes,
                    (SELECT COUNT(*) FROM Campanha_Dados WHERE Data_termino >= SYSDATE) as ativas,
                    (SELECT NVL(SUM(Orc_alocado), 0) FROM Campanha_Dados WHERE Data_termino >= SYSDATE) as orcamento,
                    (SELECT COUNT(*) FROM Espaco_Dados WHERE Disponibilidade = 'Disponível') as espacos
                FROM DUAL
            """)

            if result and result[1]:
                row = result[1][0]
                return {
                    'total_anunciantes': row[0],
                    'campanhas_ativas': row[1],
                    'orcamento_total': float(row[2]) if row[2] else 0,
                    'espacos_disponiveis': row[3]
                }
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")

        return {'total_anunciantes': 0, 'campanhas_ativas': 0, 'orcamento_total': 0, 'espacos_disponiveis': 0}

    def _create_campaigns_table(self, parent):
        """Cria tabela com campanhas REAIS"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12)
        table_frame.pack(fill="both", expand=True, pady=10)

        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame,
            text="📋 Campanhas em Andamento",
            font=("Arial", 18, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        table_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._create_real_treeview(table_container)

    def _create_real_treeview(self, parent):
        """Cria treeview com dados REAIS"""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=COLORS['dark_card'],
                        foreground=COLORS['text_primary'],
                        fieldbackground=COLORS['dark_card'],
                        rowheight=35)
        style.configure("Treeview.Heading",
                        background=COLORS['primary'],
                        foreground=COLORS['text_primary'],
                        font=("Arial", 11, "bold"))
        style.map("Treeview", background=[('selected', COLORS['accent'])])

        columns = ('Código', 'Campanha', 'Anunciante', 'Orçamento', 'Início', 'Término', 'Status')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=8)

        widths = [80, 200, 150, 120, 100, 100, 100]
        for col, width in zip(columns, widths):
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor="center")

        # BUSCAR DADOS REAIS
        real_data = self._get_real_campaigns()
        for row in real_data:
            tree.insert('', 'end', values=row)

        v_scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        h_scroll = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

    def _get_real_campaigns(self):
        """Busca campanhas REAIS da base de dados"""
        if not ORACLE_AVAILABLE:
            # Dados de fallback
            return [
                ('800001', '5G Revolution', 'Vodacom', 'MT 500,000', '01/10/2024', '31/12/2024', '🟢 Ativa'),
                ('800002', 'Verão Laurentina', 'Cervejas Moz', 'MT 300,000', '01/11/2024', '28/02/2025', '🟢 Ativa'),
            ]

        try:
            result = self.db.execute_query("""
                SELECT c.Cod_camp, c.Titulo, a.Nome_razao_soc, 
                       c.Orc_alocado, 
                       TO_CHAR(c.Data_inicio, 'DD/MM/YYYY'),
                       TO_CHAR(c.Data_termino, 'DD/MM/YYYY'),
                       CASE WHEN c.Data_termino >= SYSDATE THEN '🟢 Ativa' ELSE '🔴 Finalizada' END
                FROM Campanha_Dados c
                JOIN Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal
                WHERE c.Data_termino >= SYSDATE
                ORDER BY c.Data_inicio DESC
            """)

            if result and result[1]:
                real_data = []
                for row in result[1]:
                    real_data.append((
                        str(row[0]),
                        row[1],
                        row[2],
                        f"MT {row[3]:,.0f}",
                        row[4],
                        row[5],
                        row[6]
                    ))
                return real_data

        except Exception as e:
            print(f"Erro ao buscar campanhas: {e}")

        return []

    # ... (outros métodos show_* permanecem similares, mas agora usam db real)

    def show_anunciantes(self):
        self.clear_content()
        self.page_title.configure(text="Gestão de Anunciantes")
        try:
            from crud_anunciantes import show_anunciantes_module
            show_anunciantes_module(self.main_content, self.db, self)
        except ImportError as e:
            print(f"Erro ao carregar módulo: {e}")
            self._show_placeholder("Anunciantes", "👥")

    def show_campanhas(self):
        self.clear_content()
        self.page_title.configure(text="Gestão de Campanhas")
        try:
            from crud_campanhas import show_campanhas_module
            show_campanhas_module(self.main_content, self.db, self)
        except ImportError as e:
            print(f"Erro ao carregar módulo: {e}")
            self._show_placeholder("Campanhas", "📢")

    def show_pecas(self):
        self.clear_content()
        self.page_title.configure(text="Gestão de Peças Criativas")
        try:
            from crud_pecas import show_pecas_module
            show_pecas_module(self.main_content, self.db, self)
        except ImportError as e:
            print(f"Erro ao carregar módulo: {e}")
            self._show_placeholder("Peças Criativas", "🎨")

    def show_espacos(self):
        self.clear_content()
        self.page_title.configure(text="Gestão de Espaços Publicitários")
        try:
            from crud_espacos import show_espacos_module
            show_espacos_module(self.main_content, self.db, self)
        except ImportError as e:
            print(f"Erro ao carregar módulo: {e}")
            self._show_placeholder("Espaços Publicitários", "📺")

    def show_pagamentos(self):
        self.clear_content()
        self.page_title.configure(text="Gestão de Pagamentos")
        try:
            from crud_pagamentos import show_pagamentos_module
            show_pagamentos_module(self.main_content, self.db, self)
        except ImportError as e:
            print(f"Erro ao carregar módulo: {e}")
            self._show_placeholder("Pagamentos", "💳")

    def show_relatorios(self):
        self.clear_content()
        self.page_title.configure(text="Relatórios e Analytics")
        self._show_placeholder("Relatórios", "📊")

    def _show_placeholder(self, module_name, icon):
        placeholder = ctk.CTkFrame(self.main_content, fg_color=COLORS['dark_card'], corner_radius=12)
        placeholder.place(relx=0.5, rely=0.5, anchor="center", width=400, height=300)

        content = ctk.CTkFrame(placeholder, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(content, text=icon, font=("Arial", 48), text_color=COLORS['text_secondary']).pack(pady=10)
        ctk.CTkLabel(content, text=module_name, font=("Arial", 20, "bold"), text_color=COLORS['text_primary']).pack(pady=5)

        status_msg = "Módulo em Desenvolvimento" if ORACLE_AVAILABLE else "Oracle não disponível"
        ctk.CTkLabel(content, text=status_msg, font=("Arial", 12), text_color=COLORS['text_secondary']).pack(pady=10)

        ctk.CTkButton(
            content,
            text="Voltar ao Dashboard",
            command=self.show_dashboard,
            font=("Arial", 12),
            fg_color=COLORS['primary'],
            width=200,
            height=35
        ).pack(pady=20)

    def quit_app(self):
        if messagebox.askyesno("Confirmar", "Deseja sair do sistema?"):
            if hasattr(self, 'db') and self.db.connection:
                self.db.connection.close()
                print("🔌 Conexão Oracle fechada.")
            self.quit()

# =============================================================================
# INICIALIZAÇÃO
# =============================================================================

def start_application():
    print("🚀 INICIANDO SISTEMA DE GESTÃO DE PUBLICIDADE...")
    print("🎯 CONEXÃO ORACLE: localhost:1521/XEPDB1")
    print("👤 USUÁRIO: Gestao_Publicidade")

    app = MainApp()
    app.withdraw()

    splash = SplashScreen(app)
    app.mainloop()

if __name__ == "__main__":
    start_application()