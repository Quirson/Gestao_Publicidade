"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD ANUNCIANTES - GESTÃO COMPLETA                                  ║
║  Sistema de Gestão de Publicidade e Marketing                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from re import search


class AnunciantesCRUD:
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
        """Barra de ferramentas"""
        toolbar = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                               corner_radius=10, height=80)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(pady=15, padx=20)

        buttons = [
            ("➕ Novo Anunciante", self.open_create_form, self.COLORS['success']),
            ("✏️ Editar", self.open_edit_form, self.COLORS['primary']),
            ("🗑️ Excluir", self.delete_record, self.COLORS['danger']),
            ("🔄 Atualizar", self.load_data, self.COLORS['accent']),
            ("📊 Ver Campanhas", self.show_campaigns, self.COLORS['secondary'])
        ]

        for text, command, color in buttons:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                font=("Helvetica", 13, "bold"),
                fg_color=color,
                hover_color=self.darken_color(color),
                width=160,
                height=40,
                corner_radius=8
            )
            btn.pack(side="left", padx=5)

    def create_search_area(self):
        """Área de busca"""
        search_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                                    corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar Anunciantes",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Busca
        search_label = ctk.CTkLabel(filter_frame, text="Buscar:", font=("Helvetica", 12))
        search_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Nome, ID fiscal ou categoria...",
            width=350,
            height=35
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.search_var.trace('w', lambda *args: self.filter_data())

        # Filtro por porte
        porte_label = ctk.CTkLabel(filter_frame, text="Porte:", font=("Helvetica", 12))
        porte_label.grid(row=0, column=2, padx=(20, 10), pady=5, sticky="w")

        self.porte_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todos", "Pequeno", "Médio", "Grande"],
            width=150,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.porte_filter.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.porte_filter.set("Todos")

        # Filtro por classificação
        classif_label = ctk.CTkLabel(filter_frame, text="Classificação:", font=("Helvetica", 12))
        classif_label.grid(row=0, column=4, padx=(20, 10), pady=5, sticky="w")

        self.classif_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todas", "AAA - Excelente", "AA - Muito Bom", "A - Bom", "B - Regular", "C - Baixo"],
            width=180,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.classif_filter.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.classif_filter.set("Todas")

        # Limpar
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
        """Tabela de dados"""
        table_frame = ctk.CTkFrame(self.main_container, fg_color=self.COLORS['dark'],
                                   corner_radius=10)
        table_frame.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            table_frame,
            text="📋 Lista de Anunciantes",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        tree_container = ctk.CTkFrame(table_frame, fg_color="transparent")
        tree_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Estilo
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

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical")
        hsb = ttk.Scrollbar(tree_container, orient="horizontal")

        # Treeview
        columns = ('ID Fiscal', 'Nome/Razão Social', 'Categoria', 'Porte',
                   'Limite Crédito', 'Classificação', 'Contactos')
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
        widths = [100, 250, 180, 100, 130, 150, 150]
        for col, width in zip(columns, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Duplo clique
        self.tree.bind('<Double-1>', lambda e: self.open_edit_form())

    def load_data(self):
        """Carrega dados do banco"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT 
            Num_id_fiscal,
            Nome_razao_soc,
            Cat_negocio,
            Porte,
            Lim_cred_aprov,
            Classif_conf,
            Contactos
        FROM Anunciante_Dados
        ORDER BY Nome_razao_soc
        """

        result = self.db.execute_query(query)

        if result and result[1]:
            self.all_data = result[1]
            for row in result[1]:
                id_fiscal = row[0]
                nome = row[1][:40]
                categoria = row[2][:30]
                porte = row[3]
                credito = f"{row[4]:,.2f} MT"
                classif = row[5]
                contactos = row[6][:25]

                # Tag de cor por classificação
                tag = classif.split(' - ')[0].lower()
                self.tree.insert('', 'end', values=(
                    id_fiscal, nome, categoria, porte, credito, classif, contactos
                ), tags=(tag,))

            # Configurar cores
            self.tree.tag_configure('aaa', foreground='#28a745')
            self.tree.tag_configure('aa', foreground='#5cb85c')
            self.tree.tag_configure('a', foreground='#ffc107')
            self.tree.tag_configure('b', foreground='#fd7e14')
            self.tree.tag_configure('c', foreground='#dc3545')

    def filter_data(self):
        """Filtra dados"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_text = self.search_var.get().lower()
        porte_filter = self.porte_filter.get()
        classif_filter = self.classif_filter.get()

        if hasattr(self, 'all_data'):
            for row in self.all_data:
                nome = str(row[1]).lower()
                id_fiscal = str(row[0])
                categoria = str(row[2]).lower()
                porte = row[3]
                classif = row[5]

                # Filtros
                match_search = (search_text in nome or search_text in id_fiscal or
                                search_text in categoria)
                match_porte = (porte_filter == "Todos" or porte_filter == porte)
                match_classif = (classif_filter == "Todas" or classif_filter == classif)

                if match_search and match_porte and match_classif:
                    tag = classif.split(' - ')[0].lower()
                    self.tree.insert('', 'end', values=(
                        row[0], row[1][:40], row[2][:30], row[3],
                        f"{row[4]:,.2f} MT", row[5], row[6][:25]
                    ), tags=(tag,))

    def clear_filters(self):
        """Limpa filtros"""
        self.search_var.set("")
        self.porte_filter.set("Todos")
        self.classif_filter.set("Todas")
        self.load_data()

    def open_create_form(self):
        """Abre formulário de criação"""
        self.open_form(mode='create')

    def open_edit_form(self):
        """Abre formulário de edição"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um anunciante para editar.")
            return

        item = self.tree.item(selected[0])
        id_fiscal = item['values'][0]
        self.open_form(mode='edit', id_fiscal=id_fiscal)

    def open_form(self, mode='create', id_fiscal=None):
        """Abre formulário"""
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Novo Anunciante" if mode == 'create' else "Editar Anunciante")
        self.form_window.geometry("900x750")

        # Centralizar
        self.form_window.update_idletasks()
        x = (self.form_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.form_window.winfo_screenheight() // 2) - (750 // 2)
        self.form_window.geometry(f"900x750+{x}+{y}")

        self.form_window.transient(self.parent)
        self.form_window.grab_set()

        # Container
        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color="#2b2b2b")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_text = "📝 Novo Anunciante" if mode == 'create' else "✏️ Editar Anunciante"
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

        fields = {}
        row = 0

        # ID Fiscal
        if mode == 'edit':
            self.create_field(form_frame, "ID Fiscal:", row, fields, 'id_fiscal', readonly=True)
        else:
            self.create_field(form_frame, "ID Fiscal:*", row, fields, 'id_fiscal', width=200)
        row += 1

        # Nome/Razão Social
        self.create_field(form_frame, "Nome/Razão Social:*", row, fields, 'nome', width=500)
        row += 1

        # Categoria de Negócio
        self.create_field(form_frame, "Categoria de Negócio:*", row, fields, 'categoria', width=400)
        row += 1

        # Porte
        label = ctk.CTkLabel(form_frame, text="Porte:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['porte'] = ctk.CTkComboBox(
            form_frame,
            values=["Pequeno", "Médio", "Grande"],
            width=200,
            height=35
        )
        fields['porte'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Endereço
        self.create_field(form_frame, "Endereço:*", row, fields, 'endereco', width=500)
        row += 1

        # Contactos
        self.create_field(form_frame, "Contactos:*", row, fields, 'contactos', width=300)
        row += 1

        # Representante Legal
        self.create_field(form_frame, "Representante Legal:*", row, fields, 'rep_legal', width=300)
        row += 1

        # Preferências de Comunicação
        self.create_field(form_frame, "Pref. Comunicação:*", row, fields, 'pref_com', width=300)
        row += 1

        # Limite de Crédito
        self.create_field(form_frame, "Limite de Crédito (MT):*", row, fields, 'lim_cred', width=200)
        row += 1

        # Classificação
        label = ctk.CTkLabel(form_frame, text="Classificação:*", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['classif'] = ctk.CTkComboBox(
            form_frame,
            values=["AAA - Excelente", "AA - Muito Bom", "A - Bom", "B - Regular", "C - Baixo"],
            width=250,
            height=35
        )
        fields['classif'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Histórico de Campanhas (Textbox)
        label = ctk.CTkLabel(form_frame, text="Histórico:", font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="nw")

        fields['historico'] = ctk.CTkTextbox(form_frame, width=500, height=80)
        fields['historico'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Botões
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=lambda: self.save_record(mode, fields, id_fiscal),
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

        # Carregar dados se edição
        if mode == 'edit' and id_fiscal:
            self.load_form_data(fields, id_fiscal)

        self.form_fields = fields

    def create_field(self, parent, label_text, row, fields, field_name,
                     width=300, readonly=False):
        """Cria campo do formulário"""
        label = ctk.CTkLabel(parent, text=label_text, font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        if readonly:
            entry.configure(state="disabled")

        fields[field_name] = entry

    def load_form_data(self, fields, id_fiscal):
        """Carrega dados no formulário"""
        query = """
        SELECT Num_id_fiscal, Nome_razao_soc, Cat_negocio, Porte, Endereco,
               Contactos, Rep_legal, Historico_camp, Pref_com, Lim_cred_aprov,
               Classif_conf
        FROM Anunciante_Dados
        WHERE Num_id_fiscal = :id
        """
        result = self.db.execute_query(query, {'id': id_fiscal})

        if result and result[1]:
            data = result[1][0]

            fields['id_fiscal'].configure(state="normal")
            fields['id_fiscal'].insert(0, str(data[0]))
            fields['id_fiscal'].configure(state="disabled")

            fields['nome'].insert(0, data[1])
            fields['categoria'].insert(0, data[2])
            fields['porte'].set(data[3])
            fields['endereco'].insert(0, data[4])
            fields['contactos'].insert(0, data[5])
            fields['rep_legal'].insert(0, data[6])

            if data[7]:
                fields['historico'].insert("1.0", data[7])

            fields['pref_com'].insert(0, data[8])
            fields['lim_cred'].insert(0, str(data[9]))
            fields['classif'].set(data[10])

    def save_record(self, mode, fields, id_fiscal=None):
        """Salva registro"""
        try:
            # Validar campos obrigatórios
            if mode == 'create':
                id_fiscal_input = fields['id_fiscal'].get().strip()
                if not id_fiscal_input:
                    messagebox.showerror("Erro", "ID Fiscal é obrigatório.")
                    return

                # Validar se é numérico e tem 7 dígitos
                if not id_fiscal_input.isdigit() or len(id_fiscal_input) != 7:
                    messagebox.showerror("Erro", "ID Fiscal deve conter exatamente 7 números.")
                    return

                id_fiscal = int(id_fiscal_input)

            nome = fields['nome'].get().strip()
            categoria = fields['categoria'].get().strip()
            porte = fields['porte'].get()
            endereco = fields['endereco'].get().strip()
            contactos = fields['contactos'].get().strip()
            rep_legal = fields['rep_legal'].get().strip()
            pref_com = fields['pref_com'].get().strip()
            lim_cred = fields['lim_cred'].get().strip()
            classif = fields['classif'].get()
            historico = fields['historico'].get("1.0", "end-1c").strip()

            if not all([nome, categoria, porte, endereco, contactos, rep_legal,
                        pref_com, lim_cred, classif]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (*).")
                return

            # Validar limite de crédito
            try:
                lim_cred = float(lim_cred)
                if lim_cred < 0:
                    raise ValueError
            except:
                messagebox.showerror("Erro", "Limite de crédito inválido.")
                return

            # Validar contacto
            if not search(r'\+?\d+', contactos):
                messagebox.showerror("Erro", "Contacto deve conter números.")
                return

            if mode == 'create':
                # Verificar se ID já existe
                check_query = "SELECT COUNT(*) FROM Anunciante_Dados WHERE Num_id_fiscal = :id"
                result = self.db.execute_query(check_query, {'id': id_fiscal})
                if result and result[1] and result[1][0][0] > 0:
                    messagebox.showerror("Erro", "ID Fiscal já cadastrado.")
                    return

                # Insert
                query = """
                INSERT INTO Anunciante_Dados 
                (Num_id_fiscal, Nome_razao_soc, Cat_negocio, Porte, Endereco,
                 Contactos, Rep_legal, Historico_camp, Pref_com, Lim_cred_aprov,
                 Classif_conf)
                VALUES 
                (:id, :nome, :cat, :porte, :end, :cont, :rep, :hist, :pref, :lim, :classif)
                """

                params = {
                    'id': id_fiscal,
                    'nome': nome,
                    'cat': categoria,
                    'porte': porte,
                    'end': endereco,
                    'cont': contactos,
                    'rep': rep_legal,
                    'hist': historico if historico else None,
                    'pref': pref_com,
                    'lim': lim_cred,
                    'classif': classif
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Anunciante cadastrado com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

            else:  # edit
                query = """
                UPDATE Anunciante_Dados
                SET Nome_razao_soc = :nome,
                    Cat_negocio = :cat,
                    Porte = :porte,
                    Endereco = :end,
                    Contactos = :cont,
                    Rep_legal = :rep,
                    Historico_camp = :hist,
                    Pref_com = :pref,
                    Lim_cred_aprov = :lim,
                    Classif_conf = :classif
                WHERE Num_id_fiscal = :id
                """

                params = {
                    'id': id_fiscal,
                    'nome': nome,
                    'cat': categoria,
                    'porte': porte,
                    'end': endereco,
                    'cont': contactos,
                    'rep': rep_legal,
                    'hist': historico if historico else None,
                    'pref': pref_com,
                    'lim': lim_cred,
                    'classif': classif
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Anunciante atualizado com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def delete_record(self):
        """Exclui anunciante"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um anunciante para excluir.")
            return

        item = self.tree.item(selected[0])
        id_fiscal = item['values'][0]
        nome = item['values'][1]

        # Verificar campanhas
        query_camp = """
        SELECT COUNT(*) FROM Campanha_Dados WHERE Num_id_fiscal = :id
        """
        result_camp = self.db.execute_query(query_camp, {'id': id_fiscal})

        if result_camp and result_camp[1] and result_camp[1][0][0] > 0:
            num_campanhas = result_camp[1][0][0]
            messagebox.showerror(
                "Impossível Excluir",
                f"Este anunciante possui {num_campanhas} campanha(s) cadastrada(s).\n\n"
                "Exclua primeiro as campanhas relacionadas."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o anunciante:\n\n'{nome}'?\n\n"
            "Esta ação não pode ser desfeita!"
        )

        if confirm:
            try:
                # Excluir relacionamentos com agências
                query_rel = "DELETE FROM Anunciante_Agencia WHERE Num_id_fiscal = :id"
                self.db.execute_query(query_rel, {'id': id_fiscal}, fetch=False)

                # Excluir anunciante
                query = "DELETE FROM Anunciante_Dados WHERE Num_id_fiscal = :id"
                result = self.db.execute_query(query, {'id': id_fiscal}, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Anunciante excluído com sucesso!")
                    self.load_data()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    def show_campaigns(self):
        """Mostra campanhas do anunciante selecionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um anunciante.")
            return

        item = self.tree.item(selected[0])
        id_fiscal = item['values'][0]
        nome = item['values'][1]

        # Buscar campanhas
        query = """
        SELECT Cod_camp, Titulo, Orc_alocado, Data_inicio, Data_termino,
               CASE 
                   WHEN Data_termino < SYSDATE THEN 'Finalizada'
                   WHEN Data_inicio > SYSDATE THEN 'Agendada'
                   ELSE 'Ativa'
               END as Status
        FROM Campanha_Dados
        WHERE Num_id_fiscal = :id
        ORDER BY Data_inicio DESC
        """
        result = self.db.execute_query(query, {'id': id_fiscal})

        # Criar janela
        camp_window = ctk.CTkToplevel(self.parent)
        camp_window.title(f"Campanhas - {nome}")
        camp_window.geometry("900x600")

        # Centralizar
        camp_window.update_idletasks()
        x = (camp_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (camp_window.winfo_screenheight() // 2) - (600 // 2)
        camp_window.geometry(f"900x600+{x}+{y}")

        # Container
        container = ctk.CTkFrame(camp_window, fg_color="#2b2b2b")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            container,
            text=f"📢 Campanhas de {nome}",
            font=("Helvetica", 18, "bold"),
            text_color=self.COLORS['primary']
        )
        title.pack(pady=(0, 20))

        if result and result[1]:
            # Frame da tabela
            table_frame = ctk.CTkFrame(container, fg_color=self.COLORS['dark'])
            table_frame.pack(fill="both", expand=True)

            # Treeview
            columns = ('Código', 'Título', 'Orçamento', 'Data Início', 'Data Término', 'Status')
            tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=140, anchor="center")

            for row in result[1]:
                tree.insert('', 'end', values=(
                    row[0],
                    row[1][:30],
                    f"{row[2]:,.2f} MT",
                    row[3].strftime('%d/%m/%Y') if row[3] else '',
                    row[4].strftime('%d/%m/%Y') if row[4] else '',
                    row[5]
                ))

            tree.pack(fill="both", expand=True, padx=20, pady=20)

            # Estatísticas
            stats_frame = ctk.CTkFrame(container, fg_color=self.COLORS['dark'])
            stats_frame.pack(fill="x", pady=(10, 0))

            total = len(result[1])
            ativas = sum(1 for r in result[1] if r[5] == 'Ativa')
            total_investido = sum(r[2] for r in result[1])

            stats_text = f"📊 Total: {total} campanhas | ✅ Ativas: {ativas} | 💰 Investimento Total: {total_investido:,.2f} MT"
            stats_label = ctk.CTkLabel(
                stats_frame,
                text=stats_text,
                font=("Helvetica", 12, "bold"),
                text_color=self.COLORS['text']
            )
            stats_label.pack(pady=15)

        else:
            no_data = ctk.CTkLabel(
                container,
                text="📭 Nenhuma campanha encontrada para este anunciante.",
                font=("Helvetica", 14),
                text_color=self.COLORS['text_secondary']
            )
            no_data.pack(expand=True)

        # Botão fechar
        close_btn = ctk.CTkButton(
            container,
            text="✖️ Fechar",
            command=camp_window.destroy,
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS['secondary'],
            width=150,
            height=40
        )
        close_btn.pack(pady=20)

    def darken_color(self, color):
        """Escurece cor"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb


def show_anunciantes_module(parent, db, main_app):
    """Função de integração"""
    AnunciantesCRUD(parent, db, main_app)