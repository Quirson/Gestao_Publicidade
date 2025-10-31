"""
📦 MÓDULO ANUNCIANTES - MESMA INTERFACE DO DASHBOARD
"""

import customtkinter as ctk
from tkinter import messagebox, ttk

# Cores padronizadas do main.py
COLORS = {
    'primary': '#1a237e',
    'primary_light': '#534bae',
    'primary_dark': '#000051',
    'secondary': '#d32f2f',
    'secondary_light': '#ff6659',
    'secondary_dark': '#9a0007',
    'accent': '#2979ff',
    'success': '#00c853',
    'warning': '#ffab00',
    'danger': '#ff1744',
    'info': '#00b8d4',
    'dark_bg': '#0d1117',
    'dark_surface': '#161b22',
    'dark_card': '#21262d',
    'dark_border': '#30363d',
    'text_primary': '#f0f6fc',
    'text_secondary': '#8b949e',
    'text_disabled': '#484f58'
}

class AnunciantesCRUD:
    def __init__(self, parent, db, main_app):
        self.parent = parent
        self.db = db
        self.main_app = main_app

        self.create_interface()
        self.load_data()

    def create_interface(self):
        """Cria interface IDÊNTICA ao Dashboard"""
        self.clear_content()

        # Container principal - MESMO LAYOUT DO DASHBOARD
        container = ctk.CTkFrame(self.parent, fg_color=COLORS['dark_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título - MESMO ESTILO DO DASHBOARD
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 25))

        ctk.CTkLabel(
            title_frame,
            text="👥 Gestão de Anunciantes",
            font=("Arial", 22, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Barra de ferramentas - MESMO ESTILO
        self.create_toolbar(container)

        # Tabela - MESMO LAYOUT E DIMENSÕES DO DASHBOARD
        self.create_anunciantes_table(container)

    def create_toolbar(self, parent):
        """Barra de ferramentas igual ao Dashboard"""
        toolbar = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'],
                              corner_radius=10, height=70)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(expand=True, padx=20, pady=12)

        buttons = [
            ("➕ Novo Anunciante", self.novo_anunciante, COLORS['success']),
            ("✏️ Editar", self.editar_anunciante, COLORS['primary']),
            ("🗑️ Excluir", self.excluir_anunciante, COLORS['danger']),
            ("🔄 Atualizar", self.load_data, COLORS['accent']),
        ]

        for text, command, color in buttons:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                font=("Arial", 12, "bold"),
                fg_color=color,
                hover_color=self.darken_color(color),
                width=140,
                height=38,
                corner_radius=8
            )
            btn.pack(side="left", padx=8)

    def create_anunciantes_table(self, parent):
        """Tabela COM MESMO LAYOUT E DIMENSÕES do Dashboard"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12)
        table_frame.pack(fill="both", expand=True, pady=10)

        # Cabeçalho - MESMO ESTILO
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame,
            text="📋 Lista de Anunciantes",
            font=("Arial", 18, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Container da tabela - MESMAS DIMENSÕES
        table_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Treeview - MESMO ESTILO EXATO
        self.create_treeview(table_container)

    def create_treeview(self, parent):
        """Cria treeview IDÊNTICO ao do Dashboard"""
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

        # COLUNAS COM MESMAS LARGURAS DO DASHBOARD
        columns = ('ID', 'Nome/Razão Social', 'Categoria', 'Porte', 'Limite Crédito', 'Classificação')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)  # MESMA ALTURA

        # MESMAS LARGURAS DE COLUNA
        widths = [80, 250, 150, 100, 120, 150]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # SCROLLBARS - MESMO POSICIONAMENTO
        v_scroll = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        h_scroll = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # LAYOUT IDÊNTICO - MESMO grid()
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Bind duplo clique
        self.tree.bind('<Double-1>', lambda e: self.editar_anunciante())

    def load_data(self):
        """Carrega dados - MESMA LÓGICA DO DASHBOARD"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT Num_id_fiscal, Nome_razao_soc, Cat_negocio, Porte, Lim_cred_aprov, Classif_conf 
        FROM Anunciante_Dados 
        ORDER BY Nome_razao_soc
        """
        result = self.db.execute_query(query)

        if result and result[1]:
            for row in result[1]:
                # FORMATAÇÃO CONSISTENTE
                self.tree.insert('', 'end', values=(
                    row[0],
                    row[1],
                    row[2] if row[2] else "Não informado",
                    row[3] if row[3] else "Não informado",
                    f"MT {row[4]:,.2f}" if row[4] else "MT 0.00",
                    row[5] if row[5] else "Não classificado"
                ))
        else:
            messagebox.showinfo("Info", "Nenhum anunciante encontrado.")

    def clear_content(self):
        """Limpa conteúdo - MESMA FUNÇÃO DO MAIN"""
        for widget in self.parent.winfo_children():
            widget.destroy()

    def novo_anunciante(self):
        """Novo anunciante"""
        self.open_form(mode='create')

    def editar_anunciante(self):
        """Editar anunciante"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um anunciante para editar.")
            return

        item = self.tree.item(selected[0])
        anunciante_id = item['values'][0]
        self.open_form(mode='edit', anunciante_id=anunciante_id)

    def open_form(self, mode='create', anunciante_id=None):
        """Abre formulário para criar/editar anunciante"""
        form_window = ctk.CTkToplevel(self.parent)
        form_window.title("Novo Anunciante" if mode == 'create' else "Editar Anunciante")
        form_window.geometry("600x500")

        # Centralizar
        form_window.update_idletasks()
        x = (form_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (form_window.winfo_screenheight() // 2) - (500 // 2)
        form_window.geometry(f"600x500+{x}+{y}")

        form_window.transient(self.parent)
        form_window.grab_set()

        # Container - MESMO ESTILO
        container = ctk.CTkFrame(form_window, fg_color=COLORS['dark_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            container,
            text="📝 Novo Anunciante" if mode == 'create' else "✏️ Editar Anunciante",
            font=("Arial", 18, "bold"),
            text_color=COLORS['text_primary']
        )
        title.pack(pady=(0, 20))

        # Formulário será implementado aqui...
        # Por enquanto, mostrar mensagem
        info_frame = ctk.CTkFrame(container, fg_color=COLORS['dark_card'], corner_radius=10)
        info_frame.pack(fill="both", expand=True, pady=10)

        ctk.CTkLabel(
            info_frame,
            text="Formulário de anunciante em desenvolvimento...",
            font=("Arial", 14),
            text_color=COLORS['text_secondary']
        ).pack(expand=True)

        # Botões - MESMO ESTILO
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)

        ctk.CTkButton(
            btn_frame,
            text="Fechar",
            command=form_window.destroy,
            font=("Arial", 12),
            fg_color=COLORS['secondary'],
            width=120,
            height=35
        ).pack()

    def excluir_anunciante(self):
        """Excluir anunciante"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um anunciante para excluir.")
            return

        item = self.tree.item(selected[0])
        anunciante_id = item['values'][0]
        anunciante_nome = item['values'][1]

        # Verificar se tem campanhas associadas
        query_check = "SELECT COUNT(*) FROM Campanha_Dados WHERE Num_id_fiscal = :id"
        result = self.db.execute_query(query_check, {'id': anunciante_id})

        if result and result[1] and result[1][0][0] > 0:
            messagebox.showerror(
                "Não é possível excluir",
                f"Este anunciante possui {result[1][0][0]} campanha(s) associada(s).\n"
                "Remova as campanhas antes de excluir o anunciante."
            )
            return

        if messagebox.askyesno("Confirmar Exclusão",
                             f"Tem certeza que deseja excluir o anunciante:\n\n'{anunciante_nome}'?"):
            try:
                query_delete = "DELETE FROM Anunciante_Dados WHERE Num_id_fiscal = :id"
                result = self.db.execute_query(query_delete, {'id': anunciante_id}, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Anunciante excluído com sucesso!")
                    self.load_data()
                else:
                    messagebox.showerror("Erro", "Não foi possível excluir o anunciante.")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    def darken_color(self, color):
        """Escurece cor para efeito hover"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb

def show_anunciantes_module(parent, db, main_app):
    """Função para integrar com main app"""
    AnunciantesCRUD(parent, db, main_app)