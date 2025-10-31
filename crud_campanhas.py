"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  MÓDULO CRUD CAMPANHAS - MESMA INTERFACE DO DASHBOARD                        ║
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

class CampanhasCRUD:
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
            text="📢 Gestão de Campanhas",
            font=("Arial", 22, "bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")

        # Barra de ferramentas - MESMO ESTILO
        self.create_toolbar(container)

        # Tabela - MESMO LAYOUT E DIMENSÕES DO DASHBOARD
        self.create_campaigns_table(container)

    def create_toolbar(self, parent):
        """Barra de ferramentas igual ao Dashboard"""
        toolbar = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'],
                              corner_radius=10, height=70)
        toolbar.pack(fill="x", pady=(0, 20))
        toolbar.pack_propagate(False)

        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(expand=True, padx=20, pady=12)

        buttons = [
            ("➕ Nova Campanha", self.open_create_form, COLORS['success']),
            ("✏️ Editar", self.open_edit_form, COLORS['primary']),
            ("🗑️ Excluir", self.delete_record, COLORS['danger']),
            ("🔄 Atualizar", self.load_data, COLORS['accent']),
            ("📊 Detalhes", self.show_details, COLORS['info'])
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

    def create_campaigns_table(self, parent):
        """Tabela COM MESMO LAYOUT E DIMENSÕES do Dashboard"""
        table_frame = ctk.CTkFrame(parent, fg_color=COLORS['dark_card'], corner_radius=12)
        table_frame.pack(fill="both", expand=True, pady=10)

        # Cabeçalho - MESMO ESTILO
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame,
            text="📋 Lista de Campanhas",
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
        columns = ('Código', 'Campanha', 'Anunciante', 'Orçamento', 'Início', 'Término', 'Status')
        self.tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)  # MESMA ALTURA

        # MESMAS LARGURAS DE COLUNA
        widths = [80, 200, 150, 120, 100, 100, 100]
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
            self.all_data = result[1]
            for row in result[1]:
                # FORMATAÇÃO IDÊNTICA AO DASHBOARD
                cod = row[0]
                titulo = row[1]
                anunciante = row[2]
                orcamento = f"MT {row[3]:,.0f}"  # MESMA FORMATAÇÃO
                data_inicio = row[4].strftime('%d/%m/%Y') if row[4] else ''
                data_termino = row[5].strftime('%d/%m/%Y') if row[5] else ''
                status = row[6]

                # MESMAS CORES DE STATUS
                tag = status.lower()
                self.tree.insert('', 'end', values=(
                    cod, titulo, anunciante, orcamento,
                    data_inicio, data_termino, status
                ), tags=(tag,))

            # CONFIGURAR CORES - MESMAS DO DASHBOARD
            self.tree.tag_configure('ativa', foreground='#28a745')
            self.tree.tag_configure('agendada', foreground='#ffc107')
            self.tree.tag_configure('finalizada', foreground='#dc3545')
        else:
            messagebox.showinfo("Info", "Nenhuma campanha encontrada.")

    def clear_content(self):
        """Limpa conteúdo - MESMA FUNÇÃO DO MAIN"""
        for widget in self.parent.winfo_children():
            widget.destroy()

    # =============================================================================
    # FUNÇÕES ESPECÍFICAS DO CRUD (MANTIDAS)
    # =============================================================================

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
        form_container = ctk.CTkScrollableFrame(self.form_window, fg_color=COLORS['dark_bg'])
        form_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_text = "📝 Nova Campanha" if mode == 'create' else "✏️ Editar Campanha"
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
                                   var_name='cod_camp', fields=fields)
            row += 1

        # Anunciante
        label = ctk.CTkLabel(form_frame, text="Anunciante:*",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
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
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
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
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
        label.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        fields['data_inicio'] = DateEntry(form_frame, width=25, background='darkblue',
                                          foreground='white', borderwidth=2,
                                          date_pattern='dd/mm/yyyy')
        fields['data_inicio'].grid(row=row, column=1, padx=20, pady=10, sticky="w")
        row += 1

        label = ctk.CTkLabel(form_frame, text="Data Término:*",
                             font=("Arial", 12, "bold"),
                             text_color=COLORS['text_primary'])
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
        if mode == 'edit' and cod_camp:
            self.load_form_data(fields, cod_camp)

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
        container = ctk.CTkScrollableFrame(details_window, fg_color=COLORS['dark_bg'])
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(
            container,
            text=f"📊 {data[1]}",
            font=("Arial", 22, "bold"),
            text_color=COLORS['primary']
        )
        title.pack(pady=(0, 20))

        # Status badge
        status_color = {
            'Ativa': COLORS['success'],
            'Agendada': COLORS['warning'],
            'Finalizada': COLORS['danger']
        }

        status_badge = ctk.CTkLabel(
            container,
            text=data[11],
            font=("Arial", 14, "bold"),
            fg_color=status_color.get(data[11], COLORS['accent']),
            corner_radius=20,
            padx=20,
            pady=5
        )
        status_badge.pack(pady=(0, 20))

        # Frame de informações
        info_frame = ctk.CTkFrame(container, fg_color=COLORS['dark_card'], corner_radius=10)
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
            font=("Arial", 12, "bold"),
            text_color=COLORS['text_primary']
        )
        obj_label.grid(row=len(info_fields), column=0, padx=20, pady=10, sticky="nw")

        obj_text = ctk.CTkTextbox(info_frame, width=500, height=100)
        obj_text.grid(row=len(info_fields), column=1, padx=20, pady=10, sticky="w")
        obj_text.insert("1.0", data[3] if data[3] else "Não informado")
        obj_text.configure(state="disabled")

        # Botão fechar
        close_btn = ctk.CTkButton(
            container,
            text="✖️ Fechar",
            command=details_window.destroy,
            font=("Arial", 14, "bold"),
            fg_color=COLORS['secondary'],
            width=150,
            height=40
        )
        close_btn.pack(pady=20)

    def create_info_row(self, parent, label, value, row):
        """Cria uma linha de informação"""
        label_widget = ctk.CTkLabel(
            parent,
            text=label,
            font=("Arial", 12, "bold"),
            text_color=COLORS['text_primary']
        )
        label_widget.grid(row=row, column=0, padx=20, pady=10, sticky="w")

        value_widget = ctk.CTkLabel(
            parent,
            text=value,
            font=("Arial", 11),
            text_color=COLORS['text_secondary']
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