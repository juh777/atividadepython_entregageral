# Projeto Integrador — Crescimento Demográfico (Persona: Prefeitos de Capitais)
## Painel Integrado do Grupo

Este repositório junta as 5 entregas individuais em **um único dashboard Streamlit**,
navegável por uma barra lateral, incluindo uma página inicial de **identificação do
grupo**. Cada integrante tem sua própria seção, com um comentário no início do código
explicando o que ela faz e qual a fonte de dados utilizada.

| Integrante | Indicador | Repositório individual original |
|---|---|---|
| **Bernardo** | Taxa de crescimento populacional acumulada por cidade | [github.com/Bernardpxl/Projeto-Integrado----Entrega-Individual](https://github.com/Bernardpxl/Projeto-Integrado----Entrega-Individual) |
| **Hugo** | Recorte por Faixa Etária e Pirâmide Populacional | [github.com/hugo-srz/-Recorte-por-Faixa-Et-ria-e-Pir-mide-Populacional](https://github.com/hugo-srz/-Recorte-por-Faixa-Et-ria-e-Pir-mide-Populacional) |
| **Luan** | Recorte por Gênero e Composição Demográfica | [github.com/Luancostaf/Recorte_por_G-nero_e_Composi-o_Demogr-fica](https://github.com/Luancostaf/Recorte_por_G-nero_e_Composi-o_Demogr-fica) |
| **Júlia** | Identificação de Cidades Outliers | [github.com/juh777/-Identifica-o-de-Cidades-Outliers](https://github.com/juh777/-Identifica-o-de-Cidades-Outliers) |
| **Salomé** | Projeções de Envelhecimento Populacional e Infraestrutura | [github.com/Matheusslom/Proje-es-de-Envelhecimento-Populacional-e-Infraestrutura](https://github.com/Matheusslom/Proje-es-de-Envelhecimento-Populacional-e-Infraestrutura) |

## Conteúdo

- `app.py` → arquivo único com 6 seções: **Identificação do grupo** + uma função
  `secao_<nome>()` por integrante (lógica e gráficos de cada um preservados, com um
  comentário no topo explicando o que aquela parte faz) e um menu de navegação na
  barra lateral que alterna entre elas.
- `estatisticas.py` → módulo de funções estatísticas (média, mediana, moda, quartis,
  IQR, amplitude, variância, desvio padrão, detecção de outliers), usado por **todas**
  as 5 seções.
- `dados/` → bases reais do Censo IBGE (2010/2022 e 1980–2022) usadas por todas as
  seções.
- `requirements.txt` → todas as bibliotecas necessárias para rodar as 5 seções juntas
  (inclui `altair`, usado na seção do Luan).
- `relatorio_grupo.pdf` → relatório do grupo (2 páginas): tema, persona, objetivo,
  metodologia, indicadores de cada integrante e principais conclusões — entregável
  exigido pela rubrica do projeto.

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O navegador abre em `http://localhost:8501`. Use o menu na barra lateral para alternar
entre a identificação do grupo e as 5 partes do indicador.

## Sobre os dados (atualizado na entrega do grupo)

Todas as 5 seções usam dados reais do **Censo Demográfico do IBGE**:

- **Bernardo** → Censo 2010/2022 (taxa de crescimento acumulada das 27 capitais).
- **Hugo** → Censo 2022 (população por idade e sexo — pirâmide etária).
- **Luan** → Censo 2022 (razão de sexo por capital, convertida em população estimada
  de homens e mulheres); o upload de um CSV próprio e os dados de exemplo originais
  continuam disponíveis como opções alternativas na barra lateral.
- **Júlia** → Censo 2010/2022 (taxa de crescimento das 27 capitais).
- **Salomé** → Censo 1980–2022 (índice de envelhecimento).

Nas versões individuais que cada integrante publicou em seu próprio repositório
(ver tabela acima), o Bernardo e o Luan usam, por padrão, dados simulados — isso
está preservado nos repositórios individuais de cada um (entrega já feita), e foi
ajustado apenas **aqui, no painel integrado do grupo**, para usar a base real do
IBGE em todas as seções.

## Passo a passo para subir este painel integrado no GitHub

1. Crie um repositório novo (ex.: `projeto-integrador-crescimento-demografico-GRUPO`).
2. Faça upload de todos os arquivos desta pasta (`app.py`, `estatisticas.py`,
   `requirements.txt`, `README.md`, `relatorio_grupo.pdf` e a pasta `dados/` inteira).
3. Entregue o link deste repositório conforme combinado para a etapa de integração
   do grupo (dia 12).
