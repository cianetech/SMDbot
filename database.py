import psycopg2
from config import POSTGRESQL_DB_NAME, POSTGRESQL_USER_NAME, POSTGRESQL_HOST, POSTGRESQL_PASSWORD

class Database:
    cursor = None
    conn = None

    def status_connection(self):
        if self.conn.closed == 0:
            return "ON"
        else:
            return "OFF"

    def open_connection(self):
        self.conn = psycopg2.connect("\
            dbname=" + POSTGRESQL_DB_NAME + "\
            user=" + POSTGRESQL_USER_NAME + "\
            host=" + POSTGRESQL_HOST + "\
            password=" + POSTGRESQL_PASSWORD  + "\
        ")
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()
        print("Open Database Connection")

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        print("Close Database Connection")

    def print_result(self, result):
        for x in result:
            print(x)

    def show_tables(self):
        self.cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        result = self.cursor.fetchall()
        print("Tables: ")
        self.print_result(result)

    def create_table(self, name, columns):
        sql = "create table if not exists " + name + " (" + ",".join(columns) + ")"
        self.cursor.execute(sql)
        print(self.cursor.statusmessage + " sql: " + sql)

    def drop_table(self, name):
        sql = "drop table if exists " + name
        self.cursor.execute(sql)
        print(self.cursor.statusmessage + " sql: " + sql)

    def insert(self, table_name, columns, data):
        sql = "INSERT INTO " + table_name + " (" + ",".join(columns) + ") VALUES (" + ",".join(data) + ")"
        self.cursor.execute(sql)
        print(self.cursor.statusmessage + " sql: " + sql)

    def select_all(self,table_name):
        sql = "SELECT * FROM " + table_name
        self.cursor.execute(sql)
        print(self.cursor.statusmessage + " sql:" + sql)
        self.print_result(self.cursor.fetchall())

    def find_exact(self,text):
        sql = "SELECT resposta_text FROM pergunta, resposta WHERE pergunta_id = pergunta_id_fk AND pergunta_text ILIKE " + "'" + text + "'"
        self.cursor.execute(sql)
        self.print_result(self.cursor.fetchall())

    def create_db_model(self):
        #drop_table("pergunta")
        #drop_table("resposta")

        self.create_table("pergunta", ["pergunta_id SERIAL PRIMARY KEY", "pergunta_text text NOT NULL"])
        self.create_table("resposta", ["resposta_id SERIAL PRIMARY KEY",
                                       "resposta_text text NOT NULL", "pergunta_id_fk INTEGER REFERENCES pergunta(pergunta_id) ON DELETE CASCADE"])


    def load_db(self):
        data =  self.get_example_data()
        count = 1
        for d in data:
            self.insert("pergunta",["pergunta_text"],
                        ["'"+d[0]+"'"])
            self.insert("resposta",["resposta_text","pergunta_id_fk"],
                        ["'"+d[1]+"'", str(count)])
            count = count + 1


    def insert_new_question(self, question, answers):
        self.insert("pergunta",["pergunta_text"], ["'"+question+"'"])
        self.cursor.execute("SELECT pergunta_id from pergunta where pergunta_text = " + "'" + question + "'")
        result = self.cursor.fetchall()[0][0] # get first tuple and first colummn
        for asr in answers:
            self.insert("resposta",["resposta_text","pergunta_id_fk"],["'"+asr+"'", str(result)])
        

    def get_data(self):
        data = []
        self.cursor.execute("SELECT pergunta_id, pergunta_text from pergunta")
        result_q = self.cursor.fetchall()
        
        for q in result_q:
            q_id = q[0]
            q_text = str(q[1])#.replace("'", "", 2)
            self.cursor.execute("SELECT resposta_text from resposta where pergunta_id_fk = " + str(q_id))
            result_a = self.cursor.fetchall()
            ent = []
            ent.append(q_text)
            
            for a in result_a:
                a_text = str(a[0])#.replace("'", "", 2)
                ent.append(a_text)
            data.append(ent)
        
        return data

    def get_example_data(self):
        data = [
            ["Qual o dia da matrícula?",
             "Verificar no calendário universitário disponível no site da UFC => http://www.ufc.br/"],
            ["Qual o dia do trancamento?",
             "Verificar no calendário universitário disponível no site da UFC => http://www.ufc.br/"],
            ["Tem laboratório livre para estudo? Como saber?",
             "Através do mapa de salas, atualizado em tempo, disponível no site do SMD, menu documentos."],
            ["Quero reservar uma sala. Como faço?",
             "Verificar a sala que está livre no mapa de salas e solicitar a reserva com a coordenação. Se for de outro curso ou departamento, é preciso um ofício com a solicitação do espaço."],
            ["Como solicitar carteira de estudante? Quais documentos e onde tenho que ir?",
             "Para orientações sobre carteira de estudante, indicamos procurar o CA ou a Etufor."],
            ["Quero conversar com um determinado professor. Como agendar?",
             "O aluno pode agendar através do email do professor que está disponível no site do SMD ou se estiver na disciplina desse professor, no SIGAA."],
            ["Como vou saber se irei me formar?",
             "O aluno pode verificar no SIGAA => portal do discente-ensino-consultas do discente-pendências de conclusão. Se ainda assim estiver com dúvidas, procurar a coordenação."],
            ["Para onde envio o arquivo com a versão final do meu TCC?",
             "Por email para a coordenação e com cópia para seu orientador."],
            ["Quanto tempo tenho para entregar a versão final do TCC?", "Verifique os prazos com seu orientador."],
            ["Não poderei ir na colação de grau. O que fazer?",
             "Nomear um procurador para assinar a ata pelo aluno. Alguns dias antes da cerimônia, a coordenação sempre envia as demais orientações."],
            ["Onde tenho que buscar meu diploma?", "Na Prograd, após 60 dias da cerimônia de colação de grau."],
            ["Como pedir aproveitamento de uma disciplina?",
             "Preencher o formulário e entregar na coordenação juntamente com o histórico e as ementas já cursadas."],
            ["Como faço para entregar minhas atividades complementares?",
             "1 - Os alunos devem trazer os originais para digitalizar na Coordenação, mas o formulário deve ser impresso, pois precisa da assinatura do aluno; 2 - Os documentos originalmente digitais, podem ser entregues impressos ou em pendrive; se os documentos estiverem na nuvem, temos um computador de apoio para o aluno fazer o download; 3 - Se disponível, digitalizaremos no momento da entrega, e devolveremos tudo ao aluno. Caso contrário, ficaremos com os originais, e devolveremos assim que a digitalização for concluída."],
            ["Estou com dúvida sobre o formulário de atividades complementares. Como dividir as atividades nos grupos?",
             "Verificar as orientações no manual e no FAQ disponíveis no site do SMD."],
            ["Que horas posso conversar com o coordenador?",
             "O aluno pode marcar com o coordenador através de email, que está disponível no site do SMD."],
            ["Não sei se hoje haverá aula. Como saber?", "Geralmente o cancelamento de aulas são divulgados pelo SIGAA"],
            ["A coordenação vai funcionar nas férias?",
             "Sim. Qualquer mudança no horário de funcionamento para atendimento, são divulgadas com antecedência."],
            ["A matrícula é pela internet ou tenho que ir na coordenação?",
             "Todas as fases da matrícula são pela internet através do SIGAA, com exceção de alunos com bloqueios notificados pelo SIGAA no ato da matrícula."],
            ["Quero cursar somente uma disciplina no semestre. É possível?",
             "Não, o aluno deve cursar, no mínimo, 192h. Por exemplo => 3 disciplinas de 64h cada. "],
            ["Minhas disciplinas foram indeferidas. O que fazer no ajuste?",
             "O aluno deve efetuar uma nova solicitação no período de ajuste. "],
            ["Posso retirar disciplinas no ajuste em tempo real?",
             "Não, nesse período só é permitido incluir disciplinas."],
            ["Perdi a 1ª fase da matrícula. O que fazer? Não irei nenhuma cursar nenhuma disciplina no semestre?",
             "O aluno deve efetuar uma nova solicitação nas próximas fases da matrícula => ajuste e tempo real."],
            ["Em quais situações posso perder minha matrícula?",
             "Caso o aluno tenha reprovação por frequência após ter assinado o termo de ciência ou não se matricular em nenhuma disciplina nem ter solicitado matrícula institucional."],
            ["Acho que posso reprovar por falta mas fiquei doente alguns dias. É possível abonar minhas faltas? Devo entregar o atestado médico na coordenação?",
             "Oficialmente, não há abono de faltas na UFC, porém o aluno pode solicitar regime especial no departamento médico, por motivo de saúde, durante um determinado período, o qual permitirá acompanhar as disciplinas a distância, sem prejudicar sua frequência. "],
            ["O que é matrícula institucional? Como solicitar? ",
             "É a possibilidade de manter o vínculo ativo com a UFC sem cursar nenhuma disciplina no semestre. O tempo de curso não é interrrompido. O período de matrícula institucional é o mesmo da matrícula curricular. Só é permitida ao estudante que integralizou todos os componentes curriculares obrigatórios dos dois primeiros semestres do curso."],
            ["Quero trancar uma disciplina. Como faço?",
             "Alguns dias antes da data informada no calendário universitário, a coordenação divulga os procedimentos em todos os canais de comunicação disponíveis. "],
            ["Quero trancar o semestre. Como solicitar?",
             "Preencher e assinar o formulário de solicitação e entregar na coordenação juntamente com a documentação necessária, exceto em caso de saúde, cuja a entrada deve ser no Departamento Médico da UFC que fica ao lado do RU do Benfica."],
            ["Se eu trancar o semestre, meu IRA sofrerá alteração?",
             "Não, o trancamento total não afeta o IRA, pois interrompe a contagem de tempo do curso."],
            ["O trancamento do semestre prejudica o tempo de curso para me formar?",
             "Não, pois interrompe a contagem de tempo do curso."],
            ["Não estou recebendo as notificações do SIGAA. O que fazer?",
             "Sempre mantenha seus dados pessoais atualizados no SIGAA, principalmente email."],
            ["Posso utilizar uma das mesas digitalizadores que estão na coordenação?",
             "Sim, somente para uso dentro do bloco e assinando o protocolo."],
            ["Quando posso levar meus documentos de estágio para serem assinados pelo orientador?",
             "O aluno pode trazer toda a documentação já preenchida e assinada para a Coordenação e, na 1ª oportunidade, o orientador assinará. "],
            ["Quais são as disciplinas eletivas? Quantas eletivas tenho que cursar?",
             "As disciplinas eletivas do 4º semestre são => Análise e Projeto de Sistemas, Estruturas de Dados, Redes de Computadores, Desenho II, Fotografia Digital e Semiótica Aplicada. Desse grupo, o aluno deve cursar 4 disciplinas. As disciplinas eletivas do 5º semestre são => Engenharia de Software, Banco de Dados I, Comunicação Visual II e Design de Som. Desse grupo, o aluno deve cursar 3 disciplinas."],
            ["É obrigatório cursar as disciplinas livres?",
             "Não, é uma opção do aluno utilizar parte da carga horária de optativas para cursar fora do SMD. O limite máximo está na matriz curricular."]
        ]
        return data


##### Test Database

#db = Database()
#db.open_connection()

#db.insert_new_question( "Test de Pergunta?", ["resposta 1", "resposta 2"])
#print(db.get_data())

#db.close_connection()
 