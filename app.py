from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mysqldb import MySQLdb

# Início da aplicação
app = Flask(__name__)
app.secret_key = 'nova_senha'

# Configuração do banco de dados
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # Coloque sua senha aqui
app.config['MYSQL_DB'] = 'doacao_comida'

mysql = MySQL(app)


# Rota inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Configurar o cursor como DictCursor para retornar os resultados como dicionário
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()  # Agora retorna um dicionário
        cur.close()

        if usuario and check_password_hash(usuario['senha'], senha):  # Verifica o hash da senha
            session['tipo'] = usuario['tipo']
            session['nome'] = usuario['nome']
            session['email'] = usuario['email']
            session['usuario_id'] = usuario['id']
            
            flash('Login realizado com sucesso!', 'success')
            
            # Redireciona dependendo do tipo de usuário
            if usuario['tipo'] == 'restaurante':
                return redirect('/restaurante')
            elif usuario['tipo'] == 'ong':
                return redirect('/ong')
            else:  # Caso seja admin
                return redirect('/area_restrita')
        else:
            flash('Email ou senha inválidos!', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # Limpa todos os dados da sessão
    return redirect('/')

# Área restrita para gerenciamento de doações
@app.route('/area_restrita')
def area_restrita():
    # Verifica se o usuário logado é admin
    if 'tipo' not in session or session['tipo'] != 'admin':
        flash('Apenas administradores podem acessar esta página.', 'danger')
        return redirect('/login')

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Consulta para listar todas as doações
        cur.execute("SELECT * FROM doacoes")
        doacoes = cur.fetchall()

        # Consulta para listar todos os usuários (Restaurantes e ONGs)
        cur.execute("SELECT * FROM usuarios WHERE tipo != 'admin'")
        usuarios = cur.fetchall()
        cur.close()

        # Renderiza a página com os dados de doações e usuários
        return render_template('area_restrita.html', doacoes=doacoes, usuarios=usuarios)
    except Exception as e:
        flash(f'Erro ao carregar os dados: {str(e)}', 'danger')
        return render_template('area_restrita.html', doacoes=[], usuarios=[])


@app.route('/editar_doacao/<int:doacao_id>', methods=['GET', 'POST'])
def editar_doacao(doacao_id):
    if 'tipo' not in session or session['tipo'] != 'admin':
        flash('Apenas administradores podem acessar esta funcionalidade.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        tipo = request.form['tipo']
        descricao = request.form['descricao']
        localizacao = request.form['localizacao']

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE doacoes SET tipo = %s, descricao = %s, localizacao = %s WHERE id = %s",
                (tipo, descricao, localizacao, doacao_id)
            )
            mysql.connection.commit()
            cur.close()
            flash('Doação editada com sucesso!', 'success')
            return redirect('/area_restrita')
        except Exception as e:
            flash(f'Erro ao editar a doação: {str(e)}', 'danger')

    # Carregar dados da doação para exibir no formulário
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM doacoes WHERE id = %s", (doacao_id,))
    doacao = cur.fetchone()
    cur.close()
    return render_template('editar_doacao.html', doacao=doacao)


@app.route('/excluir_doacao/<int:doacao_id>')
def excluir_doacao(doacao_id):
    if 'tipo' not in session or session['tipo'] != 'admin':
        flash('Apenas administradores podem acessar esta funcionalidade.', 'danger')
        return redirect('/login')

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM doacoes WHERE id = %s", (doacao_id,))
        mysql.connection.commit()
        cur.close()
        flash('Doação excluída com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir a doação: {str(e)}', 'danger')

    return redirect('/area_restrita')


@app.route('/editar_usuario/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    if 'tipo' not in session or session['tipo'] != 'admin':
        flash('Apenas administradores podem acessar esta funcionalidade.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        endereco = request.form['endereco']

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "UPDATE usuarios SET nome = %s, email = %s, telefone = %s, endereco = %s WHERE id = %s",
                (nome, email, telefone, endereco, usuario_id)
            )
            mysql.connection.commit()
            cur.close()
            flash('Usuário editado com sucesso!', 'success')
            return redirect('/area_restrita')
        except Exception as e:
            flash(f'Erro ao editar o usuário: {str(e)}', 'danger')

    # Carregar dados do usuário para exibir no formulário
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cur.fetchone()
    cur.close()
    return render_template('editar_usuario.html', usuario=usuario)


@app.route('/excluir_usuario/<int:usuario_id>')
def excluir_usuario(usuario_id):
    if 'tipo' not in session or session['tipo'] != 'admin':
        flash('Apenas administradores podem acessar esta funcionalidade.', 'danger')
        return redirect('/login')

    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        mysql.connection.commit()
        cur.close()
        flash('Usuário excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir o usuário: {str(e)}', 'danger')

    return redirect('/area_restrita')


@app.route('/enviar_notificacoes', methods=['POST'])
def enviar_notificacoes():
    if 'tipo' not in session or session['tipo'] != 'admin':
        return {'message': 'Apenas administradores podem enviar notificações.'}, 403

    # try:
        cur = mysql.connection.cursor()
        # Consulta para obter os e-mails das ONGs
        cur.execute("SELECT email FROM usuarios WHERE tipo = 'ong'")
        emails = [row[0] for row in cur.fetchall()]
        cur.close()

        # Envio de e-mails
         # Configure suas credenciais
        yag = yagmail.SMTP("seu_email@gmail.com", "sua_senha")
        # Enviar o e-mail
        yag.send(to="destinatario@gmail.com",
                 subject="Teste com Yagmail",
                 contents="Este é um teste de envio de e-mail usando Yagmail.")
        return "E-mail enviado com sucesso!"
    #except Exception as e:
        return f"Erro ao enviar e-mail: {str(e)}"

    

# Cadastro de usuário (Restaurante ou ONG)
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])  # Hash da senha
        nome = request.form['nome']
        cnpj = request.form['cpf_cnpj']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        tipo = request.form['tipo']  # 'Restaurante' ou 'ONG'

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuarios (email, senha, nome, endereco, cpf_cnpj, telefone, tipo) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (email, senha, nome, cnpj, endereco, telefone, tipo))
        mysql.connection.commit()
        cur.close()

        flash('Cadastro realizado com sucesso!', 'success')
        return redirect('/')

    return render_template('cadastro.html')


