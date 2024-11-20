import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Inicia interpretador do SQLAlchemy
Base = declarative_base()

#vvv Modelo da tabela
class Dados(Base):
    __tablename__ = 'dados'
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
#^^^^


#cria db e user
def criar_db_e_usuario(db_admin_uri, novo_usuario, nova_senha, novo_db, verbose=False):
   
    try:
        conn = psycopg2.connect(db_admin_uri)
        conn.autocommit = True
        cur = conn.cursor()

        #cria user
        cur.execute(f"""
            DO $$ BEGIN
                CREATE ROLE {novo_usuario} WITH LOGIN PASSWORD '{nova_senha}';
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"Usuário '{novo_usuario}' verificado/criado.")

        #cria db
        cur.execute(f"""
            DO $$ BEGIN
                CREATE DATABASE {novo_db} OWNER {novo_usuario};
            EXCEPTION WHEN OTHERS THEN NULL;
            END $$;
        """)
        if verbose:
            print(f"Banco de dados '{novo_db}' verificado/criado.")

        cur.close()
        conn.close()
    except Exception as e:
        if verbose:
            print("Erro ao criar usuário ou banco de dados:", e)


#inicializa db e cria tabelas definidas pelo modelo
def inicializar_db(uri, verbose=False):
   
    try:
        engine = create_engine(uri)
        Base.metadata.create_all(engine)  
        if verbose:
            print("Tabelas criadas/verificadas com sucesso.")
        Session = sessionmaker(bind=engine)
        return Session()
    except Exception as e:
        if verbose:
            print("Erro ao inicializar o banco de dados:", e)
        raise

'''
# Exemplo de uso
if __name__ == "__main__":
    # Configuração do superusuário e banco
    ADMIN_URI = 'postgresql://admin:admin_pass@localhost/postgres'
    NOVO_USUARIO = 'meu_usuario'
    NOVA_SENHA = 'minha_senha'
    NOVO_DB = 'meu_banco'

    # Criação do banco de dados e usuário
    criar_db_e_usuario(
        db_admin_uri=ADMIN_URI,
        novo_usuario=NOVO_USUARIO,
        nova_senha=NOVA_SENHA,
        novo_db=NOVO_DB,
        verbose=True
    )

    # Inicialização do banco de dados
    DB_URI = f'postgresql://{NOVO_USUARIO}:{NOVA_SENHA}@localhost/{NOVO_DB}'
    session = inicializar_db(DB_URI, verbose=True)

    # Exemplo de operação (opcional)
    nova_entrada = Dados(nome="Exemplo", valor=123.45)
    session.add(nova_entrada)
    session.commit()
    print("Entrada adicionada ao banco de dados com sucesso.")
'''