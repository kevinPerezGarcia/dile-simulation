import streamlit as st
from sympy import symbols, Eq, solve, latex
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Configuración de la aplicación
st.title("DILE - Simulación")

# Pestañas
main_tabs = st.tabs(["Simulación", "Comparación",  "Información"])

with main_tabs[0]:
    # Definir variables exógenas
    r_m, r_p, tau, rho = symbols('r_m r_p tau rho')  # Tasa de interés activa, pasiva, impuestos, morosidad

    # Definir parámetros
    beta, gamma, sigma, OIE = symbols('beta gamma sigma OIE')  # Provisiones, gastos admin, comisiones servicios, otros ingresos

    # Definir variables endógenas
    L, D = symbols('L D')  # Préstamos y depósitos
    IF, GF = symbols('IF GF')  # Ingresos y gastos financieros
    RNF, PRC = symbols('RNF PRC')  # Resultado neto financiero y provisiones
    ROF, IS, GA, RO, IMP, RE = symbols('ROF IS GA RO IMP RE')  # Variables del resultado operativo y neto

    # Definir las ecuaciones del modelo
    eq1 = Eq(IF, r_m * L)  # Ingresos financieros
    eq2 = Eq(GF, r_p * D)  # Gastos financieros
    eq3 = Eq(RNF, IF - GF)  # Resultado neto financiero
    eq4 = Eq(PRC, beta * rho * L)  # Provisiones por riesgo de crédito
    eq5 = Eq(ROF, RNF - PRC)  # Resultado operativo financiero
    eq6 = Eq(IS, sigma * L)  # Ingresos por servicios
    eq7 = Eq(GA, gamma * IF)  # Gastos administrativos
    eq8 = Eq(RO, ROF + IS - GA + OIE)  # Resultado operativo
    eq9 = Eq(IMP, tau * RO)  # Impuestos
    eq10 = Eq(RE, RO - IMP)  # Resultado del ejercicio

    # Resolver simbólicamente las variables endógenas en función de las demás
    endogenous_vars = [IF, GF, RNF, PRC, ROF, IS, GA, RO, IMP, RE]
    equations = [eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq9, eq10]

    # Crear un grafo de dependencias
    graph = nx.DiGraph()

    # Agregar nodos y relaciones
    for eq in equations:
        lhs = eq.lhs
        rhs = eq.rhs
        graph.add_node(str(lhs), type="endogenous")
        for symbol in rhs.free_symbols:
            graph.add_node(str(symbol), type="exogenous" if symbol in [r_m, r_p, tau, rho, beta, gamma, sigma, OIE, L, D] else "parameter")
            graph.add_edge(str(symbol), str(lhs))
    st.sidebar.header("Parámetros del Modelo")

    # Parámetros ajustables
    r_m_value = st.sidebar.slider("Tasa de interés activa ($r_m$)", 0.01, 0.20, 0.10, 0.01)
    r_p_value = st.sidebar.slider("Tasa de interés pasiva ($r_p$)", 0.01, 0.10, 0.05, 0.01)
    tau_value = st.sidebar.slider("Tasa de impuestos ($tau$)", 0.0, 0.50, 0.30, 0.05)
    rho_value = st.sidebar.slider("Tasa de morosidad ($rho$)", 0.0, 0.10, 0.02, 0.01)
    beta_value = st.sidebar.slider("Coeficiente de provisión ($beta$)", 0.1, 1.0, 0.5, 0.1)
    gamma_value = st.sidebar.slider("Gastos administrativos (% ingresos financieros, $gamma$)", 0.0, 0.3, 0.1, 0.05)
    sigma_value = st.sidebar.slider("Comisiones (% préstamos, $sigma$)", 0.0, 0.05, 0.01, 0.005)
    OIE_value = st.sidebar.number_input("Otros ingresos extraordinarios ($OIE$)", value=5000, step=500)

    # Valores de préstamos y depósitos
    L_value = st.sidebar.number_input("Préstamos otorgados ($L$)", value=1000000, step=100000)
    D_value = st.sidebar.number_input("Depósitos captados ($D$)", value=800000, step=100000)

    # Sustituciones en el modelo
    control_variables = {
        r_m: r_m_value,
        r_p: r_p_value,
        tau: tau_value,
        rho: rho_value,
        beta: beta_value,
        gamma: gamma_value,
        sigma: sigma_value,
        OIE: OIE_value,
        L: L_value,
        D: D_value
    }

    # Resolver el sistema de ecuaciones
    solutions = solve([eq.subs(control_variables) for eq in equations], endogenous_vars, dict=True)

    # Manejo de escenarios guardados
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    # Nombrar escenario
    scenario_name = st.text_input("Nombre del escenario: ")

    # Función para guardar escenario actual
    def save_scenario():
        if solutions:
            scenario_data = {"Variables de resultado": solutions[0]}
            scenario_data.update({"Variables de control": control_variables})
            st.session_state.saved_scenarios.update({scenario_name: scenario_data})

    # Botón para guardar escenario
    if st.button("Guardar Escenario"):
        save_scenario()
        st.success("Escenario guardado con éxito")

    # Mostrar resultados
    st.subheader("Resultados del Estado de Resultados")
    # Mostrar resultados como estado de resultados
    if solutions:
        for sol in solutions:
            st.markdown(
                f"""
                | **Cuenta**                             | **Monto (S/.)**   |
                |----------------------------------------|-------------------|
                | **Ingresos financieros (IF)**          | {sol[IF]:,.2f}    |
                | **(-) Gastos financieros (GF)**        | {sol[GF]:,.2f}    |
                | **= Resultado Neto Financiero (RNF)**  | {sol[RNF]:,.2f}   |
                | **(-) Provisiones (PRC)**              | {sol[PRC]:,.2f}   |
                | **= Resultado Operativo Financiero (ROF)** | {sol[ROF]:,.2f}|
                | **(+) Ingresos por Servicios (IS)**    | {sol[IS]:,.2f}    |
                | **(-) Gastos Administrativos (GA)**    | {sol[GA]:,.2f}    |
                | **(±) Otros Ingresos/Egresos (OIE)**   | {control_variables[OIE]:,.2f} |
                | **= Resultado Operativo (RO)**         | {sol[RO]:,.2f}    |
                | **(-) Impuestos (IMP)**                | {sol[IMP]:,.2f}   |
                | **= Resultado del Ejercicio (RE)**     | {sol[RE]:,.2f}    |
                """
            )
            
            st.subheader("Composición Porcetual")
            total_if = sol[IF]
            st.markdown(
                f"""
                | **Cuenta**                             | **Porcentaje (%)**   |
                |----------------------------------------|-----------------------|
                | **Ingresos financieros (IF)**          | 100.00               |
                | **(-) Gastos financieros (GF)**        | {sol[GF] / total_if * 100:.2f} |
                | **= Resultado Neto Financiero (RNF)**  | {sol[RNF] / total_if * 100:.2f} |
                | **(-) Provisiones (PRC)**              | {sol[PRC] / total_if * 100:.2f} |
                | **= Resultado Operativo Financiero (ROF)** | {sol[ROF] / total_if * 100:.2f} |
                | **(+) Ingresos por Servicios (IS)**    | {sol[IS] / total_if * 100:.2f} |
                | **(-) Gastos Administrativos (GA)**    | {sol[GA] / total_if * 100:.2f} |
                | **(±) Otros Ingresos/Egresos (OIE)**   | {control_variables[OIE] / total_if * 100:.2f} |
                | **= Resultado Operativo (RO)**         | {sol[RO] / total_if * 100:.2f} |
                | **(-) Impuestos (IMP)**                | {sol[IMP] / total_if * 100:.2f} |
                | **= Resultado del Ejercicio (RE)**     | {sol[RE] / total_if * 100:.2f} |
                """
            )
    else:
        st.error("No se pudo resolver el sistema de ecuaciones con los valores proporcionados.")
    

