import streamlit as st
import numpy as np
import plotly.graph_objects as go


# ============================================================
# FUNCIONES DE INDICADORES
# ============================================================

def calcular_crk(cuotas, k):
    """Calcula el Ratio de Concentración de las k empresas más grandes."""
    cuotas_ordenadas = np.sort(cuotas)[::-1]
    return np.sum(cuotas_ordenadas[:k])


def calcular_hhi(cuotas):
    """Calcula el Índice de Herfindahl-Hirschman (IHH)."""
    cuotas_porcentaje = cuotas * 100
    return np.sum(cuotas_porcentaje ** 2)


def calcular_entropia(cuotas):
    """Calcula el Índice de Entropía."""
    cuotas_positivas = cuotas[cuotas > 0]
    return -np.sum(cuotas_positivas * np.log(cuotas_positivas))


# ============================================================
# FUNCIÓN GENERADORA MONTE CARLO
# ============================================================

def generar_cuotas_monte_carlo(n_empresas):
    """
    Genera un vector aleatorio de cuotas de mercado no negativas
    que suma 1 (100%).
    """

    cuotas = np.random.dirichlet(np.ones(n_empresas))

    # Ajuste numérico
    cuotas = cuotas / np.sum(cuotas)

    # Cierre numérico de la suma
    cuotas[-1] = 1.0 - np.sum(cuotas[:-1])

    return cuotas


# ============================================================
# FUNCIÓN GENERAL PARA INDICADORES
# ============================================================

def calcular_indicador(cuotas, indicador, k):
    """Calcula el indicador seleccionado."""

    if indicador == "IHH":
        return calcular_hhi(cuotas)

    elif indicador == "CRk":
        # Lo expresamos en porcentaje
        return calcular_crk(cuotas, k) * 100

    elif indicador == "Índice de Entropía":
        return calcular_entropia(cuotas)


# ============================================================
# CONFIGURACIÓN DE STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Concentración de Mercado",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Simulador de Concentración de Mercado")

st.write(
    "Esta aplicación permite calcular indicadores de concentración "
    "y comparar un mercado particular con mercados generados mediante "
    "simulación Monte Carlo."
)


# ============================================================
# CONFIGURACIÓN DEL MERCADO
# ============================================================

st.sidebar.header("Configuración del mercado")

n_empresas = st.sidebar.number_input(
    "Número de empresas (N)",
    min_value=2,
    max_value=100,
    value=5,
    step=1
)

k = st.sidebar.number_input(
    "Número de empresas para CRk",
    min_value=1,
    max_value=n_empresas,
    value=min(4, n_empresas),
    step=1
)

indicador_seleccionado = st.sidebar.selectbox(
    "Indicador para la simulación",
    [
        "IHH",
        "CRk",
        "Índice de Entropía"
    ]
)

iteraciones = st.sidebar.number_input(
    "Número de simulaciones Monte Carlo",
    min_value=100,
    max_value=50000,
    value=1000,
    step=100
)


# ============================================================
# ADVERTENCIA COMPUTACIONAL
# ============================================================

if iteraciones > 10000:

    st.sidebar.warning(
        "Un número elevado de simulaciones puede aumentar "
        "el tiempo de cálculo y el uso de recursos."
    )


# ============================================================
# ENTRADA DEL CASO PARTICULAR
# ============================================================

st.header("Cuotas de mercado")

st.write(
    "Ingrese la participación de cada empresa en porcentaje. "
    "Cada cuota debe estar entre 0% y 100% y la suma total debe ser 100%."
)

cuotas_porcentaje = []

for i in range(n_empresas):

    cuota = st.number_input(
        f"Empresa {i + 1} (%)",
        min_value=0.0,
        max_value=100.0,
        value=100.0 / n_empresas,
        step=0.1,
        key=f"empresa_{i}"
    )

    cuotas_porcentaje.append(cuota)


# Convertimos porcentajes a proporciones
cuotas = np.array(cuotas_porcentaje) / 100

suma_cuotas = np.sum(cuotas)


# ============================================================
# VALIDACIÓN
# ============================================================

st.write(
    f"**Suma de cuotas:** {suma_cuotas * 100:.2f}%"
)

mercado_valido = np.isclose(
    suma_cuotas,
    1.0,
    atol=1e-9
)

if not mercado_valido:

    st.error(
        "Las cuotas deben sumar 100%. "
        "Corrija los valores antes de calcular los indicadores."
    )

else:

    st.success(
        "✓ Las cuotas son válidas y suman 100%."
    )


    # ========================================================
    # INDICADORES DEL CASO PARTICULAR
    # ========================================================

    crk = calcular_crk(cuotas, k)
    hhi = calcular_hhi(cuotas)
    entropia = calcular_entropia(cuotas)

    st.header("Indicadores de concentración")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            f"CR{k}",
            f"{crk * 100:.2f}%"
        )

    with col2:

        st.metric(
            "IHH",
            f"{hhi:.2f}"
        )

    with col3:

        st.metric(
            "Índice de Entropía",
            f"{entropia:.4f}"
        )


    # ========================================================
    # TABLA DE CUOTAS
    # ========================================================

    st.subheader("Distribución de cuotas")

    datos = {
        "Empresa": [
            f"Empresa {i + 1}"
            for i in range(n_empresas)
        ],
        "Cuota (%)": cuotas_porcentaje
    }

    st.dataframe(
        datos,
        use_container_width=True
    )


# ============================================================
# SIMULACIÓN MONTE CARLO
# ============================================================

st.header("🎲 Simulación Monte Carlo")

st.write(
    "La simulación genera mercados aleatorios con el mismo número "
    "de empresas. En cada iteración las cuotas son no negativas "
    "y suman 100%."
)

