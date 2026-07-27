import sqlite3
from datetime import datetime, timedelta

def conectar():
    return sqlite3.connect("database.db")


# ============ FORNECEDORES ============

def cadastrar_fornecedor():
    conexao = conectar()
    cursor = conexao.cursor()

    print("\n===== CADASTRAR FORNECEDOR =====")
    nome = input("Nome do fornecedor: ")
    telefone = input("Telefone: ")
    email = input("E-mail: ")
    cnpj = input("CNPJ: ")

    cursor.execute("""
        INSERT INTO fornecedores (nome, telefone, email, cnpj)
        VALUES (?, ?, ?, ?)
    """, (nome, telefone, email, cnpj))

    conexao.commit()
    conexao.close()
    print("\n✅ Fornecedor cadastrado com sucesso!\n")


def listar_fornecedores():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM fornecedores")
    fornecedores = cursor.fetchall()

    print("\n===== FORNECEDORES =====")

    if len(fornecedores) == 0:
        print("Nenhum fornecedor cadastrado.")
    else:
        for f in fornecedores:
            print(f"ID: {f[0]}")
            print(f"Nome: {f[1]}")
            print(f"Telefone: {f[2]}")
            print(f"E-mail: {f[3]}")
            print(f"CNPJ: {f[4]}")
            print("-" * 30)

    conexao.close()


def editar_fornecedor():
    conexao = conectar()
    cursor = conexao.cursor()

    listar_fornecedores()
    id_forn = input("\nInforme o ID do fornecedor para editar: ")

    cursor.execute("SELECT * FROM fornecedores WHERE id = ?", (id_forn,))
    forn = cursor.fetchone()

    if forn is None:
        print("\n❌ Fornecedor não encontrado!")
        conexao.close()
        return

    print(f"\nEditando: {forn[1]}")
    print("(Deixe em branco para manter o valor atual)")

    nome = input(f"Nome [{forn[1]}]: ") or forn[1]
    telefone = input(f"Telefone [{forn[2]}]: ") or forn[2]
    email = input(f"E-mail [{forn[3]}]: ") or forn[3]
    cnpj = input(f"CNPJ [{forn[4]}]: ") or forn[4]

    cursor.execute("""
        UPDATE fornecedores SET nome=?, telefone=?, email=?, cnpj=? WHERE id=?
    """, (nome, telefone, email, cnpj, id_forn))

    conexao.commit()
    conexao.close()
    print("\n✅ Fornecedor atualizado com sucesso!\n")


def excluir_fornecedor():
    conexao = conectar()
    cursor = conexao.cursor()

    listar_fornecedores()
    id_forn = input("\nInforme o ID do fornecedor para excluir: ")

    cursor.execute("SELECT nome FROM fornecedores WHERE id = ?", (id_forn,))
    forn = cursor.fetchone()

    if forn is None:
        print("\n❌ Fornecedor não encontrado!")
        conexao.close()
        return

    confirmar = input(f"Tem certeza que deseja excluir '{forn[0]}'? (s/n): ").lower()
    if confirmar == "s":
        cursor.execute("DELETE FROM fornecedores WHERE id = ?", (id_forn,))
        conexao.commit()
        print("\n✅ Fornecedor excluído com sucesso!")
    else:
        print("\n❎ Operação cancelada.")

    conexao.close()


# ============ ESCOLAS ============

def cadastrar_escola():
    conexao = conectar()
    cursor = conexao.cursor()

    print("\n===== CADASTRAR ESCOLA =====")
    nome = input("Nome da escola: ")
    endereco = input("Endereço: ")
    diretor = input("Diretor: ")
    responsavel = input("Responsável pelo recebimento: ")
    telefone = input("Telefone: ")

    cursor.execute("""
        INSERT INTO escolas (nome, endereco, diretor, responsavel, telefone)
        VALUES (?, ?, ?, ?, ?)
    """, (nome, endereco, diretor, responsavel, telefone))

    conexao.commit()
    conexao.close()
    print("\n✅ Escola cadastrada com sucesso!\n")


def listar_escolas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM escolas")
    escolas = cursor.fetchall()

    print("\n===== ESCOLAS =====")

    if len(escolas) == 0:
        print("Nenhuma escola cadastrada.")
    else:
        for e in escolas:
            print(f"ID: {e[0]}")
            print(f"Nome: {e[1]}")
            print(f"Endereço: {e[2]}")
            print(f"Diretor: {e[3]}")
            print(f"Responsável: {e[4]}")
            print(f"Telefone: {e[5]}")
            print("-" * 30)

    conexao.close()


