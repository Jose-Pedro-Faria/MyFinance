# MyFinance

Aplicação web pessoal para registar e acompanhar as finanças: património, receitas e despesas mensais, investimentos, dívidas e despesas programadas, com uma página inicial de estatísticas e gráficos.

Foi pensada para **uso individual** (um único utilizador), a correr no próprio computador ou num servidor próprio, com os dados guardados numa base de dados SQLite. Tem apenas tema escuro.

## Índice

- [Funcionalidades](#funcionalidades)
- [Como são feitos os cálculos](#como-são-feitos-os-cálculos)
- [Tecnologias](#tecnologias)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Executar localmente (desenvolvimento)](#executar-localmente-desenvolvimento)
- [Executar com Docker](#executar-com-docker)
- [Configuração (variáveis de ambiente)](#configuração-variáveis-de-ambiente)
- [Cópias de segurança e restauro](#cópias-de-segurança-e-restauro)
- [Mudar para outro PC ou servidor](#mudar-para-outro-pc-ou-servidor)
- [Segurança](#segurança)
- [Resolução de problemas](#resolução-de-problemas)
- [Desenvolvimento](#desenvolvimento)
- [Licença](#licença)

---

## Funcionalidades

O acesso a todas as páginas exige login.

### Home (estatísticas)

Página inicial que **só lê** os dados das outras páginas e calcula.

- **Cartões:** património total do último registo (com variação face ao anterior), total sem emergência, investimentos (valor atual), património líquido, dívida total e mensalidades, sobra do último mês, meses de fundo de emergência, peso das dívidas na receita, despesas programadas pendentes.
- **Gráficos** (Chart.js, funcionam sem internet):
  - Evolução do património: Total, Total sem Emergência, Dinheiro, Emergência e Investimentos.
  - Receitas vs despesas por mês, com a sobra.
  - Investido vs valor atual dos investimentos, com a diferença em € e %.
  - Investimentos atuais por categoria, com tabela de percentagens ao lado.
- **Interação nos gráficos:** caixas de seleção para escolher quais as séries visíveis (por defeito todas), filtro de período (3, 6, 12 meses ou tudo) e botão **Maximizar** (ecrã inteiro; `Esc` para sair).
- **Tabelas:** médias mensais e anuais (receitas, despesas, investido, sobra), totais por ano, despesas programadas pendentes por mês, e sobra do mês vs variação do património.

### Registo Património

- Registo **mensal** do património total.
- As categorias são criadas pelo utilizador (por exemplo, uma conta nova num banco) e pertencem sempre a um de três grupos: **Dinheiro**, **Emergência** ou **Investimentos**.
- A tabela mostra, por mês, o total de cada grupo, o **Total** e o **Total sem Emergência**. O botão **+/−** em cada grupo mostra ou esconde as categorias desse grupo.
- Criar um mês novo: escolhe-se o mês e o ano em listas. Se o mês já existir, a app avisa e o registo deve ser alterado pela tabela.
- Cada mês pode ser **editado** ou **apagado** a partir da tabela (apagar pede confirmação).
- Os campos aceitam **somas** (ex.: `1200+350`).
- As categorias podem ser desativadas sem perder o histórico.

### Relatórios Mensais

- Registo mensal com **quatro categorias principais**: Receita, Despesas Essenciais, Despesas Não Essenciais e Investimento.
- Dentro de cada categoria criam-se subcategorias à vontade (ex.: "Salário" em Receita, "Renda" em Essenciais).
- Calcula a **sobra mensal**. O investimento conta como gasto.
- A tabela tem o mesmo **+/−** para ver o detalhe, e a sobra negativa aparece a vermelho.
- Criar, editar e apagar meses funciona como no Património, e os campos aceitam somas (ex.: `50+20+100`).

### Investimentos

- Cinco categorias fixas: **Ações Nacionais, Ações Mundiais, Cripto, Commodities e Caixa**.
- Cada posição tem nome, unidades, valor unitário e corretora. O valor total é calculado (unidades × valor unitário), e há subtotais por categoria e total geral.
- Mostra apenas os **valores atuais** (adicionar, editar e apagar posições).
- **Capturas (snapshots):** um botão guarda uma fotografia de todas as posições, com nota opcional. O **Histórico** lista as capturas com os totais por categoria e cada uma abre em modo só de leitura. As capturas são cópias, por isso não mudam se as posições forem alteradas depois.
- As capturas servem **apenas para consulta nesta página**. Todos os cálculos e a Home usam sempre os valores atuais.

### Dívidas

Tabela simples com: entidade de crédito, loja, item creditado, mensalidade, meses em falta, total em falta e dia acordado para pagamento.

- Mostra a **mensalidade total** de todos os créditos e o **valor total em dívida**.
- Os créditos com 0 meses em falta aparecem a cinzento e deixam de contar nos totais.

### Despesas Anuais Programadas

- Botão **Add** com os campos Data, Despesa e Valor (aceita somas).
- As despesas aparecem em **cards por mês**, apenas dos meses com despesas **por pagar**.
- Cada despesa tem uma caixa para marcar como paga. Quando todas as despesas de um mês estão pagas, o card desaparece.
- A ligação "Mostrar também meses já pagos" permite ver e corrigir meses completos.

### Campos com cálculo

Os campos de valor dos Relatórios, do Património e das Despesas Programadas aceitam expressões com `+ - * /` e parênteses, com vírgula ou ponto nos decimais. A expressão é guardada, por isso, ao editar, aparece de novo (ex.: `50+20+100`) para acrescentar mais uma parcela. A calculadora não usa `eval`: só aceita números e operadores.

---

## Como são feitos os cálculos

| Indicador | Cálculo |
|---|---|
| Total (património) | Dinheiro + Emergência + Investimentos do registo mensal |
| Total sem Emergência | Total − Emergência |
| Sobra do mês | Receita − Despesas essenciais − Despesas não essenciais − Investimento |
| Despesas (total) | Essenciais + Não essenciais + Investimento |
| Total em falta (dívida) | Mensalidade × meses em falta (só créditos com meses em falta) |
| Património líquido | Total do último registo de património − dívida total |
| Fundo de emergência (meses) | Emergência do último registo ÷ média mensal das despesas essenciais |
| Peso das dívidas na receita | Mensalidade total ÷ receita média mensal |
| Total investido | Soma de tudo o que foi registado na categoria Investimento dos relatórios |
| Valor atual dos investimentos | Soma de unidades × valor unitário das posições da página Investimentos |
| % do património (por tipo de investimento) | Valor do tipo ÷ (Dinheiro + Emergência do último registo + investimentos atuais) |
| Média anual | Média dos totais dos anos com registos (o ano em curso conta incompleto) |
| Sobra vs variação do património | Compara a variação do património com a sobra **antes de investir** (sobra + investido), apenas em meses consecutivos |

Notas:

- O dinheiro investido continua a ser património (só muda de conta para investimento), por isso a comparação com a variação do património usa a sobra antes de investir.
- O "total investido" só conta o que foi registado nos relatórios. Se existia dinheiro investido antes de começar a usar a app, esse valor não está incluído.

---

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Linguagem | Python (testado com 3.14) |
| Framework | Django 6.x |
| Base de dados | SQLite |
| Servidor (produção) | Gunicorn + WhiteNoise (ficheiros estáticos) |
| Gráficos | Chart.js 4 (ficheiro local, sem CDN) |
| Interface | Templates Django, CSS próprio (tema escuro) |
| Contentores | Docker e Docker Compose |

O SQLite chega bem para uso pessoal, mesmo com muitos anos de dados. Como o código usa o ORM do Django, passar para PostgreSQL no futuro é sobretudo uma mudança de configuração.

---

## Estrutura do projeto

```
MyFinance/
├── config/                  # Configuração do projeto
│   ├── settings.py
│   ├── urls.py
│   ├── calculos.py          # Calculadora segura (somas nos campos)
│   └── datas.py             # Seletor de mês/ano
├── home/                    # Página inicial (sem modelos; lê as outras apps)
│   └── management/commands/backup.py   # Comando de cópia de segurança
├── patrimonio/              # Registo Património
├── relatorios/              # Relatórios Mensais
├── investimentos/           # Investimentos e capturas
├── dividas/                 # Dívidas
├── programadas/             # Despesas Anuais Programadas
├── templates/               # base.html, login.html, seletor_mes.html
├── static/
│   ├── css/estilo.css       # Tema escuro
│   └── js/chart.umd.js      # Chart.js (local)
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── .env                     # Segredos (NÃO vai para o Git)
```

Cada página é uma app Django com os seus modelos, vistas, URLs e templates.

---

## Executar localmente (desenvolvimento)

Requisitos: Python 3.12 ou superior (testado com 3.14) e Git.

Em PowerShell (Windows):

```powershell
git clone <url-do-repositorio>
cd MyFinance

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000` e entra com o utilizador criado.

Se o PowerShell bloquear a ativação do ambiente virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Nas sessões seguintes basta abrir o terminal na pasta do projeto, ativar o ambiente virtual (`.venv\Scripts\Activate.ps1`) e correr `python manage.py runserver`.

Se o ficheiro `static/js/chart.umd.js` não existir, descarrega-o:

```powershell
mkdir static\js
Invoke-WebRequest "https://cdn.jsdelivr.net/npm/chart.js@4" -OutFile static\js\chart.umd.js
```

Em modo local a base de dados é o ficheiro `db.sqlite3` na raiz do projeto.

---

## Executar com Docker

É a forma recomendada para uso diário e para mudar de PC ou servidor. Requisito: Docker Desktop (Windows/Mac) ou Docker Engine com o plugin Compose (Linux).

**1. Criar o ficheiro `.env`** na raiz, com uma chave secreta própria:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

```
SECRET_KEY=cola-aqui-a-chave-gerada
```

**2. Construir e arrancar:**

```powershell
docker compose up -d --build
```

**3. Criar o utilizador:**

```powershell
docker compose exec web python manage.py createsuperuser
```

Abre `http://127.0.0.1:8000`.

Para levar uma base de dados existente (por exemplo, a do modo local), copia-a para o volume antes de entrar:

```powershell
docker compose stop
docker compose cp db.sqlite3 web:/data/db.sqlite3
docker compose start
```

### Comandos do dia a dia

| O que fazer | Comando |
|---|---|
| Parar / voltar a arrancar | `docker compose stop` / `docker compose start` |
| Aplicar alterações ao código | `docker compose up -d --build` |
| Ver mensagens e erros | `docker compose logs --tail 50` |
| Ver o estado | `docker compose ps` |
| Cópia de segurança | `docker compose exec web python manage.py backup` |
| Alterar uma palavra-passe | `docker compose exec web python manage.py changepassword <utilizador>` |

> **Atenção:** nunca uses `docker compose down -v`. A opção `-v` **apaga o volume com a base de dados**. O `docker compose down` sem `-v` é seguro.

### Como funciona

- A base de dados vive no volume Docker `dados` (ficheiro `/data/db.sqlite3` dentro do contentor), por isso sobrevive a atualizações e reconstruções.
- A pasta `backups` do projeto está ligada ao contentor, por isso as cópias aparecem no teu disco.
- O contentor corre `migrate` sempre que arranca e serve a app com Gunicorn.
- A porta 8000 só fica aberta para o próprio computador (`127.0.0.1`), não para a rede.
- Com `restart: unless-stopped`, a app volta a arrancar sozinha com o Docker. No Docker Desktop, ativa "Start Docker Desktop when you sign in" para ficar sempre disponível.

---

## Configuração (variáveis de ambiente)

Definidas no ficheiro `.env` (lido pelo `docker-compose.yml`) ou no ambiente do sistema.

| Variável | Valor por omissão | Descrição |
|---|---|---|
| `SECRET_KEY` | (obrigatória no Docker) | Chave secreta do Django. Tem de ser única e privada |
| `DEBUG` | `1` localmente, `0` no Docker | Modo de depuração. Nunca ativar em produção |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Endereços permitidos, separados por vírgulas |
| `CSRF_TRUSTED_ORIGINS` | vazio | Origens de confiança com HTTPS (ex.: `https://o.teu.dominio`) |
| `HTTPS` | `0` | Com `1`, ativa cookies seguros e o cabeçalho `X-Forwarded-Proto` (para uso atrás de um proxy HTTPS) |
| `DB_PATH` | `db.sqlite3` na raiz | Caminho do ficheiro da base de dados (no Docker: `/data/db.sqlite3`) |

---

## Cópias de segurança e restauro

### Criar uma cópia

```powershell
# No Docker
docker compose exec web python manage.py backup

# Em modo local
python manage.py backup
```

Cria `backups/db-AAAAMMDD-HHMMSS.sqlite3` usando o mecanismo de cópia do próprio SQLite (consistente mesmo com a app a funcionar) e mantém as 30 mais recentes. Opções: `--destino <pasta>` e `--manter <n>`.

### Cópias automáticas (Windows)

Cria um `backup.bat` na raiz:

```bat
@echo off
cd /d "%~dp0"
docker compose exec -T web python manage.py backup
```

No **Agendador de Tarefas**: criar tarefa básica → acionador semanal (ou diário) → ação "Iniciar um programa" → o `backup.bat`. Nas propriedades, em **Definições**, ativa "Executar a tarefa logo que possível após falha de um início agendado". O Docker Desktop tem de estar aberto.

### Restaurar uma cópia

```powershell
docker compose stop
docker compose cp backups/db-AAAAMMDD-HHMMSS.sqlite3 web:/data/db.sqlite3
docker compose start
```

Restaurar **substitui** a base de dados atual pela cópia.

### Boas práticas

- Guarda cópias **fora do computador** (disco externo ou cloud à tua escolha), porque a pasta `backups` não protege contra a avaria do disco.
- Testa o restauro de vez em quando.
- As cópias contêm dados financeiros, por isso trata-as como informação sensível.

---

## Mudar para outro PC ou servidor

1. Instala o Docker no destino.
2. Copia a pasta do projeto (sem `.venv`; ou faz `git clone`), o ficheiro **`.env`** (não está no Git) e uma cópia de segurança recente.
3. Constrói e arranca: `docker compose up -d --build`.
4. Restaura a base de dados: `docker compose stop`, `docker compose cp <cópia> web:/data/db.sqlite3`, `docker compose start`.

### Servidor acessível pela internet

Além dos passos anteriores:

- No `.env`, define `ALLOWED_HOSTS=o.teu.dominio`, `CSRF_TRUSTED_ORIGINS=https://o.teu.dominio` e `HTTPS=1`.
- Põe um **proxy com HTTPS** à frente (por exemplo Caddy ou nginx) a encaminhar para `127.0.0.1:8000`. **Não** exponhas a porta 8000 diretamente, porque o login iria em texto simples.
- Usa uma palavra-passe forte e guarda as cópias de segurança fora do servidor.

---

## Segurança

- Todas as páginas exigem login (`LoginRequiredMiddleware` do Django).
- A app foi pensada para um único utilizador: **todos os utilizadores veem os mesmos dados** (os modelos não têm "dono"). Quem precisar de dados separados deve usar uma instalação (e base de dados) por pessoa.
- **Nunca** enviar para o Git: `.env`, `db.sqlite3` e a pasta `backups/` (já estão no `.gitignore`).
- Gerar uma `SECRET_KEY` própria para cada instalação.
- As operações de apagar usam `POST` com confirmação.

---

## Resolução de problemas

| Sintoma | O que fazer |
|---|---|
| `error during connect` / daemon não está a correr | Abrir o Docker Desktop e esperar que fique ativo |
| `required variable SECRET_KEY is missing` | Criar o `.env` na raiz (ao lado do `docker-compose.yml`) com `SECRET_KEY=...` |
| `port is already allocated` / endereço já em uso | Parar o `runserver` local (`Ctrl+C`) ou outra aplicação na porta 8000 |
| Página sem estilos | Confirmar que o `WhiteNoiseMiddleware` está no `MIDDLEWARE` e refazer `docker compose up -d --build` |
| `Bad Request (400)` | Aceder por `127.0.0.1:8000` ou `localhost:8000`, ou ajustar `ALLOWED_HOSTS` |
| Gráficos em branco na Home | Confirmar que existe `static/js/chart.umd.js` e ver erros na consola do browser (`F12`) |
| `no such table` | Faltam migrações: `python manage.py makemigrations` e `python manage.py migrate` (no Docker, reiniciar o contentor aplica as migrações) |
| `Unknown command: 'backup'` | Confirmar a estrutura `home/management/commands/backup.py` e os dois `__init__.py` vazios |
| Outro erro | `docker compose logs --tail 50` |

---

## Desenvolvimento

- Depois de alterar **modelos**, gerar e aplicar migrações: `python manage.py makemigrations <app>` e `python manage.py migrate`. Executar um comando de cada vez.
- Depois de alterar o código em Docker: `docker compose up -d --build`.
- O `runserver` local usa o `db.sqlite3` da raiz, que é independente da base de dados do Docker. Usa-o só para testar alterações.
- Para acrescentar uma página nova: criar a app (`python manage.py startapp <nome>`), registá-la em `INSTALLED_APPS`, ligar as URLs em `config/urls.py` e acrescentar o link no menu de `templates/base.html`. Os campos de valor podem reutilizar `config.calculos.calcular` para aceitarem somas.
- Estilos: `static/css/estilo.css` (variáveis de cor no início do ficheiro). Os gráficos da Home estão no `<script>` de `home/templates/home/home.html`.

---

## Licença

Ver o ficheiro [LICENSE](LICENSE).