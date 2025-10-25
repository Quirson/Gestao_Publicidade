"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD CAMPANHAS - GESTÃO COMPLETA                                    ║
║  Sistema de Gestão de Publicidade e Marketing                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from tkcalendar import DateEntry
import re


class CampanhasCRUD:
    def __init__(self, parent, db, main_app):
        self.parent = parent
        self.db = db
        self.main_app = main_app
        self.selected_item = None

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
        # Container principal com scroll
        self.main_container = ctk.CTkScrollableFrame(self.parent, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Barra de ferramentas
        self.create_toolbar()

        # Área de busca e filtros
        self.create_search_area()

        # Tabela de dados
        self.create_table()

        # Painel de formulário (inicialmente oculto)
        self.form_panel = None

    def create_toolbar(self):
        """Cria a barra de ferramentas com botões de ação"""
        toolbar = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                               corner_radius=10, height=80)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        # Frame interno para centralizar botões
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(pady=15, padx=20)

        buttons = [
            ("➕ Nova Campanha", self.open_create_form, self.COLORS['success']),
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
        """Cria área de busca e filtros"""
        search_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                                    corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 20))

        # Título
        title = ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar e Filtrar",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        # Frame de filtros
        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Campo de busca
        search_label = ctk.CTkLabel(
            filter_frame,
            text="Buscar:",
            font=("Helvetica", 12),
            text_color=self.COLORS['text']
        )
        search_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Digite título ou código da campanha...",
            width=300,
            height=35
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.search_var.trace('w', lambda *args: self.filter_data())

        # Filtro por anunciante
        anunciante_label = ctk.CTkLabel(
            filter_frame,
            text="Anunciante:",
            font=("Helvetica", 12),
            text_color=self.COLORS['text']
        )
        anunciante_label.grid(row=0, column=2, padx=(20, 10), pady=5, sticky="w")

        self.anunciante_filter = ctk.CTkComboBox(
            filter_frame,
            values=self.get_anunciantes_list(),
            width=200,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.anunciante_filter.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.anunciante_filter.set("Todos")

        # Botão limpar filtros
        clear_btn = ctk.CTkButton(
            filter_frame,
            text="🗑️ Limpar",
            command=self.clear_filters,
            width=100,
            height=35,
            fg_color=self.COLORS['secondary']
        )
        clear_btn.grid(row=0, column=4, padx=(20, 0), pady=5)

    def create_table(self):
        """Cria a tabela de dados"""
        table_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                                   corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        # Título
        title = ctk.CTkLabel(
            table_frame,
            text="📋 Lista de Campanhas",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        # Container para tabela com scrollbar
        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Estilo da tabela
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background=self.COLORS['dark'],
                        foreground=self.COLORS['text'],
                        fieldbackground=self.COLORS['dark'],
                        borderwidth=0,
                        rowheight=30)
        style.configure("Treeview.Heading",
                        background=self.COLORS['primary'],
                        foreground=self.COLORS['text'],
                        borderwidth=0,
                        font=("Helvetica", 11, "bold"))
        style.map("Treeview",
                  background=[('selected', self.COLORS['accent'])],
                  foreground=[('selected', self.COLORS['text'])])

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        # Treeview
        columns = ('Código', 'Título', 'Anunciante', 'Orçamento', 'Data Início',
                   'Data Término', 'Status')
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configurar colunas
        widths = [100, 200, 180, 120, 100, 100, 100]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Bind duplo clique
        self.tree.bind('<Double-1>', lambda e: self.open_edit_form())

    def load_data(self):
        """Carrega dados do banco"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Query
        query = """
        SELECT 
            c.Cod_camp,
            c.Titulo,
            a.Nome_razao_soc,
            c.Orc_alocado,
            c.Data_inicio,
            c.Data_termino,
            CASE 
                WHEN c.Data_termino < SYSDATE THEN 'Finalizada'
                WHEN c.Data_inicio > SYSDATE THEN 'Agendada'
                ELSE 'Ativa'
            END as Status
        FROM Campanha_Dados c
        JOIN Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal
        ORDER BY c.Data_inicio DESC
        """

        result = self.db.execute_query(query)

        if result and result[1]:
            self.all_data = result[1]  # Armazenar para filtros
            for row in result[1]:
                # Formatar dados
                cod = row[0]
                titulo = row[1]
                anunciante = row[2][:25]
                orcamento = f"{row[3]:,.2f} MT"
                data_inicio = row[4].strftime('%d/%m/%Y') if row[4] else ''
                data_termino = row[5].strftime('%d/%m/%Y') if row[5] else ''
                status = row[6]

                # Tag de cor baseada no status
                tag = status.lower()
                self.tree.insert('', 'end', values=(
                    cod, titulo, anunciante, orcamento,
                    data_inicio, data_termino, status
                ), tags=(tag,))

            # Configurar cores das tags
            self.tree.tag_configure('ativa', foreground='#28a745')
            self.tree.tag_configure('agendada', foreground='#ffc107')
            self.tree.tag_configure('finalizada', foreground='#dc3545')
        else:
            messagebox.showinfo("Info", "Nenhuma campanha encontrada.")

    def filter_data(self):
        """Filtra dados na tabela"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_text = self.search_var.get().lower()
        anunciante_filter = self.anunciante_filter.get()

        if hasattr(self, 'all_data'):
            for row in self.all_data:
                titulo = str(row[1]).lower()
                cod = str(row[0])
                anunciante = str(row[2])

                # Aplicar filtros
                match_search = (search_text in titulo or search_text in cod)
                match_anunciante = (anunciante_filter == "Todos" or
                                    anunciante_filter in anunciante)

                if match_search and match_anunciante:
                    status = row[6]
                    tag = status.lower()
                    self.tree.insert('', 'end', values=(
                        row[0], row[1], row[2][:25],
                        f"{row[3]:,.2f} MT",
                        row[4].strftime('%d/%m/%Y') if row[4] else '',
                        row[5].strftime('%d/%m/%Y') if row[5] else '',
                        status
                    ), tags=(tag,))

    def clear_filters(self):
        """Limpa todos os filtros"""
        self.search_var.set("")
        self.anunciante_filter.set("Todos")
        self.load_data()

    def get_anunciantes_list(self):
        """Retorna lista de anunciantes"""
        query = "SELECT Nome_razao_soc FROM Anunciante_Dados ORDER BY Nome_razao_soc"
        result = self.db.execute_query(query)

        anunciantes = ["Todos"]
        if result and result[1]:
            anunciantes.extend([row[0] for row in result[1]])

        return anunciantes

    def open_create_form(self):
        """Abre formulário para criar nova campanha"""
        self.open_form(mode='create')

    def open_edit_form(self):
        """Abre formulário para editar campanha selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma campanha para editar.")
            return

        item = self.tree.item(selected[0])
        cod_camp = item['values'][0]
        self.open_form(mode='edit', cod_camp=cod_camp)

    def open_form(self, mode='create', cod_camp=None):
        """Abre formulário (criar ou editar)"""
        # Criar janela modal
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Nova Campanha" if mode == 'create' else "Editar Campanha")
        self.form_window.geometry("900x700")

        # Centralizar
        self.form_window.update_idletasks()
        x = (self.form_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.form_window.winfo_screenheight() // 2) - (700 // 2)
        self.form_window.geometry(f"900x700+{x}+{y}")

        # Tornar modal
        self.form_window.transient(self.parent)
        self.form_window.grab_set()

        # Container com scroll
        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color="#2b2b2b")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_text = "📝 Nova Campanha" if mode == 'create' else "✏️ Editar Campanha"
        title = ctk.CTkLabel(
            form_container,
            text=title_text,
            font=("Helvetica", 20, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=(0, 20))

        # Frame do formulário
        form_frame = ctk.CTkFrame(form_container, fg_color=self.COLORS['dark'],
                                  corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Campos do formulário
        fields = {}
        row = 0

        # Código (apenas visualização em modo edição)
        if mode == 'edit':
            self.create_form_field(form_frame, "Código:", row, readonly=True,
                                   var_name='cod_camp', fields=fields)
            row += 1

        # Anunciante
        label = ctk.CTkLabel(form_frame, text="Anunciante:*",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['anunciante'] = ctk.CTkComboBox(
            form_frame,
            values=self.get_anunciantes_for_combo(),
            width=300,
            height=35
        )
        fields['anunciante'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Título
        self.create_form_field(form_frame, "Título:*", row, width=500,
                               var_name='titulo', fields=fields)
        row += 1

        # Objetivo (Text area)
        label = ctk.CTkLabel(form_frame, text="Objetivo:*",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="nw")

        fields['objectivo'] = ctk.CTkTextbox(form_frame, width=500, height=100)
        fields['objectivo'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Público-alvo
        self.create_form_field(form_frame, "Público-Alvo:*", row, width=500,
                               var_name='pub_alvo', fields=fields)
        row += 1

        # Orçamento
        self.create_form_field(form_frame, "Orçamento (MT):*", row, width=200,
                               var_name='orc_alocado', fields=fields)
        row += 1

        # Datas
        label = ctk.CTkLabel(form_frame, text="Data Início:*",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['data_inicio'] = DateEntry(form_frame, width=25, background='darkblue',
                                          foreground='white', borderwidth=2,
                                          date_pattern='dd/mm/yyyy')
        fields['data_inicio'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        label = ctk.CTkLabel(form_frame, text="Data Término:*",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['data_termino'] = DateEntry(form_frame, width=25, background='darkblue',
                                           foreground='white', borderwidth=2,
                                           date_pattern='dd/mm/yyyy')
        fields['data_termino'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Botões
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=lambda: self.save_record(mode, fields, cod_camp),
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS['success'],
            width=150,
            height=40
        )
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.form_window.destroy,
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS['danger'],
            width=150,
            height=40
        )
        cancel_btn.pack(side="left", padx=10)

        # Carregar dados se modo edição
        if mode == 'edit' and cod_camp:
            self.load_form_data(fields, cod_camp)

        self.form_fields = fields

    def create_form_field(self, parent, label_text, row, width=300, readonly=False,
                          var_name=None, fields=None):
        """Cria um campo de formulário"""
        label = ctk.CTkLabel(parent, text=label_text, font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        if readonly:
            entry.configure(state="disabled")

        if fields is not None and var_name:
            fields[var_name] = entry

    def get_anunciantes_for_combo(self):
        """Retorna lista formatada de anunciantes para combobox"""
        query = "SELECT Num_id_fiscal, Nome_razao_soc FROM Anunciante_Dados ORDER BY Nome_razao_soc"
        result = self.db.execute_query(query)

        anunciantes = []
        if result and result[1]:
            for row in result[1]:
                anunciantes.append(f"{row[0]} - {row[1]}")

        return anunciantes if anunciantes else ["Nenhum anunciante cadastrado"]

    def load_form_data(self, fields, cod_camp):
        """Carrega dados no formulário para edição"""
        query = """
        SELECT Cod_camp, Num_id_fiscal, Titulo, Objectivo, Pub_alvo, 
               Orc_alocado, Data_inicio, Data_termino
        FROM Campanha_Dados
        WHERE Cod_camp = :cod
        """
        result = self.db.execute_query(query, {'cod': cod_camp})

        if result and result[1]:
            data = result[1][0]

            fields['cod_camp'].configure(state="normal")
            fields['cod_camp'].insert(0, str(data[0]))
            fields['cod_camp'].configure(state="disabled")

            # Anunciante
            anunciante_id = data[1]
            query_anun = f"SELECT Nome_razao_soc FROM Anunciante_Dados WHERE Num_id_fiscal = {anunciante_id}"
            result_anun = self.db.execute_query(query_anun)
            if result_anun and result_anun[1]:
                anunciante_text = f"{anunciante_id} - {result_anun[1][0][0]}"
                fields['anunciante'].set(anunciante_text)

            fields['titulo'].insert(0, data[2])
            fields['objectivo'].insert("1.0", data[3])
            fields['pub_alvo'].insert(0, data[4])
            fields['orc_alocado'].insert(0, str(data[5]))

            if data[6]:
                fields['data_inicio'].set_date(data[6])
            if data[7]:
                fields['data_termino'].set_date(data[7])

    def save_record(self, mode, fields, cod_camp=None):
        """Salva registro (criar ou atualizar)"""
        try:
            # Validar campos obrigatórios
            anunciante = fields['anunciante'].get()
            if not anunciante or anunciante == "Nenhum anunciante cadastrado":
                messagebox.showerror("Erro", "Selecione um anunciante.")
                return

            # Extrair ID do anunciante
            num_id_fiscal = int(anunciante.split(' - ')[0])

            titulo = fields['titulo'].get().strip()
            objectivo = fields['objectivo'].get("1.0", "end-1c").strip()
            pub_alvo = fields['pub_alvo'].get().strip()
            orc_alocado = fields['orc_alocado'].get().strip()

            if not all([titulo, objectivo, pub_alvo, orc_alocado]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (*).")
                return

            # Validar orçamento
            try:
                orc_alocado = float(orc_alocado)
                if orc_alocado <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Erro", "Orçamento inválido. Use apenas números.")
                return

            data_inicio = fields['data_inicio'].get_date()
            data_termino = fields['data_termino'].get_date()

            if data_termino <= data_inicio:
                messagebox.showerror("Erro", "Data de término deve ser posterior à data de início.")
                return

            # Preparar dados
            data_inicio_str = data_inicio.strftime('%d/%m/%Y')
            data_termino_str = data_termino.strftime('%d/%m/%Y')

            if mode == 'create':
                # Gerar novo código
                query_max = "SELECT NVL(MAX(Cod_camp), 8000000) + 1 FROM Campanha_Dados"
                result = self.db.execute_query(query_max)
                novo_cod = result[1][0][0] if result and result[1] else 8000001

                # Insert
                query = """
                INSERT INTO Campanha_Dados 
                (Cod_camp, Num_id_fiscal, Titulo, Objectivo, Pub_alvo, Orc_alocado,
                 Data_inicio, Data_termino)
                VALUES 
                (:cod, :fiscal, :titulo, :obj, :pub, :orc,
                 TO_DATE(:dt_ini, 'DD/MM/YYYY'), TO_DATE(:dt_fim, 'DD/MM/YYYY'))
                """

                params = {
                    'cod': novo_cod,
                    'fiscal': num_id_fiscal,
                    'titulo': titulo,
                    'obj': objectivo,
                    'pub': pub_alvo,
                    'orc': orc_alocado,
                    'dt_ini': data_inicio_str,
                    'dt_fim': data_termino_str
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Campanha criada com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

            else:  # edit
                query = """
                UPDATE Campanha_Dados
                SET Num_id_fiscal = :fiscal,
                    Titulo = :titulo,
                    Objectivo = :obj,
                    Pub_alvo = :pub,
                    Orc_alocado = :orc,
                    Data_inicio = TO_DATE(:dt_ini, 'DD/MM/YYYY'),
                    Data_termino = TO_DATE(:dt_fim, 'DD/MM/YYYY')
                WHERE Cod_camp = :cod
                """

                params = {
                    'cod': cod_camp,
                    'fiscal': num_id_fiscal,
                    'titulo': titulo,
                    'obj': objectivo,
                    'pub': pub_alvo,
                    'orc': orc_alocado,
                    'dt_ini': data_inicio_str,
                    'dt_fim': data_termino_str
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Campanha atualizada com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def delete_record(self):
        """Exclui campanha selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma campanha para excluir.")
            return

        item = self.tree.item(selected[0])
        cod_camp = item['values'][0]
        titulo = item['values'][1]

        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir a campanha:\n\n'{titulo}' (Código: {cod_camp})?\n\n"
            "Esta ação não pode ser desfeita!"
        )

        if confirm:
            try:
                # Verificar dependências
                query_dep = """
                SELECT COUNT(*) FROM Campanha_Espaco WHERE Cod_camp = :cod
                UNION ALL
                SELECT COUNT(*) FROM Campanha_PublicoAlvo WHERE Cod_camp = :cod
                UNION ALL
                SELECT COUNT(*) FROM Campanha_Canal WHERE Cod_camp = :cod
                """
                result_dep = self.db.execute_query(query_dep, {'cod': cod_camp})

                has_dependencies = False
                if result_dep and result_dep[1]:
                    for row in result_dep[1]:
                        if row[0] > 0:
                            has_dependencies = True
                            break

                if has_dependencies:
                    delete_deps = messagebox.askyesno(
                        "Dependências Encontradas",
                        "Esta campanha possui dados relacionados (espaços, canais, etc.).\n\n"
                        "Deseja excluir a campanha E todos os dados relacionados?"
                    )

                    if not delete_deps:
                        return

                    # Excluir dependências
                    queries_dep = [
                        "DELETE FROM Campanha_Espaco WHERE Cod_camp = :cod",
                        "DELETE FROM Campanha_PublicoAlvo WHERE Cod_camp = :cod",
                        "DELETE FROM Campanha_Canal WHERE Cod_camp = :cod",
                        "UPDATE Pecas_Criativas SET Cod_camp = NULL WHERE Cod_camp = :cod"
                    ]

                    for q in queries_dep:
                        self.db.execute_query(q, {'cod': cod_camp}, fetch=False)

                # Excluir campanha
                query = "DELETE FROM Campanha_Dados WHERE Cod_camp = :cod"
                result = self.db.execute_query(query, {'cod': cod_camp}, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Campanha excluída com sucesso!")
                    self.load_data()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    def show_details(self):
        """Mostra detalhes completos da campanha selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma campanha para ver detalhes.")
            return

        item = self.tree.item(selected[0])
        cod_camp = item['values'][0]

        # Buscar dados completos
        query = """
        SELECT 
            c.Cod_camp,
            c.Titulo,
            a.Nome_razao_soc,
            c.Objectivo,
            c.Pub_alvo,
            c.Orc_alocado,
            c.Data_inicio,
            c.Data_termino,
            c.Elem_criativos,
            c.Metri_desemp,
            c.Result_obtidos,
            CASE 
                WHEN c.Data_termino < SYSDATE THEN 'Finalizada'
                WHEN c.Data_inicio > SYSDATE THEN 'Agendada'
                ELSE 'Ativa'
            END as Status
        FROM Campanha_Dados c
        JOIN Anunciante_Dados a ON c.Num_id_fiscal = a.Num_id_fiscal
        WHERE c.Cod_camp = :cod
        """

        result = self.db.execute_query(query, {'cod': cod_camp})

        if not result or not result[1]:
            messagebox.showerror("Erro", "Campanha não encontrada.")
            return

        data = result[1][0]

        # Criar janela de detalhes
        details_window = ctk.CTkToplevel(self.parent)
        details_window.title(f"Detalhes da Campanha - {data[1]}")
        details_window.geometry("800x600")

        # Centralizar
        details_window.update_idletasks()
        x = (details_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (details_window.winfo_screenheight() // 2) - (600 // 2)
        details_window.geometry(f"800x600+{x}+{y}")

        # Container com scroll
        container = ctk.CTkScrollableFrame(details_window, fg_color="#2b2b2b")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            container,
            text=f"📊 {data[1]}",
            font=("Helvetica", 22, "bold"),
            text_color=self.COLORS['primary']
        )
        title.pack(pady=(0, 20))

        # Status badge
        status_color = {
            'Ativa': self.COLORS['success'],
            'Agendada': '#ffc107',
            'Finalizada': self.COLORS['danger']
        }

        status_badge = ctk.CTkLabel(
            container,
            text=data[11],
            font=("Helvetica", 14, "bold"),
            fg_color=status_color.get(data[11], self.COLORS['accent']),
            corner_radius=20,
            padx=20,
            pady=5
        )
        status_badge.pack(pady=(0, 20))

        # Frame de informações
        info_frame = ctk.CTkFrame(container, fg_color=self.COLORS['dark'], corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Campos de informação
        info_fields = [
            ("🔢 Código:", data[0]),
            ("🏢 Anunciante:", data[2]),
            ("💰 Orçamento:", f"{data[5]:,.2f} MT"),
            ("📅 Data Início:", data[6].strftime('%d/%m/%Y') if data[6] else ''),
            ("📅 Data Término:", data[7].strftime('%d/%m/%Y') if data[7] else ''),
            ("🎯 Público-Alvo:", data[4]),
        ]

        for i, (label, value) in enumerate(info_fields):
            self.create_info_row(info_frame, label, str(value), i)

        # Objetivo (área maior)
        obj_label = ctk.CTkLabel(
            info_frame,
            text="🎯 Objetivo:",
            font=("Helvetica", 12, "bold"),
            text_color=self.COLORS['text']
        )
        obj_label.grid(row=len(info_fields), column=0, padx=20, pady=10, sticky="nw")

        obj_text = ctk.CTkTextbox(info_frame, width=500, height=100)
        obj_text.grid(row=len(info_fields), column=1, padx=20, pady=10, sticky="w")
        obj_text.insert("1.0", data[3] if data[3] else "Não informado")
        obj_text.configure(state="disabled")

        # Buscar dados relacionados
        # Espaços
        query_espacos = """
        SELECT e.Local_fis_dig, e.Tipo
        FROM Espaco_Dados e
        JOIN Campanha_Espaco ce ON e.Id_espaco = ce.Id_espaco
        WHERE ce.Cod_camp = :cod
        """
        result_espacos = self.db.execute_query(query_espacos, {'cod': cod_camp})

        if result_espacos and result_espacos[1]:
            espacos_label = ctk.CTkLabel(
                info_frame,
                text="📺 Espaços Utilizados:",
                font=("Helvetica", 12, "bold"),
                text_color=self.COLORS['text']
            )
            espacos_label.grid(row=len(info_fields) + 1, column=0, padx=20, pady=10, sticky="nw")

            espacos_text = "\n".join([f"• {row[0]} ({row[1]})" for row in result_espacos[1]])
            espacos_value = ctk.CTkLabel(
                info_frame,
                text=espacos_text,
                font=("Helvetica", 11),
                text_color=self.COLORS['text_secondary'],
                justify="left"
            )
            espacos_value.grid(row=len(info_fields) + 1, column=1, padx=20, pady=10, sticky="w")

        # Canais
        query_canais = """
        SELECT Canais_util
        FROM Campanha_Canal
        WHERE Cod_camp = :cod
        """
        result_canais = self.db.execute_query(query_canais, {'cod': cod_camp})

        if result_canais and result_canais[1]:
            canais_label = ctk.CTkLabel(
                info_frame,
                text="📡 Canais:",
                font=("Helvetica", 12, "bold"),
                text_color=self.COLORS['text']
            )
            canais_label.grid(row=len(info_fields) + 2, column=0, padx=20, pady=10, sticky="nw")

            canais_text = ", ".join([row[0] for row in result_canais[1]])
            canais_value = ctk.CTkLabel(
                info_frame,
                text=canais_text,
                font=("Helvetica", 11),
                text_color=self.COLORS['text_secondary'],
                wraplength=450,
                justify="left"
            )
            canais_value.grid(row=len(info_fields) + 2, column=1, padx=20, pady=10, sticky="w")

        # Botão fechar
        close_btn = ctk.CTkButton(
            container,
            text="✖️ Fechar",
            command=details_window.destroy,
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS['secondary'],
            width=150,
            height=40
        )
        close_btn.pack(pady=20)

    def create_info_row(self, parent, label, value, row):
        """Cria uma linha de informação"""
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=("Helvetica", 12, "bold"),
            text_color=self.COLORS['text']
        )
        label_widget.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        value_widget = ctk.CTkLabel(
            parent,
            text=value,
            font=("Helvetica", 11),
            text_color=self.COLORS['text_secondary']
        )
        value_widget.grid(row=row, column=1, padx=20, pady=10, sticky="w")

    def darken_color(self, color):
        """Escurece uma cor hexadecimal"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb


# ═════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PARA INTEGRAR NO MAIN APP
# ═════════════════════════════════════════════════════════════════════════════

def show_campanhas_module(parent, db, main_app):
    """Função para chamar no menu principal"""
    CampanhasCRUD(parent, db, main_app)