def editar_escola():
    conexao = conectar()
    cursor = conexao.cursor()

    listar_escolas()
    id_esc = input("\nInforme o ID da escola para editar: ")

    cursor.execute("SELECT * FROM escolas WHERE id = ?", (id_esc,))
    esc = cursor.fetchone()

    if esc is None:
        print("\n❌ Escola não encontrada!")
        conexao.close()
        return

    print(f"\nEditando: {esc[1]}")
    print("(Deixe em branco para manter o valor atual)")

    nome = input(f"Nome [{esc[1]}]: ") or esc[1]
    endereco = input(f"Endereço [{esc[2]}]: ") or esc[2]
    diretor = input(f"Diretor [{esc[3]}]: ") or esc[3]
    responsavel = input(f"Responsável [{esc[4]}]: ") or esc[4]
    telefone = input(f"Telefone [{esc[5]}]: ") or esc[5]

    cursor.execute("""
        UPDATE escolas SET nome=?, endereco=?, diretor=?, responsavel=?, telefone=? WHERE id=?
    """, (nome, endereco, diretor, responsavel, telefone, id_esc))

    conexao.commit()
    conexao.close()
    print("\n✅ Escola atualizada com sucesso!\n")


def excluir_escola():
    conexao = conectar()
    cursor = conexao.cursor()

    listar_escolas()
    id_esc = input("\nInforme o ID da escola para excluir: ")

    cursor.execute("SELECT nome FROM escolas WHERE id = ?", (id_esc,))
    esc = cursor.fetchone()

    if esc is None:
        print("\n❌ Escola não encontrada!")
        conexao.close()
        return

    confirmar = input(f"Tem certeza que deseja excluir '{esc[0]}'? (s/n): ").lower()
    if confirmar == "s":
        cursor.execute("DELETE FROM escolas WHERE id = ?", (id_esc,))
        conexao.commit()
        print("\n✅ Escola excluída com sucesso!")
    else:
        print("\n❎ Operação cancelada.")

    conexao.close()


# ============ PRODUTOS ============

def cadastrar_produto():
    conexao = conectar()
    cursor = conexao.cursor()

    print("\n===== CADASTRAR PRODUTO =====")
    nome = input("Nome do produto: ")
    categoria = input("Categoria (ex: Grãos, Laticínios, Hortaliças): ")
    unidade = input("Unidade (kg, litro, pacote, caixa, unidade): ")
    estoque = float(input("Quantidade em estoque: "))
    estoque_minimo = float(input("Estoque mínimo (alerta quando baixar): "))
    validade = input("Validade (DD/MM/AAAA) ou deixe em branco: ")
    lote = input("Lote ou deixe em branco: ")

    cursor.execute("SELECT id, nome FROM fornecedores")
    fornecedores = cursor.fetchall()

    fornecedor_id = None
    if len(fornecedores) > 0:
        print("\nFornecedores cadastrados:")
        for f in fornecedores:
            print(f"  {f[0]} - {f[1]}")
        print("  0 - Sem fornecedor")
        escolha = input("Escolha o ID do fornecedor: ")
        if escolha != "0":
            fornecedor_id = int(escolha)
    else:
        print("\n⚠️ Nenhum fornecedor cadastrado. Cadastre um depois no menu.")

    cursor.execute("""
        INSERT INTO produtos (nome, categoria, unidade, estoque, estoque_minimo, validade, lote, fornecedor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (nome, categoria, unidade, estoque, estoque_minimo, validade or None, lote or None, fornecedor_id))

    conexao.commit()
    conexao.close()
    print("\n✅ Produto cadastrado com sucesso!\n")


def listar_produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT p.*, f.nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
    """)
    produtos = cursor.fetchall()

    print("\n===== PRODUTOS =====")

    if len(produtos) == 0:
        print("Nenhum produto cadastrado.")
    else:
        for p in produtos:
            print(f"ID: {p[0]}")
            print(f"Nome: {p[1]}")
            print(f"Categoria: {p[2]}")
            print(f"Unidade: {p[3]}")
            print(f"Estoque: {p[4]}")
            print(f"Estoque mínimo: {p[5]}")
            print(f"Validade: {p[6] if p[6] else 'Não informada'}")
            print(f"Lote: {p[7] if p[7] else 'Não informado'}")
            print(f"Fornecedor: {p[9] if p[9] else 'Não informado'}")
            print("-" * 30)

    conexao.close()


