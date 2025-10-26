"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD PEÇAS CRIATIVAS - COM ESPECIALIZAÇÃO                           ║
║  Sistema de Gestão de Publicidade e Marketing                               ║
║  Suporta: Peças Visuais, Audiovisuais e Interativas                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime


class PecasCRUD:
    def __init__(self, parent, db, main_app):
        self.parent = parent
        self.db = db
        self.main_app = main_app

        # Cores
        self.COLORS = {
            'primary': '#1f538d',
            'secondary': '#c41e3a',
            'accent': '#2d5aa6',
            'success': '#28a745',
            'danger': '#dc3545',
            'dark': '#1a1a1a',
            'text': '#ffffff',
            'text_secondary': '#b0b0b0'
        }

        self.create_interface()
        self.load_data()

    def create_interface(self):
        """Cria a interface completa do CRUD"""
        self.main_container = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_toolbar()
        self.create_search_area()
        self.create_table()

    def create_toolbar(self):
        """Cria a barra de ferramentas com os botões de ação"""
        toolbar = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                               corner_radius=10, height=80)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(pady=15, padx=20)

        buttons = [
            ("➕ Nova Peça", self.open_create_form, self.COLORS['success']),
            ("✏️ Editar", self.open_edit_form, self.COLORS['primary']),
            ("🗑️ Excluir", self.delete_record, self.COLORS['danger']),
            ("🔄 Atualizar", self.load_data, self.COLORS['accent']),
            ("📊 Detalhes", self.show_details, self.COLORS['secondary'])
        ]

        for text, command, color in buttons:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                font=("Helvetica", 13, "bold"),
                fg_color=color,
                hover_color=self.darken_color(color),
                width=150,
                height=40,
                corner_radius=8
            )
            btn.pack(side="left", padx=5)

    def create_search_area(self):
        """Cria a área de busca e filtros"""
        search_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                                    corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar Peças Criativas",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Campo de busca por texto
        search_label = ctk.CTkLabel(filter_frame, text="Buscar:", font=("Helvetica", 12))
        search_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Título ou criador...",
            width=300,
            height=35
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.search_var.trace('w', lambda *args: self.filter_data())

        # Filtro por tipo
        tipo_label = ctk.CTkLabel(filter_frame, text="Tipo:", font=("Helvetica", 12))
        tipo_label.grid(row=0, column=2, padx=(20, 10), pady=5, sticky="w")

        self.tipo_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todas", "Visual", "Audiovisual", "Interativa"],
            width=180,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.tipo_filter.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.tipo_filter.set("Todas")

        # Filtro por status
        status_label = ctk.CTkLabel(filter_frame, text="Status:", font=("Helvetica", 12))
        status_label.grid(row=0, column=4, padx=(20, 10), pady=5, sticky="w")

        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todos", "Aprovado", "Em Revisão", "Rejeitado", "Pendente"],
            width=150,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.status_filter.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.status_filter.set("Todos")

        # Botão Limpar
        clear_btn = ctk.CTkButton(
            filter_frame,
            text="🗑️ Limpar",
            command=self.clear_filters,
            width=100,
            height=35,
            fg_color=self.COLORS['secondary']
        )
        clear_btn.grid(row=0, column=6, padx=(20, 0), pady=5)

    def create_table(self):
        """Cria a tabela para exibir os dados"""
        table_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                                   corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            table_frame,
            text="🎨 Lista de Peças Criativas",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Estilo da Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=self.COLORS['dark'],
                        foreground=self.COLORS['text'],
                        fieldbackground=self.COLORS['dark'],
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background=self.COLORS['primary'],
                        foreground=self.COLORS['text'],
                        font=("Helvetica", 11, "bold"))
        style.map("Treeview",
                  background=[('selected', self.COLORS['accent'])])

        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        columns = ('ID', 'Título', 'Tipo', 'Anunciante', 'Criador',
                   'Data Criação', 'Status', 'Classificação')
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        widths = [80, 200, 120, 180, 150, 110, 110, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree.bind('<Double-1>', lambda e: self.open_edit_form())

    def load_data(self):
        """Carrega os dados do banco de dados para a tabela"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
                SELECT p.Id_unicoPeca, \
                       p.Titulo, \
                       CASE \
                           WHEN v.Id_unicoPeca IS NOT NULL THEN 'Visual' \
                           WHEN a.Id_unicoPeca IS NOT NULL THEN 'Audiovisual' \
                           WHEN i.Id_unicoPeca IS NOT NULL THEN 'Interativa' \
                           ELSE 'Genérica' \
                           END as Tipo, \
                       an.Nome_razao_soc, \
                       p.Criador, \
                       p.Data_criacao, \
                       p.Status_aprov, \
                       p.Classif_conteudo
                FROM Pecas_Criativas p
                         JOIN Anunciante_Dados an ON p.Num_id_fiscal = an.Num_id_fiscal
                         LEFT JOIN Pecas_Visuais v ON p.Id_unicoPeca = v.Id_unicoPeca
                         LEFT JOIN Pecas_Audiovisuais a ON p.Id_unicoPeca = a.Id_unicoPeca
                         LEFT JOIN Pecas_Interativas i ON p.Id_unicoPeca = i.Id_unicoPeca
                ORDER BY p.Data_criacao DESC \
                """

        result = self.db.execute_query(query)

        if result and result[1]:
            self.all_data = result[1]
            for row in result[1]:
                data_formatada = row[5].strftime('%d/%m/%Y') if row[5] else ''
                classif = f"{row[7]} anos"

                tag = str(row[6]).lower().replace(' ', '_')
                self.tree.insert('', 'end', values=(
                    row[0], row[1][:30], row[2], row[3][:25], row[4][:20],
                    data_formatada, row[6], classif
                ), tags=(tag,))

            self.tree.tag_configure('aprovado', foreground='#28a745')
            self.tree.tag_configure('em_revisão', foreground='#ffc107')
            self.tree.tag_configure('rejeitado', foreground='#dc3545')
            self.tree.tag_configure('pendente', foreground='#17a2b8')

    def filter_data(self):
        """Filtra os dados exibidos na tabela com base nos campos de busca"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_text = self.search_var.get().lower()
        tipo_filter = self.tipo_filter.get()
        status_filter = self.status_filter.get()

        if hasattr(self, 'all_data'):
            for row in self.all_data:
                titulo = str(row[1]).lower()
                tipo = str(row[2])
                criador = str(row[4]).lower()
                status = str(row[6])

                match_search = (search_text in titulo or search_text in criador)
                match_tipo = (tipo_filter == "Todas" or tipo_filter == tipo)
                match_status = (status_filter == "Todos" or status_filter == status)

                if match_search and match_tipo and match_status:
                    data_formatada = row[5].strftime('%d/%m/%Y') if row[5] else ''
                    classif = f"{row[7]} anos"
                    tag = status.lower().replace(' ', '_')
                    self.tree.insert('', 'end', values=(
                        row[0], row[1][:30], tipo, row[3][:25], row[4][:20],
                        data_formatada, status, classif
                    ), tags=(tag,))

    def clear_filters(self):
        """Limpa todos os filtros e recarrega os dados"""
        self.search_var.set("")
        self.tipo_filter.set("Todas")
        self.status_filter.set("Todos")
        self.load_data()

    def open_create_form(self):
        """Abre o formulário para criar um novo registro"""
        self.open_form(mode='create')

    def open_edit_form(self):
        """Abre o formulário para editar um registro selecionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma peça para editar.")
            return

        item = self.tree.item(selected[0])
        id_peca = item['values'][0]
        self.open_form(mode='edit', id_peca=id_peca)

    def open_form(self, mode='create', id_peca=None):
        """Abre a janela do formulário (criação ou edição)"""
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Nova Peça Criativa" if mode == 'create' else "Editar Peça")
        self.form_window.geometry("1000x800")

        self.form_window.update_idletasks()
        x = (self.form_window.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.form_window.winfo_screenheight() // 2) - (800 // 2)
        self.form_window.geometry(f"1000x800+{x}+{y}")

        self.form_window.transient(self.parent)
        self.form_window.grab_set()

        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color="#2b2b2b")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        title_text = "🎨 Nova Peça Criativa" if mode == 'create' else "✏️ Editar Peça"
        title = ctk.CTkLabel(
            form_container,
            text=title_text,
            font=("Helvetica", 20, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=(0, 20))

        form_frame = ctk.CTkFrame(form_container, fg_color=self.COLORS['dark'],
                                  corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        fields = {}
        row = 0

        # --- CAMPOS GERAIS ---
        section_label = ctk.CTkLabel(form_frame, text="📋 Informações Gerais",
                                     font=("Helvetica", 16, "bold"), text_color=self.COLORS['secondary'])
        section_label.grid(row=row, column=0, columnspan=2, pady=(10, 15), sticky="w", padx=20)
        row += 1

        if mode == 'edit':
            self.create_field(form_frame, "ID Peça:", row, fields, 'id_peca', readonly=True, width=150)
            row += 1

        label = ctk.CTkLabel(form_frame, text="Anunciante:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
        fields['anunciante'] = ctk.CTkComboBox(form_frame, values=self.get_anunciantes_list(), width=400, height=35)
        fields['anunciante'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        self.create_field(form_frame, "Título:*", row, fields, 'titulo', width=500)
        row += 1

        label = ctk.CTkLabel(form_frame, text="Descrição:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="nw")
        fields['descricao'] = ctk.CTkTextbox(form_frame, width=500, height=80)
        fields['descricao'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        self.create_field(form_frame, "Criador:*", row, fields, 'criador', width=300)
        row += 1

        label = ctk.CTkLabel(form_frame, text="Data Criação:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
        fields['data_criacao'] = DateEntry(form_frame, width=25, background='darkblue',
                                           foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        fields['data_criacao'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        label = ctk.CTkLabel(form_frame, text="Status:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
        fields['status'] = ctk.CTkComboBox(form_frame, values=["Aprovado", "Em Revisão", "Rejeitado", "Pendente"],
                                           width=200, height=35)
        fields['status'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        self.create_field(form_frame, "Classificação (anos):*", row, fields, 'classificacao', width=100)
        row += 1

        label = ctk.CTkLabel(form_frame, text="Direitos Autorais:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="nw")
        fields['direitos'] = ctk.CTkTextbox(form_frame, width=500, height=60)
        fields['direitos'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # --- TIPO E ESPECIALIZAÇÃO ---
        section_label2 = ctk.CTkLabel(form_frame, text="🎯 Tipo e Especialização",
                                      font=("Helvetica", 16, "bold"), text_color=self.COLORS['secondary'])
        section_label2.grid(row=row, column=0, columnspan=2, pady=(20, 15), sticky="w", padx=20)
        row += 1

        label = ctk.CTkLabel(form_frame, text="Tipo de Peça:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")
        fields['tipo_peca'] = ctk.CTkComboBox(form_frame, values=["Visual", "Audiovisual", "Interativa"],
                                              width=200, height=35,
                                              command=lambda choice: self.show_specialization_fields(choice, form_frame,
                                                                                                     fields, row + 1))
        fields['tipo_peca'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        fields['spec_frame'] = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields['spec_frame'].grid(row=row, column=0, columnspan=2, sticky="ew", padx=20, pady=10)
        row += 1

        # --- BOTÕES ---
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(
            btn_frame, text="💾 Salvar",
            command=lambda: self.save_record(mode, fields, id_peca),
            font=("Helvetica", 14, "bold"), fg_color=self.COLORS['success'],
            width=150, height=40)
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            btn_frame, text="❌ Cancelar",
            command=self.form_window.destroy,
            font=("Helvetica", 14, "bold"), fg_color=self.COLORS['danger'],
            width=150, height=40)
        cancel_btn.pack(side="left", padx=10)

        if mode == 'edit' and id_peca:
            self.load_form_data(fields, id_peca)

        self.form_fields = fields

    def show_specialization_fields(self, tipo, parent, fields, start_row):
        """Mostra campos específicos baseado no tipo"""
        # Limpar campos anteriores
        if 'spec_frame' in fields:
            for widget in fields['spec_frame'].winfo_children():
                widget.destroy()

        spec_frame = fields['spec_frame']

        if tipo == "Visual":
            # Campos para Peças Visuais
            self.create_field_in_frame(spec_frame, "Dimensões (Visual):*", 0, fields,
                                       'dim_visual', width=200)
            self.create_field_in_frame(spec_frame, "Resolução (Visual):*", 1, fields,
                                       'resol_visual', width=200)
            self.create_field_in_frame(spec_frame, "Formato Arquivo:*", 2, fields,
                                       'formato', width=150)
            self.create_field_in_frame(spec_frame, "Paleta de Cores:", 3, fields,
                                       'paleta', width=400)
            self.create_field_in_frame(spec_frame, "Elementos Gráficos:", 4, fields,
                                       'elementos', width=400)
            self.create_field_in_frame(spec_frame, "Compat. Dispositivos:", 5, fields,
                                       'compat_disp', width=400)

        elif tipo == "Audiovisual":
            # Campos para Peças Audiovisuais
            self.create_field_in_frame(spec_frame, "Duração:*", 0, fields,
                                       'duracao', width=150)
            self.create_field_in_frame(spec_frame, "Qualidade Vídeo:*", 1, fields,
                                       'qualidade', width=200)
            self.create_field_in_frame(spec_frame, "Resolução Vídeo:*", 2, fields,
                                       'resol_video', width=200)
            self.create_field_in_frame(spec_frame, "Legendas Disponíveis:", 3, fields,
                                       'legendas', width=400)
            self.create_field_in_frame(spec_frame, "Requisitos Técnicos:", 4, fields,
                                       'req_tecnicos', width=400)

        elif tipo == "Interativa":
            # Campos para Peças Interativas
            self.create_field_in_frame(spec_frame, "Tecnologias Utilizadas:*", 0, fields,
                                       'tecnologias', width=400)

            label = ctk.CTkLabel(spec_frame, text="Nível Interação:*",
                                 font=("Helvetica", 12, "bold"))
            label.grid(row=1, column=0, padx=20, pady=10, sticky="w")

            fields['nivel_inter'] = ctk.CTkComboBox(
                spec_frame,
                values=["Baixo", "Médio", "Alto", "Muito Alto"],
                width=200,
                height=35
            )
            fields['nivel_inter'].grid(row=1, column=1, padx=20, pady=10, sticky="w")

            self.create_field_in_frame(spec_frame, "Requisitos Dispositivo:", 2, fields,
                                       'req_dispositivo', width=400)
            self.create_field_in_frame(spec_frame, "Métricas Engajamento:*", 3, fields,
                                       'metricas', width=150)

            label = ctk.CTkLabel(spec_frame, text="Dados Coletados:",
                                 font=("Helvetica", 12, "bold"))
            label.grid(row=4, column=0, padx=20, pady=10, sticky="nw")

            fields['dados_colect'] = ctk.CTkTextbox(spec_frame, width=400, height=60)
            fields['dados_colect'].grid(row=4, column=1, padx=20, pady=10, sticky="w")

    def create_field(self, parent, label_text, row, fields, field_name,
                     width=300, readonly=False):
        """Cria um campo de entrada (label + entry) no formulário principal"""
        label = ctk.CTkLabel(parent, text=label_text, font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        if readonly:
            entry.configure(state="disabled")

        fields[field_name] = entry

    def create_field_in_frame(self, parent, label_text, row, fields, field_name, width=300):
        """Cria um campo de entrada (label + entry) dentro do frame de especialização"""
        label = ctk.CTkLabel(parent, text=label_text, font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        fields[field_name] = entry

    def get_anunciantes_list(self):
        """Retorna uma lista de anunciantes formatada para o ComboBox"""
        query = "SELECT Num_id_fiscal, Nome_razao_soc FROM Anunciante_Dados ORDER BY Nome_razao_soc"
        result = self.db.execute_query(query)

        anunciantes = []
        if result and result[1]:
            for row in result[1]:
                anunciantes.append(f"{row[0]} - {row[1]}")

        return anunciantes if anunciantes else ["Nenhum anunciante cadastrado"]

    def load_form_data(self, fields, id_peca):
        """Carrega os dados de uma peça existente no formulário para edição"""
        # Buscar dados gerais da peça
        query = """
                SELECT p.Id_unicoPeca, \
                       p.Num_id_fiscal, \
                       p.Titulo, \
                       p.Descricao, \
                       p.Criador,
                       p.Data_criacao, \
                       p.Status_aprov, \
                       p.Direitos_autorais, \
                       p.Classif_conteudo,
                       CASE
                           WHEN v.Id_unicoPeca IS NOT NULL THEN 'Visual'
                           WHEN a.Id_unicoPeca IS NOT NULL THEN 'Audiovisual'
                           WHEN i.Id_unicoPeca IS NOT NULL THEN 'Interativa'
                           ELSE NULL
                           END as Tipo
                FROM Pecas_Criativas p
                         LEFT JOIN Pecas_Visuais v ON p.Id_unicoPeca = v.Id_unicoPeca
                         LEFT JOIN Pecas_Audiovisuais a ON p.Id_unicoPeca = a.Id_unicoPeca
                         LEFT JOIN Pecas_Interativas i ON p.Id_unicoPeca = i.Id_unicoPeca
                WHERE p.Id_unicoPeca = :id \
                """
        result = self.db.execute_query(query, {'id': id_peca})

        if result and result[1]:
            data = result[1][0]

            fields['id_peca'].configure(state="normal")
            fields['id_peca'].insert(0, str(data[0]))
            fields['id_peca'].configure(state="disabled")

            anun_id = data[1]
            query_anun = f"SELECT Nome_razao_soc FROM Anunciante_Dados WHERE Num_id_fiscal = {anun_id}"
            result_anun = self.db.execute_query(query_anun)
            if result_anun and result_anun[1]:
                anun_text = f"{anun_id} - {result_anun[1][0][0]}"
                fields['anunciante'].set(anun_text)

            fields['titulo'].insert(0, data[2])
            fields['descricao'].insert("1.0", data[3])
            fields['criador'].insert(0, data[4])

            if data[5]:
                fields['data_criacao'].set_date(data[5])

            fields['status'].set(data[6])
            fields['direitos'].insert("1.0", data[7])
            fields['classificacao'].insert(0, str(data[8]))

            tipo = data[9]
            if tipo:
                fields['tipo_peca'].set(tipo)
                self.show_specialization_fields(tipo, None, fields, 0)

                # Carregar dados de especialização
                if tipo == "Visual":
                    query_visual = "SELECT Dim_pvisuais, Resol_pvisuais, Form_arquivo, Pal_cores, El_graficos, Compat_disp_exib FROM Pecas_Visuais WHERE Id_unicoPeca = :id"
                    result_spec = self.db.execute_query(query_visual, {'id': id_peca})
                    if result_spec and result_spec[1]:
                        spec_data = result_spec[1][0]
                        fields['dim_visual'].insert(0, spec_data[0])
                        fields['resol_visual'].insert(0, spec_data[1])
                        fields['formato'].insert(0, spec_data[2])
                        if spec_data[3]: fields['paleta'].insert(0, spec_data[3])
                        if spec_data[4]: fields['elementos'].insert(0, spec_data[4])
                        if spec_data[5]: fields['compat_disp'].insert(0, spec_data[5])

                elif tipo == "Audiovisual":
                    query_audio = "SELECT Duracao, Qualidad_video, Resol_video, Legendas_disp, Req_tecnicos FROM Pecas_Audiovisuais WHERE Id_unicoPeca = :id"
                    result_spec = self.db.execute_query(query_audio, {'id': id_peca})
                    if result_spec and result_spec[1]:
                        spec_data = result_spec[1][0]
                        fields['duracao'].insert(0, spec_data[0])
                        fields['qualidade'].insert(0, spec_data[1])
                        fields['resol_video'].insert(0, spec_data[2])
                        if spec_data[3]: fields['legendas'].insert(0, spec_data[3])
                        if spec_data[4]: fields['req_tecnicos'].insert(0, spec_data[4])

                elif tipo == "Interativa":
                    query_inter = "SELECT Tec_util, Niv_interacao, Req_dispositivo, Metri_engaj, Dados_colect FROM Pecas_Interativas WHERE Id_unicoPeca = :id"
                    result_spec = self.db.execute_query(query_inter, {'id': id_peca})
                    if result_spec and result_spec[1]:
                        spec_data = result_spec[1][0]
                        fields['tecnologias'].insert(0, spec_data[0])
                        fields['nivel_inter'].set(spec_data[1])
                        if spec_data[2]: fields['req_dispositivo'].insert(0, spec_data[2])
                        fields['metricas'].insert(0, str(spec_data[3]))
                        if spec_data[4]: fields['dados_colect'].insert("1.0", spec_data[4])

    def save_record(self, mode, fields, id_peca=None):
        """Salva um registro novo (create) ou atualiza um existente (edit)"""
        try:
            # Validar campos gerais
            anunciante = fields['anunciante'].get()
            if not anunciante or anunciante == "Nenhum anunciante cadastrado":
                messagebox.showerror("Erro de Validação", "Selecione um anunciante.")
                return
            num_id_fiscal = int(anunciante.split(' - ')[0])

            titulo = fields['titulo'].get().strip()
            descricao = fields['descricao'].get("1.0", "end-1c").strip()
            criador = fields['criador'].get().strip()
            status = fields['status'].get()
            direitos = fields['direitos'].get("1.0", "end-1c").strip()
            classificacao = fields['classificacao'].get().strip()
            tipo_peca = fields['tipo_peca'].get()

            if not all([titulo, descricao, criador, status, direitos, classificacao, tipo_peca]):
                messagebox.showerror("Erro de Validação", "Preencha todos os campos obrigatórios (*).")
                return

            try:
                classificacao = int(classificacao)
                if not (0 <= classificacao <= 18): raise ValueError
            except (ValueError, TypeError):
                messagebox.showerror("Erro de Validação",
                                     "A Classificação de conteúdo deve ser um número entre 0 e 18.")
                return

            data_criacao = fields['data_criacao'].get_date()
            data_criacao_str = data_criacao.strftime('%d/%m/%Y')

            # Validar campos de especialização
            if tipo_peca == "Visual":
                if not all([fields['dim_visual'].get(), fields['resol_visual'].get(), fields['formato'].get()]):
                    messagebox.showerror("Erro", "Preencha os campos obrigatórios de Peça Visual.")
                    return
            elif tipo_peca == "Audiovisual":
                if not all([fields['duracao'].get(), fields['qualidade'].get(), fields['resol_video'].get()]):
                    messagebox.showerror("Erro", "Preencha os campos obrigatórios de Peça Audiovisual.")
                    return
            elif tipo_peca == "Interativa":
                if not all([fields['tecnologias'].get(), fields['nivel_inter'].get(), fields['metricas'].get()]):
                    messagebox.showerror("Erro", "Preencha os campos obrigatórios de Peça Interativa.")
                    return
                try:
                    metricas = float(fields['metricas'].get())
                    if metricas < 0: raise ValueError
                except (ValueError, TypeError):
                    messagebox.showerror("Erro", "Métricas de engajamento deve ser um número válido.")
                    return

            # Lógica de Inserção (CREATE)
            if mode == 'create':
                query_max = "SELECT NVL(MAX(Id_unicoPeca), 7000000) + 1 FROM Pecas_Criativas"
                result = self.db.execute_query(query_max)
                novo_id = result[1][0][0]

                query_main = "INSERT INTO Pecas_Criativas (Id_unicoPeca, Titulo, Descricao, Num_id_fiscal, Criador, Data_criacao, Status_aprov, Direitos_autorais, Classif_conteudo) VALUES (:id, :titulo, :desc, :fiscal, :criador, TO_DATE(:data, 'DD/MM/YYYY'), :status, :direitos, :classif)"
                params_main = {'id': novo_id, 'titulo': titulo, 'desc': descricao, 'fiscal': num_id_fiscal,
                               'criador': criador, 'data': data_criacao_str, 'status': status, 'direitos': direitos,
                               'classif': classificacao}
                self.db.execute_query(query_main, params_main, fetch=False)

                # Inserir na tabela de especialização
                if tipo_peca == "Visual":
                    query_spec = "INSERT INTO Pecas_Visuais (Id_unicoPeca, Dim_pvisuais, Resol_pvisuais, Form_arquivo, Pal_cores, El_graficos, Compat_disp_exib) VALUES (:id, :dim, :resol, :formato, :paleta, :elem, :compat)"
                    params_spec = {'id': novo_id, 'dim': fields['dim_visual'].get().strip(),
                                   'resol': fields['resol_visual'].get().strip(),
                                   'formato': fields['formato'].get().strip(),
                                   'paleta': fields['paleta'].get().strip() or None,
                                   'elem': fields['elementos'].get().strip() or None,
                                   'compat': fields['compat_disp'].get().strip() or None}
                    self.db.execute_query(query_spec, params_spec, fetch=False)
                elif tipo_peca == "Audiovisual":
                    query_spec = "INSERT INTO Pecas_Audiovisuais (Id_unicoPeca, Duracao, Qualidad_video, Resol_video, Legendas_disp, Req_tecnicos) VALUES (:id, :duracao, :qualidade, :resol, :legendas, :req)"
                    params_spec = {'id': novo_id, 'duracao': fields['duracao'].get().strip(),
                                   'qualidade': fields['qualidade'].get().strip(),
                                   'resol': fields['resol_video'].get().strip(),
                                   'legendas': fields['legendas'].get().strip() or None,
                                   'req': fields['req_tecnicos'].get().strip() or None}
                    self.db.execute_query(query_spec, params_spec, fetch=False)
                elif tipo_peca == "Interativa":
                    query_spec = "INSERT INTO Pecas_Interativas (Id_unicoPeca, Tec_util, Niv_interacao, Req_dispositivo, Metri_engaj, Dados_colect) VALUES (:id, :tec, :nivel, :req, :metricas, :dados)"
                    params_spec = {'id': novo_id, 'tec': fields['tecnologias'].get().strip(),
                                   'nivel': fields['nivel_inter'].get(),
                                   'req': fields['req_dispositivo'].get().strip() or None,
                                   'metricas': float(fields['metricas'].get().strip()),
                                   'dados': fields['dados_colect'].get("1.0", "end-1c").strip() or None}
                    self.db.execute_query(query_spec, params_spec, fetch=False)

                messagebox.showinfo("Sucesso", "Peça criada com sucesso!")

            # Lógica de Atualização (EDIT)
            else:
                query_main = "UPDATE Pecas_Criativas SET Titulo = :titulo, Descricao = :desc, Num_id_fiscal = :fiscal, Criador = :criador, Data_criacao = TO_DATE(:data, 'DD/MM/YYYY'), Status_aprov = :status, Direitos_autorais = :direitos, Classif_conteudo = :classif WHERE Id_unicoPeca = :id"
                params_main = {'id': id_peca, 'titulo': titulo, 'desc': descricao, 'fiscal': num_id_fiscal,
                               'criador': criador, 'data': data_criacao_str, 'status': status, 'direitos': direitos,
                               'classif': classificacao}
                self.db.execute_query(query_main, params_main, fetch=False)

                # Atualizar na tabela de especialização
                if tipo_peca == "Visual":
                    query_spec = "UPDATE Pecas_Visuais SET Dim_pvisuais = :dim, Resol_pvisuais = :resol, Form_arquivo = :formato, Pal_cores = :paleta, El_graficos = :elem, Compat_disp_exib = :compat WHERE Id_unicoPeca = :id"
                    params_spec = {'id': id_peca, 'dim': fields['dim_visual'].get().strip(),
                                   'resol': fields['resol_visual'].get().strip(),
                                   'formato': fields['formato'].get().strip(),
                                   'paleta': fields['paleta'].get().strip() or None,
                                   'elem': fields['elementos'].get().strip() or None,
                                   'compat': fields['compat_disp'].get().strip() or None}
                    self.db.execute_query(query_spec, params_spec, fetch=False)
                elif tipo_peca == "Audiovisual":
                    query_spec = "UPDATE Pecas_Audiovisuais SET Duracao = :duracao, Qualidad_video = :qualidade, Resol_video = :resol, Legendas_disp = :legendas, Req_tecnicos = :req WHERE Id_unicoPeca = :id"
                    params_spec = {'id': id_peca, 'duracao': fields['duracao'].get().strip(),
                                   'qualidade': fields['qualidade'].get().strip(),
                                   'resol': fields['resol_video'].get().strip(),
                                   'legendas': fields['legendas'].get().strip() or None,
                                   'req': fields['req_tecnicos'].get().strip() or None}
                    self.db.execute_query(query_spec, params_spec, fetch=False)
                elif tipo_peca == "Interativa":
                    query_spec = "UPDATE Pecas_Interativas SET Tec_util = :tec, Niv_interacao = :nivel, Req_dispositivo = :req, Metri_engaj = :metricas, Dados_colect = :dados WHERE Id_unicoPeca = :id"
                    params_spec = {'id': id_peca, 'tec': fields['tecnologias'].get().strip(),
                                   'nivel': fields['nivel_inter'].get(),
                                   'req': fields['req_dispositivo'].get().strip() or None,
                                   'metricas': float(fields['metricas'].get().strip()),
                                   'dados': fields['dados_colect'].get("1.0", "end-1c").strip() or None}
                    self.db.execute_query(query_spec, params_spec, fetch=False)

                messagebox.showinfo("Sucesso", "Peça atualizada com sucesso!")

            self.form_window.destroy()
            self.load_data()

        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Ocorreu um erro: {str(e)}")

    def delete_record(self):
        """Exclui a peça selecionada da tabela e do banco de dados"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma peça para excluir.")
            return

        item = self.tree.item(selected[0])
        id_peca = item['values'][0]
        titulo = item['values'][1]
        tipo = item['values'][2]

        confirm = messagebox.askyesno("Confirmar Exclusão",
                                      f"Deseja realmente excluir a peça '{titulo}'?\n\nEsta ação não pode ser desfeita!")

        if confirm:
            try:
                # Excluir da tabela de especialização correspondente
                if tipo == "Visual":
                    self.db.execute_query("DELETE FROM Pecas_Visuais WHERE Id_unicoPeca = :id", {'id': id_peca},
                                          fetch=False)
                elif tipo == "Audiovisual":
                    self.db.execute_query("DELETE FROM Pecas_Audiovisuais WHERE Id_unicoPeca = :id", {'id': id_peca},
                                          fetch=False)
                elif tipo == "Interativa":
                    self.db.execute_query("DELETE FROM Pecas_Interativas WHERE Id_unicoPeca = :id", {'id': id_peca},
                                          fetch=False)

                # Excluir relacionamentos (Ex: tabela Espaco_Peca)
                self.db.execute_query("DELETE FROM Espaco_Peca WHERE Id_unicoPeca = :id", {'id': id_peca}, fetch=False)

                # Atualizar referências em campanhas para NULL
                self.db.execute_query("UPDATE Campanha_Dados SET Id_unicoPeca = NULL WHERE Id_unicoPeca = :id",
                                      {'id': id_peca}, fetch=False)

                # Finalmente, excluir da tabela principal
                self.db.execute_query("DELETE FROM Pecas_Criativas WHERE Id_unicoPeca = :id", {'id': id_peca},
                                      fetch=False)

                messagebox.showinfo("Sucesso", "Peça excluída com sucesso!")
                self.load_data()

            except Exception as e:
                messagebox.showerror("Erro ao Excluir", f"Ocorreu um erro: {str(e)}")

    def show_details(self):
        """Mostra uma janela com todos os detalhes da peça selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma peça para ver os detalhes.")
            return

        item = self.tree.item(selected[0])
        id_peca = item['values'][0]

        # Buscar dados gerais e de especialização
        query_geral = """
                      SELECT p.Id_unicoPeca, \
                             p.Titulo, \
                             p.Descricao, \
                             an.Nome_razao_soc, \
                             p.Criador,
                             p.Data_criacao, \
                             p.Status_aprov, \
                             p.Direitos_autorais, \
                             p.Classif_conteudo,
                             CASE
                                 WHEN v.Id_unicoPeca IS NOT NULL THEN 'Visual'
                                 WHEN a.Id_unicoPeca IS NOT NULL THEN 'Audiovisual'
                                 WHEN i.Id_unicoPeca IS NOT NULL THEN 'Interativa'
                                 ELSE 'Genérica'
                                 END as Tipo
                      FROM Pecas_Criativas p
                               JOIN Anunciante_Dados an ON p.Num_id_fiscal = an.Num_id_fiscal
                               LEFT JOIN Pecas_Visuais v ON p.Id_unicoPeca = v.Id_unicoPeca
                               LEFT JOIN Pecas_Audiovisuais a ON p.Id_unicoPeca = a.Id_unicoPeca
                               LEFT JOIN Pecas_Interativas i ON p.Id_unicoPeca = i.Id_unicoPeca
                      WHERE p.Id_unicoPeca = :id \
                      """
        result_geral = self.db.execute_query(query_geral, {'id': id_peca})

        if not result_geral or not result_geral[1]:
            messagebox.showerror("Erro", "Não foi possível encontrar os detalhes da peça.")
            return

        data = result_geral[1][0]
        tipo = data[9]

        # Janela de detalhes
        details_window = ctk.CTkToplevel(self.parent)
        details_window.title(f"Detalhes da Peça - {data[1]}")
        details_window.geometry("750x650")
        details_window.transient(self.parent)
        details_window.grab_set()

        container = ctk.CTkScrollableFrame(details_window, fg_color="#2b2b2b")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(container, text=f"🎨 {data[1]}", font=("Helvetica", 20, "bold"),
                     text_color=self.COLORS['primary']).pack(pady=(0, 10))
        ctk.CTkLabel(container, text=f"Tipo: {tipo}", font=("Helvetica", 13, "bold"), fg_color=self.COLORS['secondary'],
                     corner_radius=20, padx=20, pady=5).pack(pady=(0, 20))

        info_frame = ctk.CTkFrame(container, fg_color=self.COLORS['dark'], corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Informações gerais
        info_fields = [
            ("🔢 ID:", data[0]), ("🏢 Anunciante:", data[3]), ("👤 Criador:", data[4]),
            ("📅 Data Criação:", data[5].strftime('%d/%m/%Y') if data[5] else ''),
            ("✅ Status:", data[6]), ("🔞 Classificação:", f"{data[8]} anos"),
        ]

        for i, (label, value) in enumerate(info_fields):
            self.create_info_row(info_frame, label, str(value), i)

        row_count = len(info_fields)
        # Descrição e Direitos
        for label_text, content, r in [("📝 Descrição:", data[2], row_count), ("©️ Direitos:", data[7], row_count + 1)]:
            ctk.CTkLabel(info_frame, text=label_text, font=("Helvetica", 12, "bold")).grid(row=r, column=0, padx=20,
                                                                                           pady=10, sticky="nw")
            text_box = ctk.CTkTextbox(info_frame, width=500, height=60)
            text_box.grid(row=r, column=1, padx=20, pady=10, sticky="w")
            text_box.insert("1.0", content if content else "Não informado")
            text_box.configure(state="disabled")
        row_count += 2

        # Detalhes de especialização
        spec_info = []
        if tipo == "Visual":
            query_spec = "SELECT Dim_pvisuais, Resol_pvisuais, Form_arquivo, Pal_cores, El_graficos, Compat_disp_exib FROM Pecas_Visuais WHERE Id_unicoPeca = :id"
            result_spec = self.db.execute_query(query_spec, {'id': id_peca})
            if result_spec and result_spec[1]:
                d = result_spec[1][0]
                spec_info = [("Dimensões:", d[0]), ("Resolução:", d[1]), ("Formato:", d[2]), ("Paleta Cores:", d[3]),
                             ("Elementos:", d[4]), ("Compatibilidade:", d[5])]
        elif tipo == "Audiovisual":
            query_spec = "SELECT Duracao, Qualidad_video, Resol_video, Legendas_disp, Req_tecnicos FROM Pecas_Audiovisuais WHERE Id_unicoPeca = :id"
            result_spec = self.db.execute_query(query_spec, {'id': id_peca})
            if result_spec and result_spec[1]:
                d = result_spec[1][0]
                spec_info = [("Duração:", d[0]), ("Qualidade Vídeo:", d[1]), ("Resolução Vídeo:", d[2]),
                             ("Legendas:", d[3]), ("Requisitos:", d[4])]
        elif tipo == "Interativa":
            query_spec = "SELECT Tec_util, Niv_interacao, Req_dispositivo, Metri_engaj, Dados_colect FROM Pecas_Interativas WHERE Id_unicoPeca = :id"
            result_spec = self.db.execute_query(query_spec, {'id': id_peca})
            if result_spec and result_spec[1]:
                d = result_spec[1][0]
                spec_info = [("Tecnologias:", d[0]), ("Nível Interação:", d[1]), ("Requisitos:", d[2]),
                             ("Métricas Engaj.:", d[3]), ("Dados Coletados:", d[4])]

        if spec_info:
            ctk.CTkLabel(info_frame, text=f"🎯 Detalhes de {tipo}:", font=("Helvetica", 12, "bold"),
                         text_color=self.COLORS['secondary']).grid(row=row_count, column=0, columnspan=2, padx=20,
                                                                   pady=(20, 10), sticky="w")
            row_count += 1
            for label, value in spec_info:
                if value:
                    self.create_info_row(info_frame, label, str(value), row_count)
                    row_count += 1

        ctk.CTkButton(container, text="✖️ Fechar", command=details_window.destroy, font=("Helvetica", 14, "bold"),
                      fg_color=self.COLORS['secondary'], width=150, height=40).pack(pady=20)

    def create_info_row(self, parent, label, value, row):
        """Cria uma linha de informação (label + valor) na janela de detalhes"""
        ctk.CTkLabel(parent, text=label, font=("Helvetica", 12, "bold")).grid(row=row, column=0, padx=20, pady=8,
                                                                              sticky="w")
        ctk.CTkLabel(parent, text=value, font=("Helvetica", 11), wraplength=450, justify="left").grid(row=row, column=1,
                                                                                                      padx=20, pady=8,
                                                                                                      sticky="w")

    def darken_color(self, color):
        """Escurece uma cor hexadecimal para o efeito hover"""
        if not color.startswith('#'): return color
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return f'#{darker_rgb[0]:02x}{darker_rgb[1]:02x}{darker_rgb[2]:02x}'


def show_pecas_module(parent, db, main_app):
    """Função de integração para iniciar e exibir o módulo CRUD de Peças"""
    PecasCRUD(parent, db, main_app)