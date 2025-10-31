"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD ESPAÇOS PUBLICITÁRIOS - MESMA INTERFACE DO DASHBOARD           ║
║  Sistema de Gestão de Publicidade e Marketing                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
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

class EspacosCRUD:
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
            text="📺 Gestão de Espaços Publicitários",
            font=("Arial", 22, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Barra de ferramentas - MESMO ESTILO
        self.create_toolbar(container)

        # Tabela - MESMO LAYOUT E DIMENSÕES DO DASHBOARD
        self.create_espacos_table(container)

    def create_toolbar(self, parent):
        """Barra de ferramentas igual ao Dashboard"""
        toolbar = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'],
                              corner_radius=10, height=70)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(expand=True, padx=20, pady=12)

        buttons = [
            ("➕ Novo Espaço", self.open_create_form, COLORS['success']),
            ("✏️ Editar", self.open_edit_form, COLORS['primary']),
            ("🗑️ Excluir", self.delete_record, COLORS['danger']),
            ("🔄 Atualizar", self.load_data, COLORS['accent']),
            ("📊 Estatísticas", self.show_statistics, COLORS['info'])
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

    def create_espacos_table(self, parent):
        """Tabela COM MESMO LAYOUT E DIMENSÕES do Dashboard"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12)
        table_frame.pack(fill="both", expand=True, pady=10)

        # Cabeçalho - MESMO ESTILO
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame,
            text="📋 Lista de Espaços Publicitários",
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
        columns = ('ID', 'Localização', 'Tipo', 'Dimensões', 'Preço Base', 'Disponibilidade', 'Proprietário')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)  # MESMA ALTURA

        # MESMAS LARGURAS DE COLUNA
        widths = [80, 220, 150, 120, 120, 140, 180]
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
        SELECT Id_espaco, Local_fis_dig, Tipo, Dimensoes, Preco_base, 
               Disponibilidade, Proprietario
        FROM Espaco_Dados
        ORDER BY Local_fis_dig
        """

        result = self.db.execute_query(query)

        if result and result[1]:
            self.all_data = result[1]
            for row in result[1]:
                # FORMATAÇÃO CONSISTENTE
                id_espaco = row[0]
                local = row[1]
                tipo = row[2]
                dimensoes = row[3]
                preco = f"MT {row[4]:,.2f}"
                disponib = row[5]
                proprietario = row[6]

                # Tag de cor por disponibilidade
                tag = disponib.lower().replace(' ', '_')
                self.tree.insert('', 'end', values=(
                    id_espaco, local, tipo, dimensoes, preco, disponib, proprietario
                ), tags=(tag,))

            # CONFIGURAR CORES - MESMAS DO DASHBOARD
            self.tree.tag_configure('disponível', foreground='#28a745')
            self.tree.tag_configure('sempre_disponível', foreground='#5cb85c')
            self.tree.tag_configure('ocupado', foreground='#dc3545')
            self.tree.tag_configure('manutenção', foreground='#ffc107')
        else:
            messagebox.showinfo("Info", "Nenhum espaço encontrado.")

    def clear_content(self):
        """Limpa conteúdo - MESMA FUNÇÃO DO MAIN"""
        for widget in self.parent.winfo_children():
            widget.destroy()

    # =============================================================================
    # FUNÇÕES ESPECÍFICAS DO CRUD (MANTIDAS COM PEQUENOS AJUSTES)
    # =============================================================================

    def open_create_form(self):
        """Formulário de criação"""
        self.open_form(mode='create')

    def open_edit_form(self):
        """Formulário de edição"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um espaço para editar.")
            return

        item = self.tree.item(selected[0])
        id_espaco = item['values'][0]
        self.open_form(mode='edit', id_espaco=id_espaco)

    def open_form(self, mode='create', id_espaco=None):
        """Abre formulário"""
        self.form_window = ctk.CTkToplevel(self.parent)
        self.form_window.title("Novo Espaço" if mode == 'create' else "Editar Espaço")
        self.form_window.geometry("850x700")

        # Centralizar
        self.form_window.update_idletasks()
        x = (self.form_window.winfo_screenwidth() // 2) - (850 // 2)
        y = (self.form_window.winfo_screenheight() // 2) - (700 // 2)
        self.form_window.geometry(f"850x700+{x}+{y}")

        self.form_window.transient(self.parent)
        self.form_window.grab_set()

        # Container com scroll - MESMO ESTILO
        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color=COLORS['dark_bg'])
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_text = "📝 Novo Espaço Publicitário" if mode == 'create' else "✏️ Editar Espaço"
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

        fields = {}
        row = 0

        # ID (apenas visualização em edição)
        if mode == 'edit':
            self.create_field(form_frame, "ID Espaço:", row, fields, 'id_espaco',
                              readonly=True, width=150)
            row += 1

        # Localização Física/Digital
        self.create_field(form_frame, "Localização:*", row, fields, 'local', width=500)
        row += 1

        # Tipo
        self.create_field(form_frame, "Tipo:*", row, fields, 'tipo', width=400)
        row += 1

        # Dimensões
        self.create_field(form_frame, "Dimensões:*", row, fields, 'dimensoes', width=250)
        row += 1

        # Resolução
        self.create_field(form_frame, "Resolução:", row, fields, 'resolucao', width=200)
        row += 1

        # Visibilidade
        self.create_field(form_frame, "Visibilidade:*", row, fields, 'visibilidade', width=400)
        row += 1

        # Horário de Maior Fluxo
        self.create_field(form_frame, "Horário Maior Fluxo:", row, fields, 'horario', width=300)
        row += 1

        # Preço Base
        self.create_field(form_frame, "Preço Base (MT):*", row, fields, 'preco', width=200)
        row += 1

        # Disponibilidade
        label = ctk.CTkLabel(form_frame, text="Disponibilidade:*",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['disponibilidade'] = ctk.CTkComboBox(
            form_frame,
            values=["Disponível", "Ocupado", "Manutenção", "Sempre Disponível"],
            width=250,
            height=35
        )
        fields['disponibilidade'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Proprietário
        self.create_field(form_frame, "Proprietário:*", row, fields, 'proprietario', width=400)
        row += 1

        # Histórico de Ocupação (Textbox)
        label = ctk.CTkLabel(form_frame, text="Histórico Ocupação:",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="nw")

        fields['historico'] = ctk.CTkTextbox(form_frame, width=500, height=80)
        fields['historico'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        # Botões - MESMO ESTILO
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=30)

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar",
            command=lambda: self.save_record(mode, fields, id_espaco),
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

        # Carregar dados se edição
        if mode == 'edit' and id_espaco:
            self.load_form_data(fields, id_espaco)

        self.form_fields = fields

    def create_field(self, parent, label_text, row, fields, field_name,
                     width=300, readonly=False):
        """Cria campo do formulário"""
        label = ctk.CTkLabel(parent, text=label_text,
                            font=("Arial", 12, "bold"),
                            text_color=COLORS['text_primary'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        entry = ctk.CTkEntry(parent, width=width, height=35)
        entry.grid(row=row, column=1, padx=20, pady=10, sticky="w")

        if readonly:
            entry.configure(state="disabled")

        fields[field_name] = entry

    def load_form_data(self, fields, id_espaco):
        """Carrega dados no formulário"""
        query = """
        SELECT Id_espaco, Local_fis_dig, Tipo, Dimensoes, Resolucao,
               Visibilidade, Horario_maior, Preco_base, Disponibilidade,
               Proprietario, Historico_ocup
        FROM Espaco_Dados
        WHERE Id_espaco = :id
        """
        result = self.db.execute_query(query, {'id': id_espaco})

        if result and result[1]:
            data = result[1][0]

            fields['id_espaco'].configure(state="normal")
            fields['id_espaco'].insert(0, str(data[0]))
            fields['id_espaco'].configure(state="disabled")

            fields['local'].insert(0, data[1])
            fields['tipo'].insert(0, data[2])
            fields['dimensoes'].insert(0, data[3])
            if data[4]:
                fields['resolucao'].insert(0, data[4])
            fields['visibilidade'].insert(0, data[5])
            if data[6]:
                fields['horario'].insert(0, data[6])
            fields['preco'].insert(0, str(data[7]))
            fields['disponibilidade'].set(data[8])
            fields['proprietario'].insert(0, data[9])
            if data[10]:
                fields['historico'].insert("1.0", data[10])

    def save_record(self, mode, fields, id_espaco=None):
        """Salva registro"""
        try:
            local = fields['local'].get().strip()
            tipo = fields['tipo'].get().strip()
            dimensoes = fields['dimensoes'].get().strip()
            resolucao = fields['resolucao'].get().strip()
            visibilidade = fields['visibilidade'].get().strip()
            horario = fields['horario'].get().strip()
            preco = fields['preco'].get().strip()
            disponibilidade = fields['disponibilidade'].get()
            proprietario = fields['proprietario'].get().strip()
            historico = fields['historico'].get("1.0", "end-1c").strip()

            if not all([local, tipo, dimensoes, visibilidade, preco, disponibilidade, proprietario]):
                messagebox.showerror("Erro", "Preencha todos os campos obrigatórios (*).")
                return

            # Validar preço
            try:
                preco = float(preco)
                if preco <= 0:
                    raise ValueError
            except:
                messagebox.showerror("Erro", "Preço inválido.")
                return

            if mode == 'create':
                # Gerar novo ID
                query_max = "SELECT NVL(MAX(Id_espaco), 3000000) + 1 FROM Espaco_Dados"
                result = self.db.execute_query(query_max)
                novo_id = result[1][0][0] if result and result[1] else 3000001

                # Insert
                query = """
                INSERT INTO Espaco_Dados
                (Id_espaco, Local_fis_dig, Tipo, Dimensoes, Resolucao, Visibilidade,
                 Horario_maior, Preco_base, Disponibilidade, Proprietario, Historico_ocup)
                VALUES (:id, :local, :tipo, :dim, :resol, :vis, :hor, :preco, :disp, :prop, :hist)
                """

                params = {
                    'id': novo_id,
                    'local': local,
                    'tipo': tipo,
                    'dim': dimensoes,
                    'resol': resolucao if resolucao else None,
                    'vis': visibilidade,
                    'hor': horario if horario else None,
                    'preco': preco,
                    'disp': disponibilidade,
                    'prop': proprietario,
                    'hist': historico if historico else None
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Espaço cadastrado com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

            else:  # edit
                query = """
                UPDATE Espaco_Dados
                SET Local_fis_dig = :local,
                    Tipo = :tipo,
                    Dimensoes = :dim,
                    Resolucao = :resol,
                    Visibilidade = :vis,
                    Horario_maior = :hor,
                    Preco_base = :preco,
                    Disponibilidade = :disp,
                    Proprietario = :prop,
                    Historico_ocup = :hist
                WHERE Id_espaco = :id
                """

                params = {
                    'id': id_espaco,
                    'local': local,
                    'tipo': tipo,
                    'dim': dimensoes,
                    'resol': resolucao if resolucao else None,
                    'vis': visibilidade,
                    'hor': horario if horario else None,
                    'preco': preco,
                    'disp': disponibilidade,
                    'prop': proprietario,
                    'hist': historico if historico else None
                }

                result = self.db.execute_query(query, params, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Espaço atualizado com sucesso!")
                    self.form_window.destroy()
                    self.load_data()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")

    def delete_record(self):
        """Exclui espaço"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um espaço para excluir.")
            return

        item = self.tree.item(selected[0])
        id_espaco = item['values'][0]
        local = item['values'][1]

        # Verificar uso em campanhas
        query_camp = "SELECT COUNT(*) FROM Campanha_Espaco WHERE Id_espaco = :id"
        result_camp = self.db.execute_query(query_camp, {'id': id_espaco})

        if result_camp and result_camp[1] and result_camp[1][0][0] > 0:
            num_campanhas = result_camp[1][0][0]
            messagebox.showerror(
                "Impossível Excluir",
                f"Este espaço está sendo usado em {num_campanhas} campanha(s).\n\n"
                "Remova as associações antes de excluir."
            )
            return

        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o espaço:\n\n'{local}'?\n\n"
            "Esta ação não pode ser desfeita!"
        )

        if confirm:
            try:
                # Excluir relacionamento com peças
                query_rel = "DELETE FROM Espaco_Peca WHERE Id_espaco = :id"
                self.db.execute_query(query_rel, {'id': id_espaco}, fetch=False)

                # Excluir espaço
                query = "DELETE FROM Espaco_Dados WHERE Id_espaco = :id"
                result = self.db.execute_query(query, {'id': id_espaco}, fetch=False)

                if result:
                    messagebox.showinfo("Sucesso", "Espaço excluído com sucesso!")
                    self.load_data()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir: {str(e)}")

    def show_statistics(self):
        """Mostra estatísticas dos espaços"""
        # Criar janela
        stats_window = ctk.CTkToplevel(self.parent)
        stats_window.title("Estatísticas de Espaços")
        stats_window.geometry("800x600")

        # Centralizar
        stats_window.update_idletasks()
        x = (stats_window.winfo_screenwidth() // 2) - (800 // 2)
        y = (stats_window.winfo_screenheight() // 2) - (600 // 2)
        stats_window.geometry(f"800x600+{x}+{y}")

        # Container - MESMO ESTILO
        container = ctk.CTkScrollableFrame(stats_window, fg_color=COLORS['dark_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            container,
            text="📊 Estatísticas de Espaços Publicitários",
            font=("Arial", 20, "bold"),
            text_color=COLORS['primary']
        )
        title.pack(pady=(0, 30))

        # Buscar estatísticas
        # Total de espaços
        query_total = "SELECT COUNT(*) FROM Espaco_Dados"
        result_total = self.db.execute_query(query_total)
        total = result_total[1][0][0] if result_total and result_total[1] else 0

        # Por disponibilidade
        query_disp = "SELECT Disponibilidade, COUNT(*) FROM Espaco_Dados GROUP BY Disponibilidade"
        result_disp = self.db.execute_query(query_disp)

        # Por tipo
        query_tipo = "SELECT Tipo, COUNT(*) FROM Espaco_Dados GROUP BY Tipo ORDER BY COUNT(*) DESC"
        result_tipo = self.db.execute_query(query_tipo)

        # Preço médio
        query_preco = "SELECT AVG(Preco_base), MIN(Preco_base), MAX(Preco_base) FROM Espaco_Dados"
        result_preco = self.db.execute_query(query_preco)

        # Cards de estatísticas - MESMO ESTILO
        stats_frame = ctk.CTkFrame(container, fg_color="transparent")
        stats_frame.pack(fill="x", pady=20)

        # Total
        card1 = self.create_stat_card(stats_frame, "📺 Total de Espaços",
                                      str(total), COLORS['primary'])
        card1.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Disponíveis
        disponiveis = 0
        if result_disp and result_disp[1]:
            for row in result_disp[1]:
                if 'Disponível' in row[0]:
                    disponiveis += row[1]

        card2 = self.create_stat_card(stats_frame, "✅ Disponíveis",
                                      str(disponiveis), COLORS['success'])
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Preço médio
        if result_preco and result_preco[1] and result_preco[1][0][0]:
            preco_medio = f"MT {result_preco[1][0][0]:,.2f}"
        else:
            preco_medio = "MT 0.00"

        card3 = self.create_stat_card(stats_frame, "💰 Preço Médio",
                                      preco_medio, COLORS['accent'])
        card3.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)

        # Botão fechar - MESMO ESTILO
        close_btn = ctk.CTkButton(
            container,
            text="✖️ Fechar",
            command=stats_window.destroy,
            font=("Arial", 14, "bold"),
            fg_color=COLORS['secondary'],
            width=150,
            height=40
        )
        close_btn.pack(pady=20)

    def create_stat_card(self, parent, title, value, color):
        """Cria card de estatística"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10, height=100)
        card.grid_propagate(False)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 12),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(15, 5))

        value_label = ctk.CTkLabel(
            card,
            text=str(value),
            font=("Arial", 20, "bold"),
            text_color=COLORS['text_primary']
        )
        value_label.pack()

        return card

    def darken_color(self, color):
        """Escurece cor para efeito hover"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
        darker_rgb = tuple(max(0, c - 30) for c in rgb)
        return '#%02x%02x%02x' % darker_rgb


def show_espacos_module(parent, db, main_app):
    """Função para integrar com main app"""
    EspacosCRUD(parent, db, main_app)