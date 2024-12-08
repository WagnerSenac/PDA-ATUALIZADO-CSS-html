-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS doacao_comida;
USE doacao_comida;

-- Tabela de usuários para login
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(191) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL, -- Senha será armazenada como hash
    nome VARCHAR(255) NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    cpf_cnpj VARCHAR(20) NOT NULL, -- Reduzido para valores típicos de CPF/CNPJ
    telefone VARCHAR(20) NOT NULL,
    tipo ENUM('admin', 'restaurante', 'ong') NOT NULL
);

-- Inserção de um usuário administrativo inicial (senha deverá ser hash no backend)
INSERT INTO usuarios (email, senha, nome, endereco, cpf_cnpj, telefone, tipo) 
VALUES (
    'admin@doacao.com', 
    'scrypt:32768:8:1$dFqtysmf4O9Tt2yB$02e687bda6c4f00a436d4b876667b15ed4385112f33e7d1f6e1d1a2bdf9634aafcb3d0bbf4eb285673bcc0d633c6bd3eba360c6b9c7a7a4e014797f2271bb2f5', 
    'Administrador', 
    'Rua do Passeio', 
    '12345678901', 
    '32456789', 
    'admin'
);

-- Tabela de doações
CREATE TABLE doacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('comida', 'roupas', 'outros') NOT NULL,
    descricao TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP, -- Combina data e hora
    localizacao VARCHAR(255) NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);


-- Tabela de notificações
CREATE TABLE notificacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email_destinatario VARCHAR(191) NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    mensagem TEXT NOT NULL
);