def editar_produto():
    conexao = conectar()
    cursor = conexao.cursor()

    listar_produtos()
    id_prod = input("\nInforme o ID do produto para editar: ")

    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id_prod,))
    prod = cursor.fetchone()

    if prod is None:
        print("\n❌ Produto não encontrado!")
        conexao.close()
        return

    print(f"\nEditando: {prod[1]}")
    print("(Deixe em branco para manter o valor atual)")

    nome = input(f"Nome [{prod[1]}]: ") or prod[1]
    categoria = input(f"Categoria [{prod[2]}]: ") or prod[2]
    unidade = input(f"Unidade [{prod[3]}]: ") or prod[3]
    estoque_str = input(f"Estoque [{prod[4]}]: ")
    estoque = float(estoque_str) if estoque_str else prod[4]
    est_min_str = input(f"Estoque mínimo [{prod[5]}]: ")
    estoque_minimo = float(est_min_str) if est_min_str else prod[5]
    validade = input(f"Validade [{prod[6] if prod[6] else 'Não informada'}]: ") or prod[6]
    lote = input(f"Lote [{prod[7] if prod[7] else 'Não informado'}]: ") or prod[7]

    # Fornecedor
    cursor.execute("SELECT id, nome FROM fornecedores")
    fornecedores = cursor.fetchall()
    print("\nFornecedores cadastrados:")
    for f in fornecedores:
        print(f"  {f[0]} - {f[1]}")
    print(f"  Atual: {prod[8] if prod[8] else 'Nenhum'}")
    print("  0 - Manter atual / Sem fornecedor")
    escolha = input("Escolha o ID do fornecedor: ")
    if escolha == "0":
        fornecedor_id = prod[8]
    else:
        fornecedor_id = int(escolha)

    cursor.execute("""
        UPDATE produtos 
        SET nome=?, categoria=?, unidade=?, estoque=?, estoque_minimo=?, validade=?, lote=?, fornecedor_id=?
        WHERE id=?
    """, (nome, categoria, unidade, estoque, estoque_minimo, validade, lote, fornecedor_id, id_prod))

    conexao.commit()
    conexao.close()
    print("\n✅ Produto atualizado com sucesso!\n")


def excluir_produto():
    conexao = conectar()
    cursor = conexao.cursor()

    listar_produtos()
    id_prod = input("\nInforme o ID do produto para excluir: ")

    cursor.execute("SELECT nome FROM produtos WHERE id = ?", (id_prod,))
    prod = cursor.fetchone()

    if prod is None:
        print("\n❌ Produto não encontrado!")
        conexao.close()
        return

    confirmar = input(f"Tem certeza que deseja excluir '{prod[0]}'? (s/n): ").lower()
    if confirmar == "s":
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id_prod,))
        conexao.commit()
        print("\n✅ Produto excluído com sucesso!")
    else:
        print("\n❎ Operação cancelada.")

    conexao.close()


# ============ ESTOQUE ============

