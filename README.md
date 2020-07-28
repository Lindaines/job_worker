# Job Worker

**Índice**
1. [Introdução](#intr)
2. [Configuração de ambiente](#cs1)
3. [Rodar projeto](#run)


## Introdução <a name="intr"></a>

Esse serviço é responsável schedular e executar os Jobs que tem a descriçao que bate com seu Worker. 
Se uma mensagem com os parâmetros corretos chega na fila desse Worker pelo RabbitMQ, ele vai:
* Agendar o Job e colocá-lo num banco de dados pra guardar estado do mesmo. Então supondo que o Worker por algum motivo quebre e reinicie, os jobs já schedulados e seus estados não serão perdidos.
* Adicionar um timeout na função que será executada. Ex: Se a importação de base legada estiver sendo executada e estourar o timeout, a função lança exceção e o job morre.
* Publicar eventos de: Criação/Execução/Finalização/Timeout/Erro dos Jobs agendados numa fila de eventos do RabbitMQ. Essa fila será consumida por um outro serviço que fará a atualização do status do job e notificará uma lista de e-mails.


O arquivo `settings.py` é responsável por capturar as variáveis de ambiente requeridas para o projeto.
 * Atenção para as seguintes variáveis:
     - TIMEOUT_IN_SECONDS: Um inteiro que representa o timeout em segundos pra um job ser executado. O padrão são 28800 segundos(8 horas). 
     - FAKE_PROCESS_TIME_IN_SECONDS: Um inteiro que representa em segundos qual o tempo fictício para o processamento do Worker ser executado. Como aqui o trabalho de extração em si não foi implementado, é útil pra testar o evento de timeout e cancelamento do Job.
 
## Configuração de ambiente <a name="cs1"></a>
Instalar dependências(rodar na raíz do projeto, versão do Python é 3.7)
````bash
pip install -r requirements.txt
````

## Rodar Projeto <a name="run"></a>
Comando para iniciar aplicação
````bash
python main.py
````

