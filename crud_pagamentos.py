"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD PAGAMENTOS - GESTÃO COMPLETA                                   ║
║  Sistema de Gestão de Publicidade e Marketing                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk


class PagamentosCRUD:
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
        """Cria interface"""
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
            ("➕ Novo Pagamento", self.open_create_form, self.COLORS['success']),
            ("✏️ Editar", self.open_edit_form, self.COLORS['primary']),
            ("🗑️ Excluir", self.delete_record, self.COLORS['danger']),
            ("🔄 Atualizar", self.load_data, self.COLORS['accent']),
            ("📊 Relatório Financeiro", self.show_financial_report, self.COLORS['secondary'])
        ]

        for text, command, color in buttons:
            btn = ctk.CTkButton(
                btn_frame,
                text=text,
                command=command,
                font=("Helvetica", 13, "bold"),
                fg_color=color,
                hover_color=self.darken_color(color),
                width=180,
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
            text="🔍 Buscar Pagamentos",
            font=("Helvetica", 14, "bold"),
            text_color=self.COLORS['text']
        )
        title.pack(pady=10, padx=20, anchor="w")

        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Busca
        search_label = ctk.CTkLabel(filter_frame, text="Código:", font=("Helvetica", 12))
        search_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Código do pagamento...",
            width=200,
            height=35
        )
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.search_var.trace('w', lambda *args: self.filter_data())

        # Filtro por modalidade
        modal_label = ctk.CTkLabel(filter_frame, text="Modalidade:", font=("Helvetica", 12))
        modal_label.grid(row=0, column=2, padx=(20, 10), pady=5, sticky="w")

        self.modal_filter = ctk.CTkComboBox(
            filter_frame,
            values=self.get_modalidades_list(),
            width=180,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.modal_filter.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.modal_filter.set("Todas")

        # Filtro por método
        metodo_label = ctk.CTkLabel(filter_frame, text="Método:", font=("Helvetica", 12))
        metodo_label.grid(row=0, column=4, padx=(20, 10), pady=5, sticky="w")

        self.metodo_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todos", "Transferência Bancária", "Cartão de Crédito",
                    "Cheque", "M-Pesa", "Dinheiro"],
            width=200,
            height=35,
            command=lambda x: self.filter_data()
        )
        self.metodo_filter.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.metodo_filter.set("Todos")

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
            text="💳 Lista de Pagamentos",
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
        columns = ('Código', 'Modalidade', 'Valor', 'Desconto', 'Valor Final',
                   'Método Pagamento', 'Reconciliação')
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
        widths = [100, 150, 130, 100, 130, 180, 180]
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
                SELECT p.Cod_pagamento, \
                       mc.Modal_cobranca, \
                       p.Precos_dinam, \
                       pr.Desc_volume, \
                       p.Metod_pagamento, \
                       p.Reconc_financ
                FROM Pagamentos p
                         JOIN Modalidade_Cobranca mc ON p.Cod_modalidade = mc.Cod_modalidade
                         LEFT JOIN Promocoes pr ON p.Cod_promocao = pr.Cod_promocao
                ORDER BY p.Cod_pagamento DESC \
                """

        result = self.db.execute_query(query)

        if result and result[1]:
            self.all_data = result[1]
            for row in result[1]:
                cod = row[0]
                modalidade = row[1]
                valor = row[2]
                desconto = row[3] if row[3] else 0

                # Calcular valor final com desconto
                valor_final = valor * (1 - desconto / 100)

                metodo = row[4]
                reconc = row[5][:30] if row[5] else "Pendente"

                self.tree.insert('', 'end', values=(
                    cod,
                    modalidade,
                    f"{valor:,.2f} MT",
                    f"{desconto}%",
                    f"{valor_final:,.2f} MT",
                    metodo,
                    reconc
                ))

    def filter_data(self):
        """Filtra dados"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_text = self.search_var.get()
        modal_filter = self.modal_filter.get()
        metodo_filter = self.metodo_filter.get()

        if hasattr(self, 'all_data'):
            for row in self.all_data:
                cod = str(row[0])
                modalidade = row[1]
                metodo = row[4]

                # Aplicar filtros
                match_search = (not search_text or search_text in cod)
                match_modal = (modal_filter == "Todas" or modal_filter == modalidade)
                match_metodo = (metodo_filter == "Todos" or metodo_filter == metodo)

                if match_search and match_modal and match_metodo:
                    valor = row[2]
                    desconto = row[3] if row[3] else 0
                    valor_final = valor * (1 - desconto / 100)
                    reconc = row[5][:30] if row[5] else "Pendente"

                    self.tree.insert('', 'end', values=(
                        row[0],
                        modalidade,
                        f"{valor:,.2f} MT",
                        f"{desconto}%",
                        f"{valor_final:,.2f} MT",
                        metodo,
                        reconc
                    ))

    def clear_filters(self):
        """Limpa filtros"""
        self.search_var.set("")
        self.modal_filter.set("Todas")
        self.metodo_filter.set("Todos")
        self.load_data()

    def get_modalidades_list(self):
        """Retorna lista de modalidades"""
        query = "SELECT Modal_cobranca FROM Modalidade_Cobranca ORDER BY Modal_cobranca"
        result = self.db.execute_query(query)

        modalidades = ["Todas"]
        if result and result[1]:
            modalidades.extend([row[0] for row in result[1]])

        return modalidades

    def open_create_form(self):
        """Formulário de criação"""
        self.open_form(mode='create')

    def open_edit_form(self):
        """Formulário de edição"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento para editar.")
            return

        item = self.tree.item(selected[0])
        cod_pag = item['values'][0]
        self.open_form(mode='edit', cod_pag=cod_pag)

    def open_form(self, mode='create', cod_pag=None):
        """Abre formulário"""
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Novo Pagamento" if mode == 'create' else "Editar Pagamento")
        self.form_window.geometry("850x650")

        # Centralizar
        self.form_window.update_idletasks()
        x = (self.form_window.winfo_screenwidth() // 2) - (850 // 2)
        y = (self.form_window.winfo_screenheight() // 2) - (650 // 2)
        self.form_window.geometry(f"850x650+{x}+{y}")

        self.form_window.transient(self.parent)
        self.form_window.grab_set()

        # Container
        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color="#2b2b2b")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_text = "💳 Novo Pagamento" if mode == 'create' else "✏️ Editar Pagamento"
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

        # Código (apenas visualização em edição)
        if mode == 'edit':
            self.create_field(form_frame, "Código:", row, fields, 'cod_pag',
                              readonly=True, width=150)
            row += 1

        # Modalidade de Cobrança
        label = ctk.CTkLabel(form_frame, text="Modalidade Cobrança:*",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['modalidade'] = ctk.CTkComboBox(
            form_frame,
            values=self.get_modalidades_for_combo(),
            width=300,
            height=35
        )
        fields['modalidade'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Preço Dinâmico
        self.create_field(form_frame, "Valor (MT):*", row, fields, 'preco', width=200)
        row += 1

        # Promoção
        label = ctk.CTkLabel(form_frame, text="Promoção:",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['promocao'] = ctk.CTkComboBox(
            form_frame,
            values=self.get_promocoes_for_combo(),
            width=300,
            height=35,
            command=lambda choice: self.update_final_value(fields)
        )
        fields['promocao'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Valor Final (calculado)
        label = ctk.CTkLabel(form_frame, text="Valor Final:",
                             font=("Helvetica", 12, "bold"),
                             text_color=self.COLORS['success'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['valor_final'] = ctk.CTkLabel(
            form_frame,
            text="0.00 MT",
            font=("Helvetica", 16, "bold"),
            text_color=self.COLORS['success']
        )
        fields['valor_final'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Método de Pagamento
        label = ctk.CTkLabel(form_frame, text="Método Pagamento:*",
                             font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['metodo'] = ctk.CTkComboBox(
            form_frame,
            values=["Transferência Bancária", "Cartão de Crédito", "Cheque",
                    "M-Pesa", "Dinheiro"],
            width=250,
            height=35
        )
        fields['metodo'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Comprovante de Veiculação
        self.create_field(form_frame, "Comprovante:", row, fields, 'comprovante', width=400)
        row += 1

        # Reconciliação Financeira
        self.create_field(form_frame, "Reconciliação:", row, fields, 'reconciliacao', width=400)
        row += 1

        # Botões
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=lambda: self.save_record(mode, fields, cod_pag),
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
        if mode == 'edit' and cod_pag:
            self.load_form_data(fields, cod_pag)

        # Vincular evento de mudança no preço
        fields['preco'].bind('<KeyRelease>', lambda e: self.update_final_value(fields))

        self.form_fields = fields

    def create_field(self, parent, label_text, row, fields, field_name,
                     width=300, readonly=False):
        """Cria campo"""
        label = ctk.CTkLabel(parent, text=label_text, font=("Helvetica", 12, "bold"))
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        if readonly:
            entry.configure(state="disabled")

        fields[field_name] = entry

    def get_modalidades_for_combo(self):
        """Retorna modalidades para combobox"""
        query = "SELECT Cod_modalidade, Modal_cobranca FROM Modalidade_Cobranca ORDER BY Modal_cobranca"
        result = self.db.execute_query(query)

        modalidades = []
        if result and result[1]:
            for row in result[1]:
                modalidades.append(f"{row[0]} - {row[1]}")

        return modalidades if modalidades else ["Nenhuma modalidade cadastrada"]

    def get_promocoes_for_combo(self):
        """Retorna promoções para combobox"""
        query = "SELECT Cod_promocao, Pacotes_promo, Desc_volume FROM Promocoes ORDER BY Desc_volume DESC"
        result = self.db.execute_query(query)

        promocoes = ["Nenhuma"]
        if result and result[1]:
            for row in result[1]:
                promocoes.append(f"{row[0]} - {row[1]} ({row[2]}% desc.)")

        return promocoes

    def update_final_value(self, fields):
        """Atualiza valor final com desconto"""
        try:
            preco_str = fields['preco'].get().strip()
            if not preco_str:
                return

            preco = float(preco_str)
            promocao = fields['promocao'].get()

            desconto = 0
            if promocao and promocao != "Nenhuma":
                # Extrair percentual de desconto
                desc_str = promocao.split('(')[1].split('%')[0]
                desconto = float(desc_str)

            valor_final = preco * (1 - desconto / 100)
            fields['valor_final'].configure(text=f"{valor_final:,.2f} MT")

        except:
            fields['valor_final'].configure(text="0.00 MT")

    def load_form_data(self, fields, cod_pag):
        """Carrega dados no formulário"""
        query = """
                SELECT p.Cod_pagamento, \
                       p.Cod_modalidade, \
                       mc.Modal_cobranca, \
                       p.Precos_dinam,
                       p.Cod_promocao, \
                       pr.Pacotes_promo, \
                       pr.Desc_volume, \
                       p.Metod_pagamento,
                       p.Comprov_veic, \
                       p.Reconc_financ
                FROM Pagamentos p
                         JOIN Modalidade_Cobranca mc ON p.Cod_modalidade = mc.Cod_modalidade
                         LEFT JOIN Promocoes pr ON p.Cod_promocao = pr.Cod_promocao
                WHERE p.Cod_pagamento = :cod \
                """
        result = self.db.execute_query(query, {'cod': cod_pag})

        if result and result[1]:
            data = result[1][0]

            fields['cod_pag'].configure(state="normal")
            fields['cod_pag'].insert(0, str(data[0]))
            fields['cod_pag'].configure(state="disabled")

            # Modalidade
            modal_text = f"{data[1]} - {data[2]}"
            fields['modalidade'].set(modal_text)

            # Preço
            fields['preco'].insert(0, str(data[3]))

            # Promoção
            if data[4]:
                promo_text = f"{data[4]} - {data[5]} ({data[6]}% desc.)"
                fields['promocao'].set(promo_text)
            else:
                fields['promocao'].set("Nenhuma")

            # Método
            fields['metodo'].set(data[7])

            # Comprovante
            if data[8]:
                fields['comprovante'].insert(0, data[8])

            # Reconciliação
            if data[9]:
                fields['reconciliacao'].insert(0, data[9])

            # Atualizar valor final
            self.update_final_value(fields)

    def save_record(self, mode, fields, cod_pag=None):
        """Salva registro"""
        try:
            # Validar campos
            modalidade = fields['modalidade'].get()
            if not modalidade or modalidade == "Nenhuma modalidade cadastrada":
                messagebox.showerror("Erro", "Selecione uma modalidade.")
                return

            cod_modalidade = int(modalidade.split(' - ')[0])

            preco = fields['preco'].get().strip()
            metodo = fields['metodo'].get()

            if not all([preco, metodo]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (*).")
                return

            # Validar preço
            try:
                preco = float(preco)
                if preco < 0:
                    raise ValueError
            except:
                messagebox.showerror("Erro", "Valor inválido.")
                return

            # Promoção (opcional)
            promocao = fields['promocao'].get()
            cod_promocao = None
            if promocao and promocao != "Nenhuma":
                cod_promocao = int(promocao.split(' - ')[0])

            comprovante = fields['comprovante'].get().strip()
            reconciliacao = fields['reconciliacao'].get().strip()

            if mode == 'create':
                # Gerar novo código
                query_max = "SELECT NVL(MAX(Cod_pagamento), 5000000) + 1 FROM Pagamentos"
                result = self.db.execute_query(query_max)
                novo_cod = result[1][0][0] if result and result[1] else 5000001

                # Insert
                query = """
                        INSERT INTO Pagamentos
                        (Cod_pagamento, Cod_modalidade, Precos_dinam, Cod_promocao,
                         Metod_pagamento, Comprov_veic, Reconc_financ)
                        VALUES (:cod, :modal, :preco, :promo, :metodo, :comprov, :reconc) \
                        """

                params = {
                    'cod': novo_cod,
                    'modal': cod_modalidade,
                    'preco': preco,
                    'promo': cod_promocao,
                    'metodo': metodo,
                    'comprov': comprovante if comprovante else None,
                    'reconc': reconciliacao if reconciliacao else None
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Pagamento cadastrado com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

            else:  # edit
                query = """
                        UPDATE Pagamentos
                        SET Cod_modalidade  = :modal,
                            Precos_dinam    = :preco,
                            Cod_promocao    = :promo,
                            Metod_pagamento = :metodo,
                            Comprov_veic    = :comprov,
                            Reconc_financ   = :reconc
                        WHERE Cod_pagamento = :cod \
                        """

                params = {
                    'cod': cod_pag,
                    'modal': cod_modalidade,
                    'preco': preco,
                    'promo': cod_promocao,
                    'metodo': metodo,
                    'comprov': comprovante if comprovante else None,
                    'reconc': reconciliacao if reconciliacao else None
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Pagamento atualizado com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def delete_record(self):
        """Exclui pagamento"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento para excluir.")
            return

        item = self.tree.item(selected[0])
        cod_pag = item['values'][0]

        # Verificar se está sendo usado em campanhas
        query_camp = """
                     SELECT COUNT(*) \
                     FROM Campanha_Dados \
                     WHERE Cod_pagamento = :cod \
                     """
        result_camp = self.db.execute_query(query_camp, {'cod': cod_pag})

        if result_camp and result_camp[1] and result_camp[1][0][0] > 0:
            num_campanhas = result_camp[1][0][0]
            messagebox.showerror(
                "Impossível Excluir",
                f"Este pagamento está associado a {num_campanhas} campanha(s).\n\n"
                "Remova as associações antes de excluir."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o pagamento #{cod_pag}?\n\n"
            "Esta ação não pode ser desfeita!"
        )

        if confirm:
            try:
                query = "DELETE FROM Pagamentos WHERE Cod_pagamento = :cod"
                result = self.db.execute_query(query, {'cod': cod_pag}, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Pagamento excluído com sucesso!")
                    self.load_data()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    def show_financial_report(self):
        """Mostra relatório financeiro"""
        # Criar janela
        report_window = ctk.CTkToplevel(self.parent)
        report_window.title("Relatório Financeiro")
        report_window.geometry("900x700")

        # Centralizar
        report_window.update_idletasks()
        x = (report_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (report_window.winfo_screenheight() // 2) - (700 // 2)
        report_window.geometry(f"900x700+{x}+{y}")

        # Container
        container = ctk.CTkScrollableFrame(report_window, fg_color="#2b2b2b")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            container,
            text="💰 Relatório Financeiro Consolidado",
            font=("Helvetica", 22, "bold"),
            text_color=self.COLORS['primary']
        )
        title.pack(pady=(0, 30))

        # Buscar estatísticas
        # Total de pagamentos
        query_total = "SELECT COUNT(*), SUM(Precos_dinam) FROM Pagamentos"
        result_total = self.db.execute_query(query_total)

        total_pag = 0
        total_valor = 0
        if result_total and result_total[1]:
            total_pag = result_total[1][0][0] or 0
            total_valor = result_total[1][0][1] or 0

        # Por modalidade
        query_modal = """
                      SELECT mc.Modal_cobranca, COUNT(*), SUM(p.Precos_dinam)
                      FROM Pagamentos p
                               JOIN Modalidade_Cobranca mc ON p.Cod_modalidade = mc.Cod_modalidade
                      GROUP BY mc.Modal_cobranca
                      ORDER BY SUM(p.Precos_dinam) DESC \
                      """
        result_modal = self.db.execute_query(query_modal)

        # Por método
        query_metodo = """
                       SELECT Metod_pagamento, COUNT(*), SUM(Precos_dinam)
                       FROM Pagamentos
                       GROUP BY Metod_pagamento
                       ORDER BY SUM(Precos_dinam) DESC \
                       """
        result_metodo = self.db.execute_query(query_metodo)

        # Descontos totais
        query_desc = """
                     SELECT SUM(p.Precos_dinam * pr.Desc_volume / 100)
                     FROM Pagamentos p
                              JOIN Promocoes pr ON p.Cod_promocao = pr.Cod_promocao
                     WHERE p.Cod_promocao IS NOT NULL \
                     """
        result_desc = self.db.execute_query(query_desc)
        total_desconto = result_desc[1][0][0] if result_desc and result_desc[1] and result_desc[1][0][0] else 0

        # Cards resumo
        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack(fill="x", pady=20)

        cards_data = [
            ("💳 Total Pagamentos", str(total_pag), self.COLORS['primary']),
            ("💰 Receita Total", f"{total_valor:,.2f} MT", self.COLORS['success']),
            ("🎁 Descontos", f"{total_desconto:,.2f} MT", self.COLORS['secondary']),
            ("✅ Receita Líquida", f"{(total_valor - total_desconto):,.2f} MT", self.COLORS['accent'])
        ]

        for i, (title_text, value, color) in enumerate(cards_data):
            card = self.create_stat_card(cards_frame, title_text, value, color)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            cards_frame.grid_columnconfigure(i, weight=1)

        # Por Modalidade
        if result_modal and result_modal[1]:
            modal_frame = ctk.CTkFrame(container, fg_color=self.COLORS['dark'])
            modal_frame.pack(fill="x", pady=15)

            modal_title = ctk.CTkLabel(
                modal_frame,
                text="📊 Receita por Modalidade de Cobrança",
                font=("Helvetica", 16, "bold"),
                text_color=self.COLORS['text']
            )
            modal_title.pack(pady=15)

            # Tabela
            tree_frame = ctk.CTkFrame(modal_frame, fg_color="transparent")
            tree_frame.pack(fill="x", padx=20, pady=(0, 20))

            columns = ('Modalidade', 'Quantidade', 'Valor Total', 'Percentual')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=5)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=200, anchor="center")

            for row in result_modal[1]:
                modalidade = row[0]
                qtd = row[1]
                valor = row[2]
                percentual = (valor / total_valor * 100) if total_valor > 0 else 0

                tree.insert('', 'end', values=(
                    modalidade,
                    qtd,
                    f"{valor:,.2f} MT",
                    f"{percentual:.1f}%"
                ))

            tree.pack(fill="x")

        # Por Método
        if result_metodo and result_metodo[1]:
            metodo_frame = ctk.CTkFrame(container, fg_color=self.COLORS['dark'])
            metodo_frame.pack(fill="x", pady=15)

            metodo_title = ctk.CTkLabel(
                metodo_frame,
                text="💳 Receita por Método de Pagamento",
                font=("Helvetica", 16, "bold"),
                text_color=self.COLORS['text']
            )
            metodo_title.pack(pady=15)

            # Tabela
            tree_frame = ctk.CTkFrame(metodo_frame, fg_color="transparent")
            tree_frame.pack(fill="x", padx=20, pady=(0, 20))

            columns = ('Método', 'Quantidade', 'Valor Total', 'Percentual')
            tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=5)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=200, anchor="center")

            for row in result_metodo[1]:
                metodo = row[0]
                qtd = row[1]
                valor = row[2]
                percentual = (valor / total_valor * 100) if total_valor > 0 else 0

                tree.insert('', 'end', values=(
                    metodo,
                    qtd,
                    f"{valor:,.2f} MT",
                    f"{percentual:.1f}%"
                ))

            tree.pack(fill="x")

        # Botão fechar
        close_btn = ctk.CTkButton(
            container,
            text="✖️ Fechar",
            command=report_window.destroy,
            font=("Helvetica", 14, "bold"),
            fg_color=self.COLORS['secondary'],
            width=150,
            height=40
        )
        close_btn.pack(pady=30)

    def create_stat_card(self, parent, title, value, color):
        """Cria card de estatística"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=110)
        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Helvetica", 13),
            text_color=self.COLORS['text']
        )
        title_label.pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=("Helvetica", 20, "bold"),
            text_color=self.COLORS['text']
        )
        value_label.pack()

        return card

    def darken_color(self, color):
        """Escurece cor"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb


def show_pagamentos_module(parent, db, main_app):
    """Função de integração"""
    PagamentosCRUD(parent, db, main_app)