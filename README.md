# 🎲 Gerador Inteligente Lotofácil

![Demonstração da Aplicação](https://i.imgur.com/link_para_sua_imagem.png) 
*(Sugestão: tire um print screen da sua aplicação em funcionamento, suba para um site como o [Imgur](https://imgur.com/upload) e cole o link aqui para ter uma imagem de demonstração)*

> Uma aplicação web desenvolvida em Flask que utiliza análise estatística e filtros inteligentes para gerar jogos otimizados para a Lotofácil, aumentando as chances de acerto.

---

## 🚀 Funcionalidades Principais

*   **Geração Ponderada:** Gera jogos utilizando pesos baseados na **frequência histórica** e no **atraso** de cada número.
*   **Filtros Inteligentes:** Permite filtrar os jogos gerados com base nos padrões mais comuns em sorteios vencedores:
    *   Balanço de **Pares e Ímpares** (ex: 7 a 9 números ímpares).
    *   **Soma das Dezenas** (jogos cuja soma total fica entre 185 e 205).
    *   Distribuição entre **Moldura e Miolo**.
*   **Análise de Desempenho:** Para cada jogo gerado, a aplicação verifica o histórico completo de sorteios e informa quantas vezes aquela combinação já teria feito 11, 12, 13, 14 ou 15 pontos.
*   **Visualização de Dados:** Apresenta gráficos sobre a frequência de cada número e a distribuição da soma das dezenas, ajudando o usuário a entender as estatísticas.
*   **Interface Limpa e Intuitiva:** Interface amigável para selecionar as estratégias e visualizar os resultados.

---

## 🛠️ Tecnologias Utilizadas

*   **Backend:** Python
*   **Framework Web:** Flask
*   **Análise de Dados:** Pandas, NumPy
*   **Visualização de Dados:** Matplotlib, Seaborn
*   **Frontend:** HTML5, CSS3

---

## ⚙️ Como Executar o Projeto Localmente

Siga os passos abaixo para rodar a aplicação no seu computador.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/JonesViegas/gerador-lotofacil-inteligente.git
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd gerador-lotofacil-inteligente
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    # Crie o ambiente
    python -m venv venv

    # Ative o ambiente (Windows)
    .\venv\Scripts\activate

    # Ative o ambiente (Linux/macOS)
    # source venv/bin/activate
    ```

4.  **Instale as dependências:**
    O arquivo `requirements.txt` contém todas as bibliotecas necessárias.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Verifique o arquivo de dados:**
    Certifique-se de que o arquivo `Lotofácil.xlsx` com o histórico dos sorteios está presente na pasta raiz do projeto.

6.  **Execute a aplicação:**
    ```bash
    python app.py
    ```

7.  **Acesse no navegador:**
    Abra seu navegador e acesse o endereço `http://127.0.0.1:5000`.

---

## 📂 Estrutura do Projeto


.
├── static/ # Arquivos estáticos (imagens, favicon)

├── templates/

│ └── index.html # Template principal da aplicação

├── .gitignore # Arquivos e pastas a serem ignorados pelo Git

├── app.py # Lógica principal da aplicação Flask

├── Lotofácil.xlsx # Banco de dados com o histórico dos sorteios

├── requirements.txt # Lista de dependências Python

└── README.md # Este arquivo


---

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. (Você pode criar um arquivo LICENSE se desejar, mas para portfólio não é estritamente necessário).

---

## ✨ Autor

Desenvolvido por **Jones Carlos Viegas**.