# Rota para adicionar doações
@app.route('/doar', methods=['GET', 'POST'])
def doar():
    # Verifica se o usuário está logado e é um restaurante
    if 'tipo' not in session or session['tipo'] != 'restaurante':
        flash('Apenas restaurantes podem acessar esta página.', 'danger')
        return redirect('/login')

    if request.method == 'POST':
        tipo = request.form['tipo']
        descricao = request.form['descricao']
        localizacao = request.form['localizacao']

        try:
            cur = mysql.connection.cursor()
            # Insere os dados da doação no banco
            cur.execute(
                "INSERT INTO doacoes (tipo, descricao, localizacao, usuario_id) VALUES (%s, %s, %s, %s)",
                (tipo, descricao, localizacao, session['usuario_id'])
            )
            mysql.connection.commit()
            cur.close()

            flash('Doação cadastrada com sucesso!', 'success')
            return redirect('/restaurante')
        except Exception as e:
            flash(f'Erro ao cadastrar a doação: {str(e)}', 'danger')

    return render_template('restaurante.html')  # Retorna à página do restaurante


@app.route('/suporte', methods=['POST'])
def suporte():
    # Verifica se o usuário está logado
    if 'tipo' not in session:
        flash('Você precisa estar logado para acessar o suporte.', 'danger')
        return redirect('/login')

    mensagem = request.form['mensagem']

    try:
        cur = mysql.connection.cursor()
        # Envia a mensagem para a tabela de notificações
        cur.execute(
            "INSERT INTO notificacoes (email_destinatario, mensagem) VALUES (%s, %s)",
            ('admin@doacao.com', mensagem)  # Envia ao email do administrador
        )
        mysql.connection.commit()
        cur.close()

        flash('Mensagem enviada ao suporte com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao enviar a mensagem para o suporte: {str(e)}', 'danger')

    return redirect('/restaurante')  # Retorna à página do restaurante


@app.route('/restaurante')
def restaurante():
    # Verifica se o usuário está logado e é um restaurante
    if 'tipo' not in session or session['tipo'] != 'restaurante':
        flash('Apenas restaurantes podem acessar esta página.', 'danger')
        return redirect('/login')

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Seleciona as doações do restaurante logado
        cur.execute(
            "SELECT id, tipo, descricao, data_hora, localizacao FROM doacoes WHERE usuario_id = %s",
            (session['usuario_id'],)
        )
        historico_doacoes = cur.fetchall()
        cur.close()

        # Renderiza a página com o histórico de doações
        return render_template('restaurante.html', historico_doacoes=historico_doacoes)
    except Exception as e:
        flash(f'Erro ao carregar o histórico de doações: {str(e)}', 'danger')
        return render_template('restaurante.html', historico_doacoes=[])
    
@app.route('/ong')
def ong():
    # Verifica se o usuário está logado e é uma ONG
    if 'tipo' not in session or session['tipo'] != 'ong':
        flash('Apenas ONGs podem acessar esta página.', 'danger')
        return redirect('/login')

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Consulta para obter doações e contatos dos restaurantes
        cur.execute("""
            SELECT 
                doacoes.tipo,
                doacoes.descricao,
                doacoes.localizacao,
                doacoes.data_hora,
                usuarios.nome AS restaurante_nome,
                usuarios.email AS restaurante_email,
                usuarios.telefone AS restaurante_telefone
            FROM doacoes
            JOIN usuarios ON doacoes.usuario_id = usuarios.id
            WHERE usuarios.tipo = 'restaurante'
        """)
        doacoes_disponiveis = cur.fetchall()
        cur.close()

        # Renderiza a página com as doações disponíveis
        return render_template('ong.html', doacoes_disponiveis=doacoes_disponiveis)
    except Exception as e:
        flash(f'Erro ao carregar as doações disponíveis: {str(e)}', 'danger')
        return render_template('ong.html', doacoes_disponiveis=[])





if __name__ == '__main__':
    app.run(debug=True)