with main_tabs[1]:
    # Mostrar los escenarios guardados
    st.subheader("Escenarios Guardados")

    # Verificar si hay escenarios guardados
    if st.session_state.saved_scenarios:
        
        # Mostar tabla de control
        
        
        # Mostrar tabla de resultados
        scenario_dict = st.session_state.saved_scenarios[scenario_name]["Variables de resultado"]
        scenario_df = pd.DataFrame(scenario_dict, index=[scenario_name])
        #TODO Renombrar nombre de las variables por algo más explicativos como el del estado de resultados
        
        st.dataframe(scenario_df.T)
            
        # Mostrar tabla de composición
        
        # Mostrar tabla de métricas
        
        # Mostrar gráfico de radar sobre métricas
    else:
        st.write("No hay escenarios guardados.")
        
with main_tabs[2]:
    # Mostrar tabla en Markdown
    st.subheader("Análisis")
    st.markdown(r"""
    | **Partida**                                    | **Fórmula**                                 |
    |------------------------------------------------|---------------------------------------------|
    | **Ingresos Financieros ($IF$)**                | $IF = r_m \times L$                         |
    | **Gastos Financieros ($GF$)**                  | $GF = r_p \times D$                         |
    | **Resultado Neto Financiero ($RNF$)**          | $RNF = IF - GF$                             |
    | **Provisiones por Riesgos de Crédito ($PRC$)** | $PRC = \beta \times \rho \times L$          |
    | **Resultado Operativo Financiero ($ROF$)**     | $ROF = RNF - PRC$                           |
    | **Ingresos por Servicios ($IS$)**              | $IS = \sigma \times L$                      |
    | **Gastos Administrativos ($GA$)**              | $GA = \gamma \times IF$                     |
    | **Resultado Operativo ($RO$)**                 | $RO = ROF + IS - GA + OIE$                  |
    | **Impuestos ($IMP$)**                          | $IMP = \tau \times RO$                      |
    | **Resultado del Ejercicio ($RE$)**             | $RE = RO - IMP$                             |
    """)

    # Variables
    st.subheader("Variables")
    st.markdown(r"""
    | **Variable**                                 | **Símbolo**                            | **Tipo de Variable**                      |
    |----------------------------------------------|----------------------------------------|-------------------------------------------|
    | **Ingresos Financieros**                     | $IF$                                   | Variable de Resultado                     |
    | **Gastos Financieros**                       | $GF$                                   | Variable de Resultado                     |
    | **Resultado Neto Financiero**                | $RNF$                                  | Variable de Resultado                     |
    | **Provisiones por Riesgos de Crédito**       | $PRC$                                  | Variable de Resultado                     |
    | **Resultado Operativo Financiero**          | $ROF$                                  | Variable de Resultado                     |
    | **Ingresos por Servicios**                   | $IS$                                   | Variable de Resultado                     |
    | **Gastos Administrativos**                   | $GA$                                   | Variable de Resultado                     |
    | **Resultado Operativo**                      | $RO$                                   | Variable de Resultado                     |
    | **Impuestos**                               | $IMP$                                  | Variable de Resultado                     |
    | **Resultado del Ejercicio**                  | $RE$                                   | Variable de Resultado                     |
    | **Tasa de Interés Activa ($r_m$)**            | $r_m$                                  | Variable de Control                       |
    | **Tasa de Interés Pasiva ($r_p$)**           | $r_p$                                  | Variable de Control                       |
    | **Depósitos ($D$)**                          | $D$                                    | Variable de Control                       |
    | **Monto de Créditos ($L$)**                  | $L$                                    | Variable de Control                       |
    | **Factor de Riesgo ($\beta$)**               | $\beta$                                | Variable de Control                       |
    | **Factor de Liquidez ($\rho$)**              | $\rho$                                 | Variable de Control                       |
    | **Factor de Rentabilidad ($\sigma$)**        | $\sigma$                               | Variable de Control                       |
    | **Factor de Costo Administrativo ($\gamma$)**| $\gamma$                               | Variable de Control                       |
    | **Tasa de Impuesto ($\tau$)**                | $\tau$                                 | Variable de Control                       |
    | **Otros Ingresos y Egresos ($OIE$)**         | $OIE$                                  | Variable de Control                       |
    """)

    # Grafo de dependencias
    st.subheader("Gráfico de Dependencias")
    st.markdown("""
    Este gráfico muestra las relaciones de dependencia entre las variables del modelo. Sus elementos son:
    
    1. **Nodos**:
        - Representan variables de control o de resultado.
        - Se diferencian por colores:
            - **Rojo**: Variables de control.
            - **Azul**: Variables de resultado.
    2. **Aristas**:
        - Representan las relaciones de dependencia entre variables.
    """)

    # Dibujar el grafo
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph)
    colors = ["red" if graph.nodes[node]["type"] == "exogenous" else "blue" for node in graph.nodes()]
    nx.draw(graph, pos, with_labels=True, node_color=colors, node_size=3000, font_size=10, font_weight="bold", arrowsize=20, edge_color="gray")
    plt.title("Dependencias entre Variables", fontsize=16)
    st.pyplot(plt)