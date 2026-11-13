"""
Projeto Integrador — "Números que Falam: Descobrindo o Brasil"
Tema do Grupo: Crescimento Demográfico (Persona: Prefeitos de Capitais)

PAINEL INTEGRADO DO GRUPO — reúne as 5 partes individuais em um único
dashboard Streamlit, navegável pela barra lateral.

Integrantes e indicadores (código original de cada um, ver comentário
no início de cada função "secao_*" abaixo):
  - Bernardo -> Taxa de crescimento populacional acumulada por cidade
  - Hugo     -> Recorte por Faixa Etária e Pirâmide Populacional
  - Luan     -> Recorte por Gênero e Composição Demográfica
  - Júlia    -> Identificação de Cidades Outliers
  - Salomé   -> Projeções de Envelhecimento Populacional e Infraestrutura

Como rodar localmente:
    pip install -r requirements.txt
    streamlit run app.py
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from estatisticas import resumo_estatistico, detectar_outliers, classificar_outlier, formatar_numero

st.set_page_config(
    page_title="Crescimento Demográfico — Painel Integrado do Grupo",
    page_icon="🏙️",
    layout="wide",
)

def secao_bernardo():
    """
    ====================================================================
    BERNARDO — Taxa de crescimento populacional acumulada por cidade
    ====================================================================
    O que esta seção faz:
    Calcula a taxa de crescimento populacional acumulada (2010→2022) por
    capital, com estatísticas descritivas completas (média, mediana,
    moda, quartis, IQR, amplitude, variância e desvio padrão) e
    detecção de outliers pela regra 1,5×IQR, exibidos em gráfico de
    barras, histograma/boxplot e em um resumo executivo.

    Observação de transparência: a estrutura e a lógica desta seção são
    as mesmas publicadas pelo Bernardo em seu repositório individual
    (github.com/Bernardpxl/Projeto-Integrado----Entrega-Individual), que
    originalmente usava dados SIMULADOS (numpy.random, semente 42) com
    10 capitais. Para a entrega do GRUPO, a fonte de dados foi trocada
    aqui pela base real do Censo IBGE 2010/2022 das 27 capitais (a
    mesma base usada pela Júlia), para atender à exigência da rubrica
    de usar dados reais do SIDRA/IBGE — e também completadas as
    estatísticas (moda, quartis e variância) e o gráfico de distribuição
    (histograma/boxplot) que faltavam no código original.
    ====================================================================
    """

    import numpy as np
    import pandas as pd
    import streamlit as st
    import plotly.express as px

    # (st.set_page_config já foi definido uma única vez no topo deste arquivo integrado)

    st.title("🏙️ Taxa de Crescimento Populacional Acumulada por Cidade")
    st.markdown(
        "Módulo individual voltado para o apoio aos Prefeitos de Capitais na revisão de Planos Diretores."
    )

    @st.cache_data
    def carregar_dados():
        df = pd.read_csv("dados/capitais_crescimento_2010_2022.csv")
        df = df.rename(columns={
            "cidade": "Municipio",
            "uf": "UF",
            "regiao": "Regiao",
            "taxa_crescimento_pct": "Taxa_Crescimento_Anual",
            "populacao_2022": "Populacao_2022",
        })
        return df

    df = carregar_dados()

    st.sidebar.header("🔍 Filtros de Análise")
    regiao_selecionada = st.sidebar.selectbox(
        "Selecione a Região", options=["Todas"] + sorted(df["Regiao"].dropna().unique().tolist()),
        key="bernardo_regiao",
    )
    if regiao_selecionada != "Todas":
        df_regiao = df[df["Regiao"] == regiao_selecionada]
    else:
        df_regiao = df

    uf_selecionada = st.sidebar.selectbox(
        "Selecione a UF", options=["Todas"] + sorted(df_regiao["UF"].dropna().unique().tolist()),
        key="bernardo_uf",
    )
    if uf_selecionada != "Todas":
        df_filtrado = df_regiao[df_regiao["UF"] == uf_selecionada]
    else:
        df_filtrado = df_regiao

    taxas = df_filtrado["Taxa_Crescimento_Anual"]
    stats = resumo_estatistico(taxas)

    media = stats["media"]
    mediana = stats["mediana"]
    moda = stats["moda"]
    q1 = stats["q1"]
    q3 = stats["q3"]
    iqr = stats["iqr"]
    amplitude = stats["amplitude"]
    desvio_padrao = stats["desvio_padrao"]
    variancia = stats["variancia"]

    limite_inferior = stats["limite_inferior_outlier"]
    limite_superior = stats["limite_superior_outlier"]
    outliers = df_filtrado[
        (taxas < limite_inferior) | (taxas > limite_superior)
    ]

    st.subheader("📊 Métricas Estatísticas do Indicador (2010→2022)")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Média", f"{formatar_numero(media)}%")
    col2.metric("Mediana", f"{formatar_numero(mediana)}%")
    col3.metric("Moda", f"{formatar_numero(moda)}%" if moda is not None else "—")
    col4.metric("Desvio Padrão", formatar_numero(desvio_padrao))

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Q1 (25%)", f"{formatar_numero(q1)}%")
    col6.metric("Q3 (75%)", f"{formatar_numero(q3)}%")
    col7.metric("IQR", formatar_numero(iqr))
    col8.metric("Variância", formatar_numero(variancia))

    st.caption(f"Amplitude (máx − mín): **{formatar_numero(amplitude)} p.p.** • n = {stats['n']} capitais")

    st.markdown("---")
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Gráfico de Barras: Crescimento por Cidade")
        st.bar_chart(df_filtrado.set_index("Municipio")["Taxa_Crescimento_Anual"])

    with col_g2:
        st.subheader("Distribuição da Taxa de Crescimento (Boxplot)")
        fig_box = px.box(
            df_filtrado, y="Taxa_Crescimento_Anual", points="all",
            hover_data=["Municipio"],
            labels={"Taxa_Crescimento_Anual": "Taxa de crescimento acumulada (%)"},
        )
        fig_box.update_layout(height=350)
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("Histograma: Frequência das taxas de crescimento")
    fig_hist = px.histogram(
        df_filtrado, x="Taxa_Crescimento_Anual", nbins=8,
        labels={"Taxa_Crescimento_Anual": "Taxa de crescimento acumulada (%)"},
    )
    fig_hist.update_layout(height=300)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.subheader("🎯 Ranking: Cidades que mais cresceram / encolheram")
    df_rank = df_filtrado.sort_values("Taxa_Crescimento_Anual", ascending=False)
    st.dataframe(
        df_rank[["Municipio", "UF", "Regiao", "Taxa_Crescimento_Anual"]].rename(
            columns={"Taxa_Crescimento_Anual": "Crescimento 2010→2022 (%)"}
        ),
        use_container_width=True, hide_index=True,
    )

    st.subheader("Análise de Outliers (Cidades Anômalas)")
    if not outliers.empty:
        st.warning(
            "Foram identificadas cidades fora do padrão de normalidade estatística ($1.5 \\times IQR$):"
        )
        st.dataframe(
            outliers[["Municipio", "Regiao", "Taxa_Crescimento_Anual"]]
        )
    else:
        st.success(
            "Não há outliers com base no filtro e na regra estatística aplicada."
        )

    st.markdown("---")
    st.subheader("📰 Contextualização e Transição Demográfica")
    st.markdown(
        f"""
        > **Resumo Executivo para Gestores:** Entre 2010 e 2022, a taxa de crescimento acumulada das capitais
        > selecionadas teve mediana de **{formatar_numero(mediana)}%**, com dispersão (IQR) de
        > **{formatar_numero(iqr)} p.p.** A maior parte das capitais converge para um crescimento moderado,
        > enquanto polos específicos (ver ranking e outliers acima) sofrem com desvios acentuados devido à
        > expansão urbana acelerada ou ao esvaziamento demográfico.
        """
    )
    st.caption("Fonte dos dados: IBGE, Censo Demográfico 2010 e 2022 (taxa de crescimento acumulada por capital).")



def secao_hugo():
    """
    ====================================================================
    HUGO — Recorte por Faixa Etária e Pirâmide Populacional
    ====================================================================
    O que esta seção faz:
    Monta a pirâmide etária aproximada (0–14, 15–64, 65+ anos) de cada
    uma das 5 capitais da persona, com estatística descritiva do
    percentual de idosos entre as capitais, detecção de outliers de
    envelhecimento e a evolução histórica da estrutura etária de
    1980 a 2022, usando dados reais do Censo IBGE 2022 (população por
    idade e sexo).
    Código original: github.com/hugo-srz/-Recorte-por-Faixa-Et-ria-e-Pir-mide-Populacional
    ====================================================================
    """

    """
    Projeto Integrador — "Números que Falam: Descobrindo o Brasil"
    Tema do Grupo: Crescimento Demográfico (Persona: Prefeitos de Capitais)

    Integrante: HUGO
    Indicador individual: Recorte por Faixa Etária e Pirâmide Populacional
    Fonte: IBGE, Censo Demográfico 2022 — População por idade e sexo (resultados do universo,
    publicação por Unidade da Federação, usada como melhor proxy disponível para a capital).

    Como rodar localmente:
        pip install -r requirements.txt
        streamlit run app.py
    """

    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    import streamlit as st

    from estatisticas import resumo_estatistico, detectar_outliers, classificar_outlier, formatar_numero

    # (st.set_page_config já foi definido uma única vez no topo deste arquivo integrado)

    CAMINHO_DADOS_PADRAO = "dados/estrutura_etaria_uf_capitais.csv"

    # --------------------------------------------------------------------------------------
    # ETL
    # --------------------------------------------------------------------------------------
    @st.cache_data
    def carregar_dados_padrao() -> pd.DataFrame:
        return pd.read_csv(CAMINHO_DADOS_PADRAO)


    def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]
        for c in ["pct_0_14", "pct_15_64", "pct_65_mais", "indice_envelhecimento", "idade_mediana", "razao_sexo_capital", "ano"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df


    st.sidebar.title("⚙️ Filtros")
    st.sidebar.caption("Projeto Integrador • Faixa Etária e Pirâmide Populacional")

    arquivo = st.sidebar.file_uploader("Upload da base IBGE (CSV ou XLSX)", type=["csv", "xlsx"])
    if arquivo is not None:
        try:
            df_bruto = pd.read_excel(arquivo) if arquivo.name.endswith(".xlsx") else pd.read_csv(arquivo)
            st.sidebar.success("Arquivo carregado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler o arquivo: {e}")
            df_bruto = carregar_dados_padrao()
    else:
        df_bruto = carregar_dados_padrao()
        st.sidebar.info("Usando a base padrão do IBGE (Censo 2022 — população por idade e sexo).")

    df = tratar_dados(df_bruto)

    capitais = sorted(df["capital"].dropna().unique().tolist())
    capital_sel = st.sidebar.selectbox("Capital (persona)", capitais, index=capitais.index("Curitiba") if "Curitiba" in capitais else 0)

    anos_disp = sorted(df["ano"].dropna().unique().tolist())
    ano_sel = st.sidebar.select_slider("Ano do Censo", options=anos_disp, value=max(anos_disp))

    comparar = st.sidebar.multiselect(
        "Comparar outras capitais (série histórica)", [c for c in capitais if c != capital_sel], default=[]
    )

    df_capital = df[df["capital"] == capital_sel]
    linha_ano = df_capital[df_capital["ano"] == ano_sel]
    if linha_ano.empty:
        st.warning("Sem dado para este ano/capital.")
        st.stop()
    linha_ano = linha_ano.iloc[0]

    # --------------------------------------------------------------------------------------
    # CABEÇALHO
    # --------------------------------------------------------------------------------------
    PERSONAS = {
        "Curitiba": "Carlos (Prefeito de Curitiba)", "Porto Alegre": "Eduardo (Prefeito de Porto Alegre)",
        "Belo Horizonte": "Elisa (Prefeita de Belo Horizonte)", "Salvador": "Jorge (Prefeito de Salvador)",
        "Florianopolis": "Roberto (Prefeito de Florianópolis)",
    }
    st.title("🧓 Recorte por Faixa Etária e Pirâmide Populacional")
    st.caption(
        f"Startup de Análise de Dados • Consultoria para {PERSONAS.get(capital_sel, capital_sel)} • "
        f"Censo IBGE {ano_sel} • Responsável: **Hugo**"
    )

    with st.expander("📋 Cenário da persona (clique para ler)"):
        st.markdown(
            """
            Os prefeitos das capitais precisam entender o **envelhecimento populacional** para
            redesenhar a alocação orçamentária entre creches/escolas (base da pirâmide) e
            UBS/centros de convivência para idosos (topo da pirâmide).
            """
        )

    # --------------------------------------------------------------------------------------
    # KPIs
    # --------------------------------------------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("0 a 14 anos", f"{formatar_numero(linha_ano['pct_0_14'])}%")
    c2.metric("15 a 64 anos", f"{formatar_numero(linha_ano['pct_15_64'])}%")
    c3.metric("65 anos ou mais", f"{formatar_numero(linha_ano['pct_65_mais'])}%")
    idade_med = linha_ano.get("idade_mediana")
    c4.metric("Idade mediana (UF)", f"{int(idade_med)} anos" if pd.notna(idade_med) else "-")

    # --------------------------------------------------------------------------------------
    # ESTATÍSTICA DESCRITIVA (sobre as 5 capitais no ano selecionado)
    # --------------------------------------------------------------------------------------
    st.subheader(f"📊 Resumo estatístico — % de idosos (65+) entre as 5 capitais em {ano_sel}")
    df_ano = df[df["ano"] == ano_sel]
    stats = resumo_estatistico(df_ano["pct_65_mais"])
    if stats:
        cA, cB, cC, cD, cE = st.columns(5)
        cA.metric("Média", f"{formatar_numero(stats['media'])}%")
        cB.metric("Mediana", f"{formatar_numero(stats['mediana'])}%")
        cC.metric("Q1 / Q3", f"{formatar_numero(stats['q1'])}% / {formatar_numero(stats['q3'])}%")
        cD.metric("IQR", f"{formatar_numero(stats['iqr'])}%")
        cE.metric("Desvio padrão", f"{formatar_numero(stats['desvio_padrao'])}%")

        outliers = detectar_outliers(df_ano, "pct_65_mais")
        if not outliers.empty:
            st.warning(
                "Capital(is) com estrutura etária **estatisticamente atípica** (regra 1,5×IQR): "
                + ", ".join(outliers["capital"].tolist())
            )
        else:
            st.success("Nenhuma capital é outlier de envelhecimento nesta seleção (1,5×IQR).")

    # --------------------------------------------------------------------------------------
    # PIRÂMIDE POPULACIONAL (aproximada a partir dos grandes grupos etários + razão de sexo)
    # --------------------------------------------------------------------------------------
    st.subheader(f"🔺 Pirâmide Populacional Aproximada — {capital_sel} ({ano_sel})")
    st.caption(
        "⚠️ Aproximação metodológica: o IBGE não publica o corte por idade simples e sexo em nível "
        "municipal nesta divulgação; a pirâmide abaixo distribui os 3 grandes grupos etários "
        "(0–14, 15–64, 65+) do município pela razão de sexo divulgada para a capital."
    )

    razao_sexo = linha_ano.get("razao_sexo_capital")
    if pd.notna(razao_sexo):
        frac_masc = razao_sexo / (100 + razao_sexo)  # homens / (homens+mulheres)
    else:
        frac_masc = 0.485  # média nacional 2022 como fallback

    grupos = ["0–14 anos", "15–64 anos", "65+ anos"]
    pcts = [linha_ano["pct_0_14"], linha_ano["pct_15_64"], linha_ano["pct_65_mais"]]
    homens = [-p * frac_masc for p in pcts]
    mulheres = [p * (1 - frac_masc) for p in pcts]

    fig_piramide = go.Figure()
    fig_piramide.add_trace(go.Bar(y=grupos, x=homens, orientation="h", name="Homens", marker_color="#1f77b4"))
    fig_piramide.add_trace(go.Bar(y=grupos, x=mulheres, orientation="h", name="Mulheres", marker_color="#e377c2"))
    fig_piramide.update_layout(
        barmode="overlay", bargap=0.1, title=f"Pirâmide etária — {capital_sel}, {ano_sel}",
        xaxis_title="% da população (homens à esquerda / mulheres à direita)", height=420,
    )
    st.plotly_chart(fig_piramide, use_container_width=True)

    # --------------------------------------------------------------------------------------
    # SÉRIE HISTÓRICA — ESTREITAMENTO DA BASE / ALARGAMENTO DO TOPO
    # --------------------------------------------------------------------------------------
    st.subheader("📈 Evolução da estrutura etária (1980–2022)")
    capitais_para_grafico = [capital_sel] + comparar
    df_hist = df[df["capital"].isin(capitais_para_grafico)]

    tab1, tab2 = st.tabs(["Evolução por faixa (capital selecionada)", "Comparar % de idosos entre capitais"])

    with tab1:
        df_long = df[df["capital"] == capital_sel].melt(
            id_vars=["ano"], value_vars=["pct_0_14", "pct_15_64", "pct_65_mais"],
            var_name="faixa", value_name="percentual",
        )
        nomes = {"pct_0_14": "0–14 anos", "pct_15_64": "15–64 anos", "pct_65_mais": "65+ anos"}
        df_long["faixa"] = df_long["faixa"].map(nomes)
        fig_linha = px.line(
            df_long, x="ano", y="percentual", color="faixa", markers=True,
            labels={"ano": "Ano do Censo", "percentual": "% da população", "faixa": "Faixa etária"},
            title=f"{capital_sel}: estreitamento da base e alargamento do topo da pirâmide",
        )
        st.plotly_chart(fig_linha, use_container_width=True)

    with tab2:
        fig_comp = px.line(
            df_hist, x="ano", y="pct_65_mais", color="capital", markers=True,
            labels={"ano": "Ano do Censo", "pct_65_mais": "% da população com 65+ anos", "capital": "Capital"},
            title="Envelhecimento comparado entre capitais",
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # --------------------------------------------------------------------------------------
    # RESPOSTA ÀS PERGUNTAS DE NEGÓCIO
    # --------------------------------------------------------------------------------------
    st.subheader("💼 Resposta às Perguntas de Negócio da Persona")
    mais_velha = df_ano.loc[df_ano["pct_65_mais"].idxmax()]
    mais_jovem = df_ano.loc[df_ano["pct_65_mais"].idxmin()]
    st.markdown(
        f"""
    1. **Como está estruturada a pirâmide etária de {capital_sel}?**
       Em {ano_sel}, {formatar_numero(linha_ano['pct_0_14'])}% da população tem até 14 anos,
       {formatar_numero(linha_ano['pct_15_64'])}% está em idade ativa (15–64) e
       {formatar_numero(linha_ano['pct_65_mais'])}% tem 65 anos ou mais — uma base que se
       estreitou e um topo que se alargou desde 1980, confirmando a transição demográfica.

    2. **Qual capital está mais/menos envelhecida?**
       **{mais_velha['capital']}** tem a maior proporção de idosos ({formatar_numero(mais_velha['pct_65_mais'])}%)
       entre as 5 capitais da persona, enquanto **{mais_jovem['capital']}** tem a menor
       ({formatar_numero(mais_jovem['pct_65_mais'])}%) — útil para priorizar investimento em
       UBS geriátricas versus creches/escolas conforme o perfil de cada município.
        """
    )

    # --------------------------------------------------------------------------------------
    # CONTEÚDO ADICIONAL
    # --------------------------------------------------------------------------------------
    st.subheader("📰 Conteúdo adicional — Envelhecimento da população brasileira")
    st.markdown(
        """
        **🔗 Censo 2022: número de pessoas com 65 anos ou mais de idade cresceu 57,4% em 12 anos**
        *IBGE Agência de Notícias* — detalha o avanço do índice de envelhecimento (de 30,7 para 55,2)
        e da idade mediana (de 29 para 35 anos) no país.
        [Ler reportagem](https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-denoticias/noticias/38186-)
        """
    )

    st.divider()
    st.caption(
        "Fonte dos dados: IBGE, Censo Demográfico 2022 — População por idade e sexo (resultados do universo). "
        "Desenvolvido por Hugo • Projeto Integrador — Python & Matemática."
    )



def secao_luan():
    """
    ====================================================================
    LUAN — Recorte por Gênero e Composição Demográfica
    ====================================================================
    O que esta seção faz:
    Permite recortar uma base por coluna de Gênero e por coluna de
    Composição Demográfica, calcula estatísticas descritivas completas
    (média, mediana, moda, quartis, IQR, amplitude, variância e desvio
    padrão) da variável numérica escolhida, detecta outliers (regra
    1,5×IQR) e visualiza a distribuição em boxplot (Altair) e
    histograma, além de um ranking territorial e um texto interpretativo.

    Observação de transparência: a lógica de recorte, os filtros e os
    gráficos (boxplot/histograma) são os mesmos publicados pelo Luan em
    seu repositório individual (github.com/Luancostaf/Recorte_por_G-nero
    _Composi-o_Demogr-fica), que por padrão usava uma base de dados de
    EXEMPLO gerada aleatoriamente (500 registros simulados). Para a
    entrega do GRUPO, foi adicionada aqui uma terceira opção de fonte de
    dados com a base REAL do Censo IBGE 2022 (razão de sexo por capital,
    convertida em população estimada de homens e mulheres), para
    atender à exigência da rubrica de usar dados reais do IBGE — e
    foram completadas as estatísticas (moda, amplitude, desvio padrão e
    variância), o ranking territorial e o texto interpretativo que
    faltavam no código original.
    ====================================================================
    """

    import numpy as np
    import pandas as pd
    import streamlit as st

    # Configuração da página do Streamlit
    # (st.set_page_config já foi definido uma única vez no topo deste arquivo integrado)

    st.title("📊 Análise Demográfica: Filtros, Estatísticas e Outliers")
    st.markdown(
        "Este aplicativo realiza o recorte por **Gênero** e **Composição"
        " Demográfica**, calcula estatísticas descritivas e detecta *outliers*"
        " (valores discrepantes)."
    )

    # 1. Carregamento dos Dados
    @st.cache_data
    def carregar_dados_exemplo():
      np.random.seed(42)
      n = 500
      dados = {
          "ID": range(1, n + 1),
          "Genero": np.random.choice(
              ["Feminino", "Masculino", "Outro"], size=n, p=[0.48, 0.48, 0.04]
          ),
          "Composicao_Demografica": np.random.choice(
              ["Urbana Central", "Urbana Periférica", "Rural"],
              size=n,
              p=[0.5, 0.3, 0.2],
          ),
          "Renda": np.random.lognormal(mean=8, sigma=0.8, size=n) * 100,
          "Idade": np.random.randint(18, 75, size=n),
      }
      return pd.DataFrame(dados)

    @st.cache_data
    def carregar_dados_ibge_reais():
        # Censo IBGE 2022 — razão de sexo por capital, convertida em população
        # estimada de homens e mulheres (ver dados/composicao_genero_capitais.csv).
        return pd.read_csv("dados/composicao_genero_capitais.csv")

    st.sidebar.header("📁 Fonte de Dados")
    opcao_dados = st.sidebar.radio(
        "Escolha a fonte:",
        ("Usar dados reais do IBGE (capitais)", "Usar dados de exemplo", "Fazer upload de arquivo CSV"),
    )

    if opcao_dados == "Fazer upload de arquivo CSV":
      arquivo_upload = st.sidebar.file_uploader("Envie seu arquivo CSV", type=["csv"])
      if arquivo_upload is not None:
        df = pd.read_csv(arquivo_upload)
      else:
        st.info("Por favor, envie um arquivo CSV ou mude para os dados de exemplo.")
        st.stop()
    elif opcao_dados == "Usar dados reais do IBGE (capitais)":
      df = carregar_dados_ibge_reais()
      st.sidebar.success("Usando dados reais do Censo IBGE 2022 (5 capitais da persona).")
    else:
      df = carregar_dados_exemplo()

    # 2. Configuração dos Recortes (Filtros)
    st.sidebar.header("🔍 Recorte e Filtros")

    colunas_categoricas = df.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    if not colunas_categoricas:
      st.error("O DataFrame não possui colunas categóricas para os recortes.")
      st.stop()

    opcoes_genero_padrao = [
        c for c in colunas_categoricas if "genero" in c.lower() or "sexo" in c.lower()
    ]
    col_genero = st.sidebar.selectbox(
        "Selecione a coluna de Gênero:",
        colunas_categoricas,
        index=(
            colunas_categoricas.index(opcoes_genero_padrao[0])
            if opcoes_genero_padrao
            else 0
        ),
    )

    generos_disponiveis = df[col_genero].dropna().unique().tolist()
    generos_selecionados = st.sidebar.multiselect(
        "Filtrar por Gênero:",
        options=generos_disponiveis,
        default=generos_disponiveis,
    )

    opcoes_demog_padrao = [
        c
        for c in colunas_categoricas
        if "demograf" in c.lower() or "regiao" in c.lower() or "local" in c.lower()
    ]
    col_demografia = st.sidebar.selectbox(
        "Selecione a coluna de Composição Demográfica:",
        colunas_categoricas,
        index=(
            colunas_categoricas.index(opcoes_demog_padrao[0])
            if opcoes_demog_padrao
            else (1 if len(colunas_categoricas) > 1 else 0)
        ),
    )

    demografias_disponiveis = df[col_demografia].dropna().unique().tolist()
    demografias_selecionadas = st.sidebar.multiselect(
        "Filtrar por Composição Demográfica:",
        options=demografias_disponiveis,
        default=demografias_disponiveis,
    )

    df_filtrado = df[
        df[col_genero].isin(generos_selecionados)
        & df[col_demografia].isin(demografias_selecionadas)
    ]

    st.subheader("📋 Dados Filtrados")
    st.write(
        f"Mostrando **{len(df_filtrado)}** de **{len(df)}** registros totais após o"
        " recorte."
    )
    st.dataframe(df_filtrado.head(10), use_container_width=True)

    # 3. Escolha da Variável Numérica para Análise
    colunas_numericas = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    if not colunas_numericas:
      st.warning("Não há colunas numéricas disponíveis para calcular estatísticas.")
      st.stop()

    st.sidebar.header("📈 Variável de Análise")
    col_analise = st.sidebar.selectbox(
        "Selecione a métrica numérica:", colunas_numericas
    )

    # 4. Cálculo de Estatísticas Descritivas (Média, Mediana, Quartis, IQR)
    if len(df_filtrado) > 0:
      serie_dados = df_filtrado[col_analise].dropna()

      stats_luan = resumo_estatistico(serie_dados)
      media = stats_luan["media"]
      mediana = stats_luan["mediana"]
      moda = stats_luan["moda"]
      q1 = stats_luan["q1"]
      q3 = stats_luan["q3"]
      iqr = stats_luan["iqr"]
      amplitude = stats_luan["amplitude"]
      desvio_padrao = stats_luan["desvio_padrao"]
      variancia = stats_luan["variancia"]

      limite_inferior = stats_luan["limite_inferior_outlier"]
      limite_superior = stats_luan["limite_superior_outlier"]

      outliers = serie_dados[
          (serie_dados < limite_inferior) | (serie_dados > limite_superior)
      ]

      st.markdown("---")
      st.subheader(f"📊 Estatísticas Descritivas para: `{col_analise}`")

      col1, col2, col3, col4 = st.columns(4)
      col1.metric("Média", formatar_numero(media))
      col2.metric("Mediana", formatar_numero(mediana))
      col3.metric("Moda", formatar_numero(moda) if moda is not None else "—")
      col4.metric("Desvio Padrão", formatar_numero(desvio_padrao))

      col5, col6, col7, col8 = st.columns(4)
      col5.metric("1º Quartil (Q1)", formatar_numero(q1))
      col6.metric("3º Quartil (Q3)", formatar_numero(q3))
      col7.metric("IQR (Q3 - Q1)", formatar_numero(iqr))
      col8.metric("Variância", formatar_numero(variancia))

      st.caption(f"Amplitude (máx − mín): **{formatar_numero(amplitude)}** • n = {stats_luan['n']} registros válidos")

      st.markdown("---")

      # 5. Detecção e Visualização de Outliers
      st.subheader("🚨 Detecção de Outliers (Método IQR)")

      st.write(f"- **Limite Inferior:** `{limite_inferior:,.2f}`")
      st.write(f"- **Limite Superior:** `{limite_superior:,.2f}`")
      st.write(
          f"- **Total de outliers encontrados:** `{len(outliers)}` (de um total de"
          f" {len(serie_dados)} registros válidos)"
      )

      if len(outliers) > 0:
        with st.expander("Visualizar registros identificados como Outliers"):
          st.dataframe(
              df_filtrado.loc[outliers.index], use_container_width=True
          )
      else:
        st.success("Nenhum outlier detectado para este recorte com os filtros atuais!")

      st.markdown("---")
      st.subheader("📈 Visualização Gráfica")

      aba1, aba2 = st.tabs(["Boxplot", "Distribuição"])

      with aba1:
        import altair as alt

        st.markdown(
            "*O Boxplot abaixo ajuda a visualizar visualmente os limites e os"
            " outliers.*"
        )
        chart = (
            alt.Chart(df_filtrado)
            .mark_boxplot(extent=1.5)
            .encode(
                x=col_genero,
                y=col_analise,
                color=col_demografia,
                tooltip=[col_genero, col_demografia, col_analise],
            )
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)

      with aba2:
        st.bar_chart(serie_dados.value_counts(bins=10).sort_index())

      # 6. Ranking / comparação territorial (quando houver uma coluna de
      # capital/cidade/UF disponível na base — presente na opção de dados
      # reais do IBGE, e também detectada automaticamente num CSV enviado).
      col_territorio = next(
          (c for c in df_filtrado.columns if c.lower() in ("capital", "cidade", "municipio", "uf")),
          None,
      )
      if col_territorio:
        st.markdown("---")
        st.subheader(f"🎯 Ranking territorial — `{col_analise}` por {col_territorio}")
        df_rank = (
            df_filtrado.groupby(col_territorio)[col_analise]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={col_analise: f"{col_analise} (média)"})
        )
        st.dataframe(df_rank, use_container_width=True, hide_index=True)
        st.bar_chart(df_rank.set_index(col_territorio))

      # 7. Texto interpretativo
      st.markdown("---")
      st.subheader("📝 Leitura dos resultados")
      direcao = "mais concentrados em torno da mediana" if iqr < desvio_padrao else "mais dispersos, com maior variação entre os grupos"
      st.info(
          f"Para a variável **{col_analise}**, a mediana foi de **{formatar_numero(mediana)}** e o IQR de "
          f"**{formatar_numero(iqr)}**, indicando valores {direcao}. "
          f"{'Foram encontrados ' + str(len(outliers)) + ' outlier(s) pela regra 1,5×IQR, que merecem atenção na leitura por gênero/composição.' if len(outliers) > 0 else 'Não há outliers pela regra 1,5×IQR nesta seleção, o que sugere um recorte estatisticamente homogêneo.'}"
      )

    else:
      st.warning(
          "A seleção atual de filtros não retornou nenhum dado. Tente selecionar"
          " mais opções na barra lateral."
      )



def secao_julia():
    """
    ====================================================================
    JÚLIA — Identificação de Cidades Outliers (cresceram muito / encolheram)
    ====================================================================
    O que esta seção faz:
    Aplica a regra estatística do IQR (com multiplicador ajustável pelo
    usuário, padrão 1,5×IQR) sobre a taxa de crescimento 2010–2022 das
    capitais, separando outliers superiores (cresceram muito acima do
    padrão) de outliers inferiores (encolheram muito abaixo do padrão),
    com boxplot e gráfico de desvio em relação à mediana. Usa dados
    reais do Censo IBGE 2010 e 2022.
    Código original: github.com/juh777/-Identifica-o-de-Cidades-Outliers
    ====================================================================
    """

    """
    Projeto Integrador — "Números que Falam: Descobrindo o Brasil"
    Tema do Grupo: Crescimento Demográfico (Persona: Prefeitos de Capitais)

    Integrante: JÚLIA
    Indicador individual: Identificação de Cidades Outliers (que cresceram muito ou encolheram)
    Fonte: IBGE, Censo Demográfico 2010 e 2022.

    Como rodar localmente:
        pip install -r requirements.txt
        streamlit run app.py
    """

    import pandas as pd
    import plotly.express as px
    import streamlit as st

    from estatisticas import resumo_estatistico, detectar_outliers, classificar_outlier, formatar_numero

    # (st.set_page_config já foi definido uma única vez no topo deste arquivo integrado)

    CAMINHO_DADOS_PADRAO = "dados/capitais_crescimento_2010_2022.csv"

    PERSONAS = {
        "Curitiba": "Carlos", "Porto Alegre": "Eduardo", "Belo Horizonte": "Elisa",
        "Salvador": "Jorge", "Florianopolis": "Roberto",
    }


    @st.cache_data
    def carregar_dados_padrao() -> pd.DataFrame:
        return pd.read_csv(CAMINHO_DADOS_PADRAO)


    def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]
        for c in ["populacao_2010", "populacao_2022", "variacao_absoluta", "taxa_crescimento_pct"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna(subset=["populacao_2010", "populacao_2022"])
        df["taxa_crescimento_pct"] = ((df["populacao_2022"] - df["populacao_2010"]) / df["populacao_2010"] * 100).round(2)
        df["e_capital_do_grupo"] = df["cidade"].isin(PERSONAS.keys())
        return df


    st.sidebar.title("⚙️ Filtros")
    st.sidebar.caption("Projeto Integrador • Identificação de Cidades Outliers")

    arquivo = st.sidebar.file_uploader("Upload da base IBGE (CSV ou XLSX)", type=["csv", "xlsx"])
    if arquivo is not None:
        try:
            df_bruto = pd.read_excel(arquivo) if arquivo.name.endswith(".xlsx") else pd.read_csv(arquivo)
            st.sidebar.success("Arquivo carregado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler o arquivo: {e}")
            df_bruto = carregar_dados_padrao()
    else:
        df_bruto = carregar_dados_padrao()
        st.sidebar.info("Usando a base padrão do IBGE (Censo 2010/2022).")

    df = tratar_dados(df_bruto)

    regioes = sorted(df["regiao"].dropna().unique().tolist())
    regiao_sel = st.sidebar.multiselect("Região", regioes, default=regioes)
    df_f = df[df["regiao"].isin(regiao_sel)]

    multiplicador = st.sidebar.slider(
        "Sensibilidade do teste de outliers (multiplicador do IQR)", min_value=1.0, max_value=3.0, value=1.5, step=0.1,
        help="A regra clássica usa 1,5×IQR. Valores maiores tornam o critério mais rígido (menos outliers).",
    )

    if df_f.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        st.stop()

    # --------------------------------------------------------------------------------------
    st.title("🎯 Identificação de Cidades Outliers de Crescimento")
    st.caption("Startup de Análise de Dados • Consultoria para Prefeitos de Capitais • Responsável: **Júlia**")

    with st.expander("📋 Cenário da persona (clique para ler)"):
        st.markdown(
            """
            Antes de revisar os Planos Diretores, os prefeitos pedem à consultoria: **"onde estão os
            casos fora da curva?"** — cidades que cresceram de forma explosiva (pressão sobre
            infraestrutura, saneamento, mobilidade) ou que encolheram (ociosidade de equipamentos
            públicos, evasão econômica). Esta seção aplica a **regra estatística do IQR** para
            responder com rigor, sem depender de impressão subjetiva.
            """
        )

    # --------------------------------------------------------------------------------------
    # ESTATÍSTICA DESCRITIVA COMPLETA
    # --------------------------------------------------------------------------------------
    stats = resumo_estatistico(df_f["taxa_crescimento_pct"])
    st.subheader("📊 Resumo estatístico — Taxa de crescimento (%) 2010–2022")

    linha1 = st.columns(4)
    linha1[0].metric("Média", f"{formatar_numero(stats['media'])}%")
    linha1[1].metric("Mediana", f"{formatar_numero(stats['mediana'])}%")
    linha1[2].metric("Moda", f"{formatar_numero(stats['moda'])}%" if pd.notna(stats["moda"]) else "-")
    linha1[3].metric("Desvio padrão", f"{formatar_numero(stats['desvio_padrao'])}%")

    linha2 = st.columns(4)
    linha2[0].metric("Q1", f"{formatar_numero(stats['q1'])}%")
    linha2[1].metric("Q2 (mediana)", f"{formatar_numero(stats['q2'])}%")
    linha2[2].metric("Q3", f"{formatar_numero(stats['q3'])}%")
    linha2[3].metric("IQR (Q3−Q1)", f"{formatar_numero(stats['iqr'])}%")

    linha3 = st.columns(3)
    linha3[0].metric("Amplitude (máx−mín)", f"{formatar_numero(stats['amplitude'])} p.p.")
    linha3[1].metric("Variância", formatar_numero(stats["variancia"]))
    linha3[2].metric("Limites do IQR", f"[{formatar_numero(stats['limite_inferior_outlier'])}%, {formatar_numero(stats['limite_superior_outlier'])}%]")

    # Limites recalculados conforme o multiplicador escolhido pelo usuário
    lim_inf_custom = stats["q1"] - multiplicador * stats["iqr"]
    lim_sup_custom = stats["q3"] + multiplicador * stats["iqr"]

    # --------------------------------------------------------------------------------------
    # DETECÇÃO DE OUTLIERS
    # --------------------------------------------------------------------------------------
    st.subheader(f"🚨 Cidades Outliers (regra {multiplicador:.1f} × IQR)")

    df_f = df_f.copy()
    df_f["classificacao"] = df_f["taxa_crescimento_pct"].apply(
        lambda v, q1=stats["q1"], q3=stats["q3"], iqr=stats["iqr"]: classificar_outlier(v, q1, q3, iqr)
        if multiplicador == 1.5 else (
            "Outlier superior (muito acima do padrão)" if v > lim_sup_custom else
            "Outlier inferior (muito abaixo do padrão)" if v < lim_inf_custom else
            "Dentro do padrão"
        )
    )

    outliers_sup = df_f[df_f["taxa_crescimento_pct"] > lim_sup_custom].sort_values("taxa_crescimento_pct", ascending=False)
    outliers_inf = df_f[df_f["taxa_crescimento_pct"] < lim_inf_custom].sort_values("taxa_crescimento_pct")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**🔺 Outliers superiores — cresceram muito acima do esperado (> {formatar_numero(lim_sup_custom)}%)**")
        if outliers_sup.empty:
            st.success("Nenhuma cidade nesta categoria.")
        else:
            st.dataframe(
                outliers_sup[["cidade", "uf", "taxa_crescimento_pct"]].rename(
                    columns={"cidade": "Cidade", "uf": "UF", "taxa_crescimento_pct": "Crescimento (%)"}
                ),
                use_container_width=True, hide_index=True,
            )
    with col2:
        st.markdown(f"**🔻 Outliers inferiores — encolheram muito abaixo do esperado (< {formatar_numero(lim_inf_custom)}%)**")
        if outliers_inf.empty:
            st.success("Nenhuma cidade nesta categoria.")
        else:
            st.dataframe(
                outliers_inf[["cidade", "uf", "taxa_crescimento_pct"]].rename(
                    columns={"cidade": "Cidade", "uf": "UF", "taxa_crescimento_pct": "Crescimento (%)"}
                ),
                use_container_width=True, hide_index=True,
            )

    # --------------------------------------------------------------------------------------
    # GRÁFICOS
    # --------------------------------------------------------------------------------------
    st.subheader("📉 Visualizações")
    tab1, tab2 = st.tabs(["Boxplot com outliers", "Dispersão (Z-score visual)"])

    with tab1:
        fig_box = px.box(
            df_f, y="taxa_crescimento_pct", points="all", hover_data=["cidade", "uf"],
            labels={"taxa_crescimento_pct": "Crescimento acumulado 2010–2022 (%)"},
            title="Boxplot da taxa de crescimento — pontos fora dos bigodes são outliers",
        )
        st.plotly_chart(fig_box, use_container_width=True)

    with tab2:
        df_f["desvio_da_mediana"] = df_f["taxa_crescimento_pct"] - stats["mediana"]
        fig_scatter = px.bar(
            df_f.sort_values("desvio_da_mediana"), x="desvio_da_mediana", y="cidade", orientation="h",
            color="classificacao",
            color_discrete_map={
                "Outlier superior (muito acima do padrão)": "#d62728",
                "Outlier inferior (muito abaixo do padrão)": "#ff7f0e",
                "Dentro do padrão": "#1f77b4",
                "Sem dado": "#7f7f7f",
            },
            labels={"desvio_da_mediana": "Desvio em relação à mediana (p.p.)", "cidade": "", "classificacao": "Classificação"},
            title="Desvio de cada capital em relação à mediana do grupo",
            height=750,
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # --------------------------------------------------------------------------------------
    # RESPOSTA ÀS PERGUNTAS DE NEGÓCIO
    # --------------------------------------------------------------------------------------
    st.subheader("💼 Resposta às Perguntas de Negócio da Persona")
    total_outliers = len(outliers_sup) + len(outliers_inf)
    st.markdown(
        f"""
    1. **Onde estão situados os outliers de crescimento?**
       Com a regra de **{multiplicador:.1f}×IQR**, foram identificadas **{total_outliers} cidades
       outliers** em {len(df_f)} capitais analisadas: **{len(outliers_sup)}** cresceram muito
       acima do padrão (destaque para {', '.join(outliers_sup['cidade'].tolist()) if not outliers_sup.empty else 'nenhuma'})
       e **{len(outliers_inf)}** encolheram muito abaixo do padrão
       ({', '.join(outliers_inf['cidade'].tolist()) if not outliers_inf.empty else 'nenhuma'}).

    2. **Por que isso importa para o orçamento público?**
       Outliers superiores pressionam **infraestrutura, saneamento e mobilidade** acima da
       capacidade planejada — risco de déficit de serviços. Outliers inferiores indicam
       **ociosidade de equipamentos públicos** (escolas, postos de saúde dimensionados para uma
       população que não existe mais) e possível evasão econômica — risco de gasto ineficiente.
       Tratar as demais cidades pela mediana (não pela média) evita que esses extremos distorçam
       o diagnóstico de "crescimento típico" das capitais brasileiras.
        """
    )

    # --------------------------------------------------------------------------------------
    # CONTEÚDO ADICIONAL
    # --------------------------------------------------------------------------------------
    st.subheader("📰 Conteúdo adicional")
    st.markdown(
        """
        **🔗 Censo 2022: Boa Vista e Florianópolis têm aumento populacional superior a 20% em 12 anos**
        *CNN Brasil* [Ler reportagem](https://www.cnnbrasil.com.br/nacional/censo-2022-boa-vista-e-florianopolis-tem-aumento-populacional-superior-a-20-em-12-anos/)

        **🔗 Censo 2022: saiba o que explica a queda populacional em diferentes capitais do país**
        *Itatiaia* [Ler reportagem](https://www.itatiaia.com.br/brasil/censo-2022-saiba-o-que-explica-a-queda-populacional-em-diferentes-capitais-do-pais/)
        """
    )

    st.divider()
    st.caption(
        "Fonte dos dados: IBGE, Censo Demográfico 2010 e 2022. "
        "Desenvolvido por Júlia • Projeto Integrador — Python & Matemática."
    )



def secao_salome():
    """
    ====================================================================
    SALOMÉ — Projeções de Envelhecimento Populacional e Infraestrutura
    ====================================================================
    O que esta seção faz:
    Projeta por regressão linear simples o percentual futuro de idosos
    (65+) de cada capital a partir da série histórica do Censo IBGE
    (1980–2022), compara o índice de envelhecimento entre as 5
    capitais e estima o impacto em infraestrutura (vagas de atenção ao
    idoso sugeridas) decorrente do envelhecimento projetado.
    Código original: github.com/Matheusslom/Proje-es-de-Envelhecimento-Populacional-e-Infraestrutura
    ====================================================================
    """

    """
    Projeto Integrador — "Números que Falam: Descobrindo o Brasil"
    Tema do Grupo: Crescimento Demográfico (Persona: Prefeitos de Capitais)

    Integrante: SALOMÉ
    Indicador individual: Projeções de Envelhecimento Populacional e Infraestrutura
    Fonte: IBGE, Censo Demográfico 2022 — População por idade e sexo (índice de envelhecimento).

    Como rodar localmente:
        pip install -r requirements.txt
        streamlit run app.py
    """

    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import streamlit as st

    from estatisticas import resumo_estatistico, detectar_outliers, classificar_outlier, formatar_numero

    # (st.set_page_config já foi definido uma única vez no topo deste arquivo integrado)

    CAMINHO_DADOS_PADRAO = "dados/estrutura_etaria_uf_capitais.csv"

    PERSONAS = {
        "Curitiba": "Carlos (Prefeito de Curitiba)", "Porto Alegre": "Eduardo (Prefeito de Porto Alegre)",
        "Belo Horizonte": "Elisa (Prefeita de Belo Horizonte)", "Salvador": "Jorge (Prefeito de Salvador)",
        "Florianopolis": "Roberto (Prefeito de Florianópolis)",
    }


    @st.cache_data
    def carregar_dados_padrao() -> pd.DataFrame:
        return pd.read_csv(CAMINHO_DADOS_PADRAO)


    def tratar_dados(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [c.strip().lower() for c in df.columns]
        for c in ["pct_0_14", "pct_15_64", "pct_65_mais", "indice_envelhecimento", "idade_mediana", "ano"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df


    def projetar_linear(anos: np.ndarray, valores: np.ndarray, anos_futuros: np.ndarray) -> np.ndarray:
        """Projeção simples por regressão linear (mínimos quadrados) — adequada para um
        indicador didático de tendência; não substitui as projeções demográficas oficiais do IBGE."""
        coef = np.polyfit(anos, valores, deg=1)
        return np.polyval(coef, anos_futuros)


    st.sidebar.title("⚙️ Filtros")
    st.sidebar.caption("Projeto Integrador • Envelhecimento e Infraestrutura")

    arquivo = st.sidebar.file_uploader("Upload da base IBGE (CSV ou XLSX)", type=["csv", "xlsx"])
    if arquivo is not None:
        try:
            df_bruto = pd.read_excel(arquivo) if arquivo.name.endswith(".xlsx") else pd.read_csv(arquivo)
            st.sidebar.success("Arquivo carregado com sucesso!")
        except Exception as e:
            st.sidebar.error(f"Erro ao ler o arquivo: {e}")
            df_bruto = carregar_dados_padrao()
    else:
        df_bruto = carregar_dados_padrao()
        st.sidebar.info("Usando a base padrão do IBGE (Censo 2022 — índice de envelhecimento).")

    df = tratar_dados(df_bruto)

    capitais = sorted(df["capital"].dropna().unique().tolist())
    capital_sel = st.sidebar.selectbox("Capital (persona)", capitais, index=capitais.index("Curitiba") if "Curitiba" in capitais else 0)

    horizonte = st.sidebar.slider("Horizonte da projeção (anos à frente de 2022)", min_value=4, max_value=28, value=12, step=4)

    df_capital = df[df["capital"] == capital_sel].sort_values("ano")

    # --------------------------------------------------------------------------------------
    st.title("🏗️ Projeções de Envelhecimento Populacional e Infraestrutura")
    st.caption(
        f"Startup de Análise de Dados • Consultoria para {PERSONAS.get(capital_sel, capital_sel)} • "
        f"Responsável: **Salomé**"
    )

    with st.expander("📋 Cenário da persona (clique para ler)"):
        st.markdown(
            """
            Os prefeitos revisam os **Planos Diretores** olhando para a década seguinte: quanto
            mais rápido a cidade envelhece, maior a urgência de investir agora em UBS geriátricas,
            mobilidade acessível e centros de convivência — e menor a pressão futura sobre creches
            e escolas de ensino fundamental.
            """
        )

    # --------------------------------------------------------------------------------------
    # KPIs — situação atual (2022)
    # --------------------------------------------------------------------------------------
    linha_2022 = df_capital[df_capital["ano"] == 2022].iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("% 65+ em 2022", f"{formatar_numero(linha_2022['pct_65_mais'])}%")
    c2.metric("Índice de envelhecimento 2022", formatar_numero(linha_2022["indice_envelhecimento"]))
    c3.metric("Idade mediana (UF) 2022", f"{int(linha_2022['idade_mediana'])} anos")

    # --------------------------------------------------------------------------------------
    # PROJEÇÃO LINEAR SIMPLES
    # --------------------------------------------------------------------------------------
    st.subheader(f"📈 Projeção de envelhecimento — {capital_sel}")

    anos_hist = df_capital["ano"].values.astype(float)
    pct_65_hist = df_capital["pct_65_mais"].values.astype(float)
    ano_final_projecao = 2022 + horizonte
    anos_futuros = np.arange(2023, ano_final_projecao + 1)
    projecao = projetar_linear(anos_hist, pct_65_hist, anos_futuros)
    projecao = np.clip(projecao, 0, 100)  # percentual não pode passar de 100%

    fig_proj = go.Figure()
    fig_proj.add_trace(go.Scatter(x=anos_hist, y=pct_65_hist, mode="lines+markers", name="Histórico (Censo)", line=dict(color="#1f77b4")))
    fig_proj.add_trace(go.Scatter(x=anos_futuros, y=projecao, mode="lines+markers", name="Projeção linear", line=dict(color="#d62728", dash="dash")))
    fig_proj.update_layout(
        title=f"% da população com 65+ anos — histórico e projeção até {ano_final_projecao}",
        xaxis_title="Ano", yaxis_title="% da população com 65 anos ou mais", height=450,
    )
    st.plotly_chart(fig_proj, use_container_width=True)

    pct_projetado = projecao[-1]
    st.info(
        f"Pela tendência linear dos últimos censos, **{capital_sel}** pode chegar a "
        f"**{formatar_numero(pct_projetado)}%** de idosos (65+) em **{ano_final_projecao}** "
        f"— um crescimento de {formatar_numero(pct_projetado - linha_2022['pct_65_mais'])} p.p. "
        "em relação a 2022. ⚠️ Projeção didática por regressão linear simples; para decisões reais "
        "de política pública, usar as **Projeções da População do IBGE**, que incorporam fecundidade, "
        "mortalidade e migração."
    )

    # --------------------------------------------------------------------------------------
    # ESTATÍSTICA DESCRITIVA — comparação entre as 5 capitais em 2022
    # --------------------------------------------------------------------------------------
    st.subheader("📊 Resumo estatístico — Índice de envelhecimento entre as 5 capitais (2022)")
    df_2022 = df[df["ano"] == 2022]
    stats = resumo_estatistico(df_2022["indice_envelhecimento"])
    cA, cB, cC, cD = st.columns(4)
    cA.metric("Média", formatar_numero(stats["media"]))
    cB.metric("Mediana", formatar_numero(stats["mediana"]))
    cC.metric("IQR", formatar_numero(stats["iqr"]))
    cD.metric("Desvio padrão", formatar_numero(stats["desvio_padrao"]))

    outliers = detectar_outliers(df_2022, "indice_envelhecimento")
    if not outliers.empty:
        st.warning("Capital(is) com índice de envelhecimento estatisticamente atípico: " + ", ".join(outliers["capital"].tolist()))
    else:
        st.success("Nenhuma capital é outlier de envelhecimento nesta seleção (1,5×IQR).")

    fig_comp = px.bar(
        df_2022.sort_values("indice_envelhecimento"), x="indice_envelhecimento", y="capital", orientation="h",
        labels={"indice_envelhecimento": "Índice de envelhecimento (idosos por 100 crianças)", "capital": ""},
        title="Índice de envelhecimento por capital (2022) — quanto maior, mais envelhecida a estrutura",
        color="indice_envelhecimento", color_continuous_scale="OrRd",
    )
    st.plotly_chart(fig_comp, use_container_width=True)

    # --------------------------------------------------------------------------------------
    # IMPACTO EM INFRAESTRUTURA — ESTIMATIVA ILUSTRATIVA
    # --------------------------------------------------------------------------------------
    st.subheader("🏥 Impacto estimado em infraestrutura")
    st.caption(
        "Estimativa didática: assume 1 vaga de UBS geriátrica / centro de convivência a cada "
        "1.000 idosos adicionais, apenas para ilustrar a ordem de grandeza do planejamento."
    )
    pop_atual = {
        "Curitiba": 1773733, "Porto Alegre": 1332570, "Belo Horizonte": 2315560,
        "Salvador": 2418005, "Florianopolis": 537213,
    }.get(capital_sel, 1_000_000)

    idosos_2022 = pop_atual * linha_2022["pct_65_mais"] / 100
    idosos_projetado = pop_atual * pct_projetado / 100
    novos_idosos = max(idosos_projetado - idosos_2022, 0)
    vagas_estimadas = int(novos_idosos / 1000)

    c1, c2, c3 = st.columns(3)
    c1.metric("Idosos (65+) em 2022 (estimado)", f"{int(idosos_2022):,}".replace(",", "."))
    c2.metric(f"Idosos (65+) em {ano_final_projecao} (projetado)", f"{int(idosos_projetado):,}".replace(",", "."))
    c3.metric("Novas vagas de atenção ao idoso sugeridas", f"{vagas_estimadas:,}".replace(",", "."))

    # --------------------------------------------------------------------------------------
    # RESPOSTA ÀS PERGUNTAS DE NEGÓCIO
    # --------------------------------------------------------------------------------------
    st.subheader("💼 Resposta às Perguntas de Negócio da Persona")
    st.markdown(
        f"""
    1. **Qual a velocidade do envelhecimento em {capital_sel}?**
       O índice de envelhecimento saltou de forma expressiva entre 2010 e 2022; mantendo a
       tendência linear, a cidade pode chegar a **{formatar_numero(pct_projetado)}%** de idosos
       em **{ano_final_projecao}**, reforçando a urgência de antecipar investimentos em saúde e
       mobilidade para a terceira idade.

    2. **Como priorizar o orçamento de infraestrutura entre as 5 capitais?**
       Capitais com maior índice de envelhecimento hoje (ver ranking acima) devem priorizar
       **UBS geriátricas e transporte acessível**; capitais relativamente mais jovens ainda têm
       janela para investir em **educação infantil e fundamental** antes que a pirâmide se inverta.
        """
    )

    # --------------------------------------------------------------------------------------
    # CONTEÚDO ADICIONAL
    # --------------------------------------------------------------------------------------
    st.subheader("📰 Conteúdo adicional")
    st.markdown(
        """
        **🔗 Censo 2022: número de pessoas com 65 anos ou mais de idade cresceu 57,4% em 12 anos**
        *IBGE Agência de Notícias*
        [Ler reportagem](https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-denoticias/noticias/38186-)

        **🔗 Censo 2022: Minas está entre os estados com maior população idosa do Brasil**
        *Itatiaia* [Ler reportagem](https://www.itatiaia.com.br/brasil/censo-2022-minas-esta-entre-os-estados-com-maior-populacao-idosa-do-brasil/)
        """
    )

    st.divider()
    st.caption(
        "Fonte dos dados: IBGE, Censo Demográfico 2022 — População por idade e sexo (índice de envelhecimento). "
        "Projeção: regressão linear simples sobre os censos históricos (uso didático). "
        "Desenvolvido por Salomé • Projeto Integrador — Python & Matemática."
    )


def secao_identificacao():
    """
    ====================================================================
    IDENTIFICAÇÃO DO GRUPO
    ====================================================================
    O que esta seção faz:
    Apresenta a identificação do grupo exigida pela rubrica do projeto
    (tema, persona e os 5 integrantes com o indicador demográfico de
    cada um), de forma visível dentro do próprio painel — e não apenas
    no README do repositório.
    ====================================================================
    """
    import pandas as pd
    import streamlit as st

    st.title("🏙️ Projeto Integrador — Crescimento Demográfico")
    st.subheader("Painel Integrado do Grupo")
    st.markdown(
        """
        **Projeto:** *Números que Falam: Descobrindo o Brasil* — Dashboard de Indicadores do IBGE
        com Estatística Descritiva em Python
        **Tema do grupo:** Crescimento Demográfico
        **Persona:** Prefeitos de Capitais
        """
    )

    st.markdown("### 👥 Integrantes e indicadores")
    tabela = pd.DataFrame(
        [
            ("Bernardo", "Taxa de crescimento populacional acumulada por cidade", "IBGE (Censo 2010/2022)"),
            ("Hugo", "Recorte por Faixa Etária e Pirâmide Populacional", "IBGE (Censo 2022)"),
            ("Luan", "Recorte por Gênero e Composição Demográfica", "IBGE (Censo 2022)"),
            ("Júlia", "Identificação de Cidades Outliers", "IBGE (Censo 2010/2022)"),
            ("Salomé", "Projeções de Envelhecimento Populacional e Infraestrutura", "IBGE (Censo 1980–2022)"),
        ],
        columns=["Integrante", "Indicador demográfico", "Fonte de dados"],
    )
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    st.info(
        "💡 Use o menu **\"Escolha o indicador\"** na barra lateral para navegar entre as 5 "
        "seções individuais do grupo. Cada seção começa com um comentário explicando o que o "
        "respectivo integrante fez e qual a fonte de dados utilizada."
    )

    st.caption(
        "Projeto Integrador — Matemática/Python • Persona: Prefeitos de Capitais • "
        "Grupo: Bernardo, Hugo, Luan, Júlia e Salomé."
    )


# ----------------------------------------------------------------------------------
# NAVEGAÇÃO — BARRA LATERAL PADRONIZADA DO GRUPO
# ----------------------------------------------------------------------------------
st.sidebar.title("🏙️ Crescimento Demográfico")
st.sidebar.caption("Persona: Prefeitos de Capitais • Projeto Integrador — Números que Falam")

SECOES = {
    "👥 Identificação do grupo": secao_identificacao,
    "📈 Bernardo — Crescimento populacional acumulado": secao_bernardo,
    "🧓 Hugo — Faixa etária e pirâmide populacional": secao_hugo,
    "🚻 Luan — Gênero e composição demográfica": secao_luan,
    "🎯 Júlia — Identificação de cidades outliers": secao_julia,
    "🏗️ Salomé — Envelhecimento e infraestrutura": secao_salome,
}

escolha = st.sidebar.radio("Escolha o indicador:", list(SECOES.keys()))
st.sidebar.divider()
st.sidebar.caption("Fonte: IBGE, Censo Demográfico (todas as 5 seções já usam base real do IBGE "
                    "na entrega do grupo — ver comentário no início de cada seção).")

SECOES[escolha]()
