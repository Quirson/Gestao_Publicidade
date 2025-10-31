"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD PAGAMENTOS - MESMA INTERFACE DO DASHBOARD                       ║
║  Sistema de Gestão de Publicidade e Marketing                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime
from tkcalendar import DateEntry
import re

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

class PagamentosCRUD:
    def __init__(self, parent, db, main_app):
        self.parent = parent
        self.db = db
        self.main_app = main_app
        self.selected_item = None

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
            text="💳 Gestão de Pagamentos",
            font=("Arial", 22, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Barra de ferramentas - MESMO ESTILO
        self.create_toolbar(container)

        # Tabela - MESMO LAYOUT E DIMENSÕES DO DASHBOARD
        self.create_pagamentos_table(container)

    def create_toolbar(self, parent):
        """Barra de ferramentas igual ao Dashboard"""
        toolbar = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'],
                              corner_radius=10, height=70)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(expand=True, padx=20, pady=12)

        buttons = [
            ("➕ Novo Pagamento", self.open_create_form, COLORS['success']),
            ("✏️ Editar", self.open_edit_form, COLORS['primary']),
            ("🗑️ Excluir", self.delete_record, COLORS['danger']),
            ("🔄 Atualizar", self.load_data, COLORS['accent']),
            ("📊 Relatório", self.show_financial_report, COLORS['info'])
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

    def create_pagamentos_table(self, parent):
        """Tabela COM MESMO LAYOUT E DIMENSÕES do Dashboard"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12)
        table_frame.pack(fill="both", expand=True, pady=10)

        # Cabeçalho - MESMO ESTILO
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame,
            text="📋 Lista de Pagamentos",
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
        columns = ('Código', 'Modalidade', 'Valor', 'Desconto', 'Valor Final', 'Método', 'Status')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)

        # MESMAS LARGURAS DE COLUNA
        widths = [100, 150, 120, 100, 120, 150, 100]
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
        self.tree.bind('<Double-1>', lambda e: self.open_edit_form())

    def load_data(self):
        """Carrega dados - MESMA LÓGICA DO DASHBOARD"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
        SELECT 
            p.Cod_pagamento,
            mc.Modal_cobranca,
            p.Precos_dinam,
            pr.Desc_volume,
            p.Metod_pagamento,
            p.Reconc_financ
        FROM Pagamentos p
        JOIN Modalidade_Cobranca mc ON p.Cod_modalidade = mc.Cod_modalidade
        LEFT JOIN Promocoes pr ON p.Cod_promocao = pr.Cod_promocao
        ORDER BY p.Cod_pagamento DESC
        """

        result = self.db.execute_query(query)

        if result and result[1]:
            self.all_data = result[1]
            for row in result[1]:
                cod = row[0]
                modalidade = row[1]
                valor = row[2]
                desconto = row[3] if row[3] else 0
                valor_final = valor * (1 - desconto / 100)
                metodo = row[4]
                reconc = row[5]

                # Determinar status pela reconciliação
                status = "🟢 Concluído" if reconc and "concluído" in reconc.lower() else "🟡 Pendente"

                # FORMATAÇÃO IDÊNTICA AO DASHBOARD
                self.tree.insert('', 'end', values=(
                    cod,
                    modalidade,
                    f"MT {valor:,.2f}",
                    f"{desconto}%",
                    f"MT {valor_final:,.2f}",
                    metodo,
                    status
                ))

        else:
            messagebox.showinfo("Info", "Nenhum pagamento encontrado.")

    def clear_content(self):
        """Limpa conteúdo - MESMA FUNÇÃO DO MAIN"""
        for widget in self.parent.winfo_children():
            widget.destroy()

    # =============================================================================
    # FUNÇÕES ESPECÍFICAS DO CRUD (MANTIDAS COM MELHORIAS VISUAIS)
    # =============================================================================

    def open_create_form(self):
        """Abre formulário para criar novo pagamento"""
        self.open_form(mode='create')

    def open_edit_form(self):
        """Abre formulário para editar pagamento selecionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento para editar.")
            return

        item = self.tree.item(selected[0])
        cod_pag = item['values'][0]
        self.open_form(mode='edit', cod_pag=cod_pag)

    def open_form(self, mode='create', cod_pag=None):
        """Abre formulário (criar ou editar)"""
        # Criar janela modal
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Novo Pagamento" if mode == 'create' else "Editar Pagamento")
        self.form_window.geometry("800x650")

        # Centralizar
        self.form_window.update_idletasks()
        x = (self.form_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.form_window.winfo_screenheight() // 2) - (650 // 2)
        self.form_window.geometry(f"800x650+{x}+{y}")

        # Tornar modal
        self.form_window.transient(self.parent)
        self.form_window.grab_set()

        # Container com scroll
        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color=COLORS['dark_bg'])
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_text = "💳 Novo Pagamento" if mode == 'create' else "✏️ Editar Pagamento"
        title = ctk.CTkLabel(
            form_container,
            text=title_text,
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        )
        title.pack(pady=(0, 20))

        # Frame do formulário
        form_frame = ctk.CTkFrame(form_container, fg_color=COLORS['dark_card'],
                                  corner_radius=10)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Campos do formulário
        fields = {}
        row = 0

        # Código (apenas visualização em modo edição)
        if mode == 'edit':
            self.create_form_field(form_frame, "Código:", row, readonly=True,
                                   var_name='cod_pag', fields=fields)
            row += 1

        # Modalidade de Cobrança
        label = ctk.CTkLabel(form_frame, text="Modalidade Cobrança:*",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
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
        self.create_form_field(form_frame, "Valor (MT):*", row, width=200,
                               var_name='preco', fields=fields)
        row += 1

        # Promoção
        label = ctk.CTkLabel(form_frame, text="Promoção:",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
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
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['success'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['valor_final'] = ctk.CTkLabel(
            form_frame,
            text="0.00 MT",
            font=("Arial", 16, "bold"),
            text_color=COLORS['success']
        )
        fields['valor_final'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Método de Pagamento
        label = ctk.CTkLabel(form_frame, text="Método Pagamento:*",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
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
        self.create_form_field(form_frame, "Comprovante:", row, width=400,
                               var_name='comprovante', fields=fields)
        row += 1

        # Reconciliação Financeira
        self.create_form_field(form_frame, "Reconciliação:", row, width=400,
                               var_name='reconciliacao', fields=fields)
        row += 1

        # Botões
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=lambda: self.save_record(mode, fields, cod_pag),
            font=("Arial", 14, "bold"),
            fg_color=COLORS['success'],
            width=150,
            height=40
        )
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.form_window.destroy,
            font=("Arial", 14, "bold"),
            fg_color=COLORS['danger'],
            width=150,
            height=40
        )
        cancel_btn.pack(side="left", padx=10)

        # Carregar dados se modo edição
        if mode == 'edit' and cod_pag:
            self.load_form_data(fields, cod_pag)

        # Vincular evento de mudança no preço
        fields['preco'].bind('<KeyRelease>', lambda e: self.update_final_value(fields))

        self.form_fields = fields

    def create_form_field(self, parent, label_text, row, width=300, readonly=False,
                          var_name=None, fields=None):
        """Cria um campo de formulário"""
        label = ctk.CTkLabel(parent, text=label_text,
                            font=("Arial", 12, "bold"),
                            text_color=COLORS['text_primary'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        if readonly:
            entry.configure(state="disabled")

        if fields is not None and var_name:
            fields[var_name] = entry

    def get_modalidades_for_combo(self):
        """Retorna lista formatada de modalidades para combobox"""
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
            fields['valor_final'].configure(text=f"MT {valor_final:,.2f}")

        except:
            fields['valor_final'].configure(text="MT 0.00")

    def load_form_data(self, fields, cod_pag):
        """Carrega dados no formulário para edição"""
        query = """
        SELECT p.Cod_pagamento, p.Cod_modalidade, mc.Modal_cobranca, p.Precos_dinam,
               p.Cod_promocao, pr.Pacotes_promo, pr.Desc_volume, p.Metod_pagamento,
               p.Comprov_veic, p.Reconc_financ
        FROM Pagamentos p
        JOIN Modalidade_Cobranca mc ON p.Cod_modalidade = mc.Cod_modalidade
        LEFT JOIN Promocoes pr ON p.Cod_promocao = pr.Cod_promocao
        WHERE p.Cod_pagamento = :cod
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
        """Salva registro (criar ou atualizar)"""
        try:
            # Validar campos obrigatórios
            modalidade = fields['modalidade'].get()
            if not modalidade or modalidade == "Nenhuma modalidade cadastrada":
                messagebox.showerror("Erro", "Selecione uma modalidade.")
                return

            # Extrair ID da modalidade
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
                messagebox.showerror("Erro", "Valor inválido. Use apenas números.")
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
                VALUES (:cod, :modal, :preco, :promo, :metodo, :comprov, :reconc)
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
                SET Cod_modalidade = :modal,
                    Precos_dinam = :preco,
                    Cod_promocao = :promo,
                    Metod_pagamento = :metodo,
                    Comprov_veic = :comprov,
                    Reconc_financ = :reconc
                WHERE Cod_pagamento = :cod
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
        """Exclui pagamento selecionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um pagamento para excluir.")
            return

        item = self.tree.item(selected[0])
        cod_pag = item['values'][0]

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
        """Mostra relatório financeiro - COM MESMA ESTÉTICA DO DASHBOARD"""
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
        container = ctk.CTkScrollableFrame(report_window, fg_color=COLORS['dark_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título - MESMO ESTILO
        title = ctk.CTkLabel(
            container,
            text="💰 Relatório Financeiro Consolidado",
            font=("Arial", 22, "bold"),
            text_color=COLORS['text_primary']
        )
        title.pack(pady=(0, 30))

        # Buscar estatísticas
        stats_data = self._get_financial_stats()

        # Cards resumo - MESMO ESTILO DO DASHBOARD
        stats_frame = ctk.CTkFrame(container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 30))

        cards_info = [
            ("💳", "Total Pagamentos", str(stats_data['total_pagamentos']), COLORS['primary']),
            ("💰", "Receita Total", f"MT {stats_data['receita_total']:,.2f}", COLORS['success']),
            ("🎁", "Descontos", f"MT {stats_data['total_descontos']:,.2f}", COLORS['warning']),
            ("✅", "Receita Líquida", f"MT {stats_data['receita_liquida']:,.2f}", COLORS['accent'])
        ]

        for i, (icon, title_text, value, color) in enumerate(cards_info):
            card = self.create_stat_card(stats_frame, title_text, value, icon, color, width=200, height=110)
            card.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")
            stats_frame.grid_columnconfigure(i, weight=1)

        # Tabelas de detalhes
        if stats_data['por_modalidade']:
            self._create_detailed_table(container, "📊 Receita por Modalidade",
                                      stats_data['por_modalidade'],
                                      ['Modalidade', 'Quantidade', 'Valor Total', 'Percentual'])

        if stats_data['por_metodo']:
            self._create_detailed_table(container, "💳 Receita por Método",
                                      stats_data['por_metodo'],
                                      ['Método', 'Quantidade', 'Valor Total', 'Percentual'])

        # Botão fechar
        close_btn = ctk.CTkButton(
            container,
            text="✖️ Fechar",
            command=report_window.destroy,
            font=("Arial", 14, "bold"),
            fg_color=COLORS['secondary'],
            width=150,
            height=40
        )
        close_btn.pack(pady=30)

    def _get_financial_stats(self):
        """Busca estatísticas financeiras"""
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
        ORDER BY SUM(p.Precos_dinam) DESC
        """
        result_modal = self.db.execute_query(query_modal)

        # Por método
        query_metodo = """
        SELECT Metod_pagamento, COUNT(*), SUM(Precos_dinam)
        FROM Pagamentos
        GROUP BY Metod_pagamento
        ORDER BY SUM(Precos_dinam) DESC
        """
        result_metodo = self.db.execute_query(query_metodo)

        # Descontos totais
        query_desc = """
        SELECT SUM(p.Precos_dinam * pr.Desc_volume / 100)
        FROM Pagamentos p
        JOIN Promocoes pr ON p.Cod_promocao = pr.Cod_promocao
        WHERE p.Cod_promocao IS NOT NULL
        """
        result_desc = self.db.execute_query(query_desc)
        total_desconto = result_desc[1][0][0] if result_desc and result_desc[1] and result_desc[1][0][0] else 0

        return {
            'total_pagamentos': total_pag,
            'receita_total': total_valor,
            'total_descontos': total_desconto,
            'receita_liquida': total_valor - total_desconto,
            'por_modalidade': result_modal[1] if result_modal and result_modal[1] else [],
            'por_metodo': result_metodo[1] if result_metodo and result_metodo[1] else []
        }

    def _create_detailed_table(self, parent, title, data, columns):
        """Cria tabela detalhada no relatório"""
        frame = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12)
        frame.pack(fill="x", pady=15)

        # Título
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 16, "bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=15)

        # Tabela
        table_container = ctk.CTkFrame(frame, fg_color="transparent")
        table_container.pack(fill="x", padx=20, pady=(0, 20))

        # Criar treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Report.Treeview",
                        background=COLORS['dark_card'],
                        foreground=COLORS['text_primary'],
                        fieldbackground=COLORS['dark_card'],
                        rowheight=30)
        style.configure("Report.Treeview.Heading",
                        background=COLORS['primary'],
                        foreground=COLORS['text_primary'],
                        font=("Arial", 10, "bold"))

        tree = ttk.Treeview(table_container, columns=columns, show='headings',
                           height=min(6, len(data)), style="Report.Treeview")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="center")

        # Adicionar dados
        total_valor = sum(row[2] for row in data) if data else 0
        for row in data:
            percentual = (row[2] / total_valor * 100) if total_valor > 0 else 0
            tree.insert('', 'end', values=(
                row[0],
                row[1],
                f"MT {row[2]:,.2f}",
                f"{percentual:.1f}%"
            ))

        tree.pack(fill="x")

    def create_stat_card(self, parent, title, value, icon, color, **kwargs):
        """Cria card de estatística NO ESTILO DO DASHBOARD"""
        card = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12,
                           border_width=1, border_color=COLORS['dark_border'], **kwargs)
        card.grid_columnconfigure(0, weight=1)

        # Ícone e título
        icon_frame = ctk.CTkFrame(card, fg_color="transparent")
        icon_frame.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        ctk.CTkLabel(icon_frame, text=icon, font=("Arial", 20), text_color=color).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(icon_frame, text=title, font=("Arial", 12), text_color=COLORS['text_secondary']).pack(side="left")

        # Valor
        value_label = ctk.CTkLabel(card, text=value, font=("Arial", 20, "bold"),
                                 text_color=COLORS['text_primary'])
        value_label.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))

        return card

    def darken_color(self, color):
        """Escurece uma cor hexadecimal"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb


# ═════════════════════════════════════════════════════════════════════════════
# FUNÇÃO PARA INTEGRAR NO MAIN APP
# ═════════════════════════════════════════════════════════════════════════════

def show_pagamentos_module(parent, db, main_app):
    """Função para chamar no menu principal"""
    PagamentosCRUD(parent, db, main_app)