def atualizar_estoque():
    conexao = conectar()
    cursor = conexao.cursor()

    print("\n===== ATUALIZAR ESTOQUE =====")
    id_produto = int(input("Informe o ID do produto: "))

    cursor.execute("SELECT nome, estoque, unidade FROM produtos WHERE id = ?", (id_produto,))
    produto = cursor.fetchone()

    if produto is None:
        print("\n❌ Produto não encontrado!\n")
        conexao.close()
        return

    print(f"\nProduto: {produto[0]}")
    print(f"Estoque atual: {produto[1]} {produto[2]}")

    print("\n1 - Entrada de mercadoria")
    print("2 - Saída de mercadoria")
    opcao = input("Escolha: ")

    quantidade = float(input(f"Quantidade ({produto[2]}): "))

    data_hoje = datetime.now().strftime("%d/%m/%Y")

    if opcao == "1":
        novo_estoque = produto[1] + quantidade
        nota_fiscal = input("Nota Fiscal (ou deixe em branco): ")
        lote = input("Lote (ou deixe em branco): ")
        validade = input("Validade (DD/MM/AAAA) ou deixe em branco: ")

        cursor.execute("""
            INSERT INTO entradas (produto_id, quantidade, data, validade, lote, nota_fiscal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (id_produto, quantidade, data_hoje, validade or None, lote or None, nota_fiscal or None))

        print(f"\n✅ Entrada registrada: +{quantidade} {produto[2]}")

    elif opcao == "2":
        if quantidade > produto[1]:
            print("\n❌ Erro! Estoque insuficiente.")
            conexao.close()
            return

        novo_estoque = produto[1] - quantidade

        cursor.execute("SELECT id, nome FROM escolas")
        escolas = cursor.fetchall()

        escola_id = None
        if len(escolas) > 0:
            print("\nEscolas cadastradas:")
            for e in escolas:
                print(f"  {e[0]} - {e[1]}")
            escolha = input("ID da escola que recebeu (ou 0 para não vincular): ")
            if escolha != "0":
                escola_id = int(escolha)
        else:
            print("\n⚠️ Nenhuma escola cadastrada.")

        observacao = input("Observação (ou deixe em branco): ")

        cursor.execute("""
            INSERT INTO saidas (produto_id, escola_id, quantidade, data, observacao)
            VALUES (?, ?, ?, ?, ?)
        """, (id_produto, escola_id, quantidade, data_hoje, observacao or None))

        print(f"\n✅ Saída registrada: -{quantidade} {produto[2]}")

    else:
        print("\n❌ Opção inválida.")
        conexao.close()
        return

    cursor.execute("""
        UPDATE produtos SET estoque = ? WHERE id = ?
    """, (novo_estoque, id_produto))

    conexao.commit()
    conexao.close()
    print("\n✅ Estoque atualizado com sucesso!\n")


def verificar_alertas():
    conexao = conectar()
    cursor = conexao.cursor()

    hoje = datetime.now()
    limite_atencao = hoje + timedelta(days=30)

    cursor.execute("SELECT id, nome, estoque, estoque_minimo, validade, unidade FROM produtos")
    produtos = cursor.fetchall()

    vencidos = []
    proximos_vencer = []
    estoque_baixo = []

    for p in produtos:
        id_prod, nome, estoque, est_min, validade_str, unidade = p

        if estoque <= est_min:
            estoque_baixo.append((nome, estoque, est_min, unidade))

        if validade_str:
            try:
                validade = datetime.strptime(validade_str, "%d/%m/%Y")
                if validade < hoje:
                    dias = (hoje - validade).days
                    vencidos.append((nome, validade_str, dias, unidade))
                elif validade <= limite_atencao:
                    dias = (validade - hoje).days
                    proximos_vencer.append((nome, validade_str, dias, unidade))
            except ValueError:
                pass

    conexao.close()

    print("\n" + "=" * 40)
    print("         📋 ALERTAS DO SISTEMA")
    print("=" * 40)

    if vencidos:
        print("\n🔴 PRODUTOS VENCIDOS:")
        for nome, data, dias, unidade in vencidos:
            print(f"   • {nome} — Venceu em {data} (há {dias} dias)")
    else:
        print("\n✅ Nenhum produto vencido.")

    if proximos_vencer:
        print("\n🟡 PRODUTOS QUE VENCEM EM ATÉ 30 DIAS:")
        for nome, data, dias, unidade in proximos_vencer:
            print(f"   • {nome} — Vence em {dias} dias ({data})")
    else:
        print("\n✅ Nenhum produto próximo do vencimento.")

    if estoque_baixo:
        print("\n🔵 ESTOQUE ABAIXO DO MÍNIMO:")
        for nome, estoque, est_min, unidade in estoque_baixo:
            print(f"   • {nome} — {estoque} {unidade} (mínimo: {est_min} {unidade})")
    else:
        print("\n✅ Nenhum produto com estoque baixo.")

    print("\n" + "=" * 40 + "\n")


# ============ RELATÓRIOS ============

def relatorio_estoque_atual():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT p.nome, p.categoria, p.estoque, p.estoque_minimo, p.unidade, p.validade, f.nome
        FROM produtos p
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        ORDER BY p.categoria, p.nome
    """)
    produtos = cursor.fetchall()

    print("\n" + "=" * 60)
    print("         📦 RELATÓRIO DE ESTOQUE ATUAL")
    print("=" * 60)

    if not produtos:
        print("\nNenhum produto cadastrado.")
    else:
        total_itens = 0
        for p in produtos:
            nome, categoria, estoque, est_min, unidade, validade, fornecedor = p
            alerta = " ⚠️ BAIXO" if estoque <= est_min else ""
            print(f"\n📌 {nome} ({categoria})")
            print(f"   Estoque: {estoque} {unidade}{alerta}")
            print(f"   Mínimo: {est_min} {unidade}")
            print(f"   Validade: {validade if validade else 'Não informada'}")
            print(f"   Fornecedor: {fornecedor if fornecedor else 'Não informado'}")
            total_itens += 1

        print(f"\n📊 Total de produtos cadastrados: {total_itens}")

    print("=" * 60 + "\n")
    conexao.close()


def relatorio_entradas():
    conexao = conectar()
    cursor = conexao.cursor()

    mes = input("Digite o mês (MM/AAAA) ou deixe em branco para todas: ").strip()

    if mes:
        cursor.execute("""
            SELECT e.id, p.nome, e.quantidade, e.data, e.nota_fiscal, e.lote, e.validade
            FROM entradas e
            JOIN produtos p ON e.produto_id = p.id
            WHERE e.data LIKE ?
            ORDER BY e.data DESC
        """, (f"%/{mes}",))
    else:
        cursor.execute("""
            SELECT e.id, p.nome, e.quantidade, e.data, e.nota_fiscal, e.lote, e.validade
            FROM entradas e
            JOIN produtos p ON e.produto_id = p.id
            ORDER BY e.data DESC
        """)

    entradas = cursor.fetchall()

    print("\n" + "=" * 60)
    print("         📥 RELATÓRIO DE ENTRADAS")
    if mes:
        print(f"         Mês: {mes}")
    print("=" * 60)

    if not entradas:
        print("\nNenhuma entrada registrada.")
    else:
        total = 0
        for e in entradas:
            id_ent, nome, qtd, data, nf, lote, validade = e
            print(f"\n📌 {nome}")
            print(f"   Quantidade: +{qtd}")
            print(f"   Data: {data}")
            print(f"   Nota Fiscal: {nf if nf else 'Não informada'}")
            print(f"   Lote: {lote if lote else 'Não informado'}")
            print(f"   Validade: {validade if validade else 'Não informada'}")
            total += qtd

        print(f"\n📊 Total de entradas: {len(entradas)} registros")

    print("=" * 60 + "\n")
    conexao.close()


def relatorio_saidas():
    conexao = conectar()
    cursor = conexao.cursor()

    print("\nEscolas cadastradas:")
    cursor.execute("SELECT id, nome FROM escolas")
    escolas = cursor.fetchall()
    for e in escolas:
        print(f"  {e[0]} - {e[1]}")
    print("  0 - Todas as escolas")

    escolha = input("Escolha o ID da escola: ").strip()

    if escolha == "0":
        cursor.execute("""
            SELECT s.id, p.nome, s.quantidade, s.data, e.nome, s.observacao
            FROM saidas s
            JOIN produtos p ON s.produto_id = p.id
            LEFT JOIN escolas e ON s.escola_id = e.id
            ORDER BY s.data DESC
        """)
    else:
        cursor.execute("""
            SELECT s.id, p.nome, s.quantidade, s.data, e.nome, s.observacao
            FROM saidas s
            JOIN produtos p ON s.produto_id = p.id
            LEFT JOIN escolas e ON s.escola_id = e.id
            WHERE s.escola_id = ?
            ORDER BY s.data DESC
        """, (escolha,))

    saidas = cursor.fetchall()

    print("\n" + "=" * 60)
    print("         📤 RELATÓRIO DE SAÍDAS")
    print("=" * 60)

    if not saidas:
        print("\nNenhuma saída registrada.")
    else:
        for s in saidas:
            id_sai, nome, qtd, data, escola, obs = s
            print(f"\n📌 {nome}")
            print(f"   Quantidade: -{qtd}")
            print(f"   Data: {data}")
            print(f"   Escola: {escola if escola else 'Não vinculada'}")
            print(f"   Observação: {obs if obs else 'Nenhuma'}")

        print(f"\n📊 Total de saídas: {len(saidas)} registros")

    print("=" * 60 + "\n")
    conexao.close()


def relatorio_resumo():
    conexao = conectar()
    cursor = conexao.cursor()

    hoje = datetime.now()
    mes_atual = hoje.strftime("%m/%Y")

    cursor.execute("SELECT COUNT(*) FROM produtos")
    total_produtos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(estoque) FROM produtos")
    total_estoque = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM fornecedores")
    total_fornecedores = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM escolas")
    total_escolas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT SUM(quantidade) FROM entradas WHERE data LIKE ?
    """, (f"%/{mes_atual}",))
    entradas_mes = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT SUM(quantidade) FROM saidas WHERE data LIKE ?
    """, (f"%/{mes_atual}",))
    saidas_mes = cursor.fetchone()[0] or 0

    cursor.execute("SELECT nome, validade FROM produtos WHERE validade IS NOT NULL")
    vencidos = 0
    proximos = 0
    for p in cursor.fetchall():
        try:
            v = datetime.strptime(p[1], "%d/%m/%Y")
            if v < hoje:
                vencidos += 1
            elif v <= hoje + timedelta(days=30):
                proximos += 1
        except:
            pass

    cursor.execute("SELECT COUNT(*) FROM produtos WHERE estoque <= estoque_minimo")
    estoque_baixo = cursor.fetchone()[0]

    conexao.close()

    print("\n" + "=" * 50)
    print("         📊 RESUMO DO SISTEMA")
    print("=" * 50)
    print(f"\n📦 Produtos cadastrados:        {total_produtos}")
    print(f"📊 Total em estoque:             {total_estoque:.0f} unidades")
    print(f"🏭 Fornecedores:                 {total_fornecedores}")
    print(f"🏫 Escolas:                      {total_escolas}")
    print(f"\n📥 Entradas do mês ({mes_atual}):   {entradas_mes:.0f}")
    print(f"📤 Saídas do mês ({mes_atual}):    {saidas_mes:.0f}")
    print(f"\n🔴 Produtos vencidos:            {vencidos}")
    print(f"🟡 Próximos do vencimento:       {proximos}")
    print(f"🔵 Estoque abaixo do mínimo:     {estoque_baixo}")
    print("=" * 50 + "\n")


def menu_relatorios():
    while True:
        print("\n===== RELATÓRIOS =====")
        print("1 - Estoque atual")
        print("2 - Histórico de entradas")
        print("3 - Histórico de saídas por escola")
        print("4 - Resumo geral (dashboard)")
        print("5 - Voltar ao menu principal")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            relatorio_estoque_atual()
        elif opcao == "2":
            relatorio_entradas()
        elif opcao == "3":
            relatorio_saidas()
        elif opcao == "4":
            relatorio_resumo()
        elif opcao == "5":
            break
        else:
            print("\n❌ Opção inválida!")


# ============ GERENCIAR REGISTROS ============

def menu_gerenciar():
    while True:
        print("\n===== GERENCIAR REGISTROS =====")
        print("1 - Editar produto")
        print("2 - Excluir produto")
        print("3 - Editar fornecedor")
        print("4 - Excluir fornecedor")
        print("5 - Editar escola")
        print("6 - Excluir escola")
        print("7 - Voltar ao menu principal")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":
            editar_produto()
        elif opcao == "2":
            excluir_produto()
        elif opcao == "3":
            editar_fornecedor()
        elif opcao == "4":
            excluir_fornecedor()
        elif opcao == "5":
            editar_escola()
        elif opcao == "6":
            excluir_escola()
        elif opcao == "7":
            break
        else:
            print("\n❌ Opção inválida!")


# ============ MENU PRINCIPAL ============

while True:

    print("\n===== SISTEMA DE ESTOQUE =====")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Atualizar estoque")
    print("4 - Cadastrar fornecedor")
    print("5 - Listar fornecedores")
    print("6 - Cadastrar escola")
    print("7 - Listar escolas")
    print("8 - Verificar alertas")
    print("9 - Relatórios")
    print("10 - Gerenciar registros")
    print("11 - Sair")

    opcao = input("\nEscolha uma opção: ")

    if opcao == "1":
        cadastrar_produto()

    elif opcao == "2":
        listar_produtos()

    elif opcao == "3":
        atualizar_estoque()

    elif opcao == "4":
        cadastrar_fornecedor()

    elif opcao == "5":
        listar_fornecedores()

    elif opcao == "6":
        cadastrar_escola()

    elif opcao == "7":
        listar_escolas()

    elif opcao == "8":
        verificar_alertas()

    elif opcao == "9":
        menu_relatorios()

    elif opcao == "10":
        menu_gerenciar()

    elif opcao == "11":
        print("\nSistema encerrado. Até logo!")
        break

    else:
        print("\n❌ Opção inválida!")