st.write(
    f"**Indicador seleccionado:** {indicador_seleccionado}"
)


# Solo permitimos ejecutar si el mercado particular es válido
if mercado_valido:

    if st.button(
        "Ejecutar simulación Monte Carlo",
        type="primary"
    ):

        simulaciones = []

        indicadores_simulados = []


        # ====================================================
        # GENERACIÓN DE LOS MERCADOS
        # ====================================================

        for _ in range(iteraciones):

            cuotas_simuladas = generar_cuotas_monte_carlo(
                n_empresas
            )

            simulaciones.append(
                cuotas_simuladas
            )

            valor_simulado = calcular_indicador(
                cuotas_simuladas,
                indicador_seleccionado,
                k
            )

            indicadores_simulados.append(
                valor_simulado
            )


        simulaciones = np.array(
            simulaciones
        )

        indicadores_simulados = np.array(
            indicadores_simulados
        )


        # ====================================================
        # COMPROBACIÓN DE LAS SUMAS
        # ====================================================

        sumas = np.sum(
            simulaciones,
            axis=1
        )

        st.success(
            f"Se generaron correctamente "
            f"{iteraciones:,} mercados simulados."
        )

        st.write(
            f"**Número de empresas por mercado:** "
            f"{n_empresas}"
        )

        st.write(
            f"**Número de mercados simulados:** "
            f"{iteraciones:,}"
        )

        st.write(
            f"**Suma mínima encontrada:** "
            f"{np.min(sumas):.12f}"
        )

        st.write(
            f"**Suma máxima encontrada:** "
            f"{np.max(sumas):.12f}"
        )


        # ====================================================
        # INFORMACIÓN DEL INDICADOR SELECCIONADO
        # ====================================================

        if indicador_seleccionado == "IHH":

            valor_particular = hhi

            nombre_indicador = "IHH"

            unidad = "puntos"


        elif indicador_seleccionado == "CRk":

            valor_particular = crk * 100

            nombre_indicador = f"CR{k}"

            unidad = "%"


        elif indicador_seleccionado == "Índice de Entropía":

            valor_particular = entropia

            nombre_indicador = "Índice de Entropía"

            unidad = ""


        # ====================================================
        # ESTADÍSTICAS MONTE CARLO
        # ====================================================

        st.subheader(
            f"Resultados simulados: {nombre_indicador}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Promedio",
                f"{np.mean(indicadores_simulados):.2f} "
                f"{unidad}"
            )

        with col2:

            st.metric(
                "Mínimo",
                f"{np.min(indicadores_simulados):.2f} "
                f"{unidad}"
            )

        with col3:

            st.metric(
                "Máximo",
                f"{np.max(indicadores_simulados):.2f} "
                f"{unidad}"
            )


        # ====================================================
        # PRIMEROS 10 RESULTADOS
        # ====================================================

        st.write(
            f"Primeros 10 valores generados de "
            f"{nombre_indicador}:"
        )

        st.dataframe(
            {
                "Simulación": np.arange(1, 11),

                nombre_indicador:
                    indicadores_simulados[:10]
            },
            use_container_width=True
        )


        # ====================================================
        # HISTOGRAMA
        # ====================================================

        st.subheader(
            f"Distribución empírica de {nombre_indicador}"
        )

        fig = go.Figure()

        fig.add_trace(
            go.Histogram(
                x=indicadores_simulados,
                nbinsx=30,
                name="Mercados simulados"
            )
        )


        # ====================================================
        # LÍNEA DEL CASO PARTICULAR
        # ====================================================

        fig.add_vline(
            x=valor_particular,
            line_width=3,
            line_dash="dash",
            annotation_text=(
                f"{nombre_indicador} particular = "
                f"{valor_particular:.2f}"
            ),
            annotation_position="top right"
        )


        # ====================================================
        # CONFIGURACIÓN DEL GRÁFICO
        # ====================================================

        if unidad:

            titulo_eje_x = (
                f"{nombre_indicador} ({unidad})"
            )

        else:

            titulo_eje_x = nombre_indicador


        fig.update_layout(
            title=(
                f"Distribución de {nombre_indicador} "
                f"mediante simulación Monte Carlo"
            ),
            xaxis_title=titulo_eje_x,
            yaxis_title="Frecuencia",
            bargap=0.05
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


        # ====================================================
        # PERCENTIL
        # ====================================================

        percentil = np.mean(
            indicadores_simulados
            <= valor_particular
        ) * 100


        st.subheader(
            "Posición del mercado particular"
        )

        st.metric(
            f"Percentil de {nombre_indicador}",
            f"{percentil:.1f}%"
        )

        st.write(
            f"El valor particular de "
            f"**{nombre_indicador}** es "
            f"**{valor_particular:.2f} {unidad}**. "
            f"Se encuentra aproximadamente en el "
            f"**percentil {percentil:.1f}** "
            f"de la distribución simulada."
        )

        st.write(
            f"Esto significa que aproximadamente el "
            f"**{percentil:.1f}%** de los mercados "
            f"simulados presenta un valor de "
            f"**{nombre_indicador} menor o igual** "
            f"al del mercado particular."
        )


        # ====================================================
        # ACLARACIÓN PARA ENTROPÍA
        # ====================================================

        if indicador_seleccionado == "Índice de Entropía":

            st.info(
                "En el Índice de Entropía, un valor mayor "
                "representa una distribución más uniforme de "
                "las cuotas. Por ello, un percentil mayor no "
                "debe interpretarse automáticamente como una "
                "mayor concentración."
            )

else:

    st.info(
        "Corrija las cuotas del mercado particular antes "
        "de ejecutar la simulación Monte Carlo."
    )