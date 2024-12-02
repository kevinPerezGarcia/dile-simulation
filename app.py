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
    
    # Mostrar tabla de información financiera
    st.subheader("Análisis Financiero")
    st.markdown(r"""
    | Rubro                           | Símbolo    | Cálculo: Fórmula o Valor |
    |---------------------------------|------------|--------------------------|
    | **Cartera**                     | $CAR$      | dado |
    | **Total de Ingresos**           | $TOT\_ING$ | $TOT\_ING = ING\_FIN + ING\_CUR + ING\_SEG$ |
    | **Ingresos Financieros**        | $ING\_FIN$ | $ING\_FIN = INT + MOR + DES$ |
    | - Interés                       | $INT$      | $\alpha_{INT} \cdot CAR$ |
    | - Mora                          | $MOR$      | $\alpha_{MOR} \cdot CAR$ |
    | - Desgravamen                   | $DES$      | $\alpha_{DES} \cdot CAR$ |
    | **Ingresos por Cursos**         | $ING\_CUR$ | $\alpha_{ING\_CUR} \cdot CAR$ |
    | **Ingresos por Seguros**        | $ING\_SEG$ | $\alpha_{ING\_SEG} \cdot CAR$ |
    | **Total de Gastos**             | $TOT\_GAS$ | $TOT\_GAS = DEP + COS\_FON + PRO$ |
    | - Costo de Fondeo               | $COS_FON$  | $COS\_FON = \alpha_{COS\_FON} \cdot DEP$ |
    | * Depósitos                     | $DEP$      | $DEP = \alpha_{DEP} \cdot CAR $ |
    | - Provisión                     | $PRO$      | $PRO = \alpha_{PRO} \cdot CAR$ |
    | **Utilidad Bruta**              | $UTI\_BRU$ | $UTI\_BRU = TOT\_ING - TOT\_GAS$ |
    | **Gastos Administrativos**      | $GAS\_ADM$ | $GAS\_ADM = SAL\_PER + ALQ\_MAN + SER\_BAS + CLC$ |
    | - Salario del Personal          | $SAL\_PER$ | $SAL\_PER = \alpha_{SAL\_PER} \cdot ING\_FIN$ |
    | - Alquiler y Mantenimiento      | $ALQ\_MAN$ | $ALQ\_MAN = \alpha_{ALQ\_MAN} \cdot ING\_FIN$ |
    | - Servicios Básicos             | $SER\_BAS$ | $SER\_BAS = \alpha_{SER\_BAS} \cdot ING\_FIN$ |
    | - Costos Legales de Consultoría | $CLC$      | $CLC = \alpha_{CLC} \cdot ING\_FIN$ |
    | **Gastos Operativos**           | $GAS\_OPE$ | $GO = PUB\_MAR + COM\_VEN + EFC + GAS\_OFI$ |
    | - Publicidad y Marketing        | $PUB\_MAR$ | $PUB\_MAR = \alpha_{PUB\_MAR} \cdot ING\_FIN$ |
    | - Comisiones de Ventas          | $COM\_VEN$ | $COM\_VEN = \alpha_{COM\_VEN} \cdot ING\_FIN$ |
    | - Eventos y Ferias Comerciales  | $EFC$      | $EFC = \alpha_{EFC} \cdot ING\_FIN$ |
    | - Gastos de Oficina             | $GAS\_OFI$ | $GAS\_OFI = \alpha_{GAS\_OFI} \cdot ING\_FIN$ |
    | **Utilidad Neta**               | $UTI\_NET$ | $UTI\_NET = UTI\_BRU - GAS\_ADM - GAS\_OPE$ |
    """)
    
    # Tabla de parámetros
    st.subheader("Parámetros")
    st.markdown(r"""
    | Proporción       | Descripción                              | Rubro                     |
    |------------------|------------------------------------------|---------------------------|
    | $\alpha_{INT}$   | Tasa de interés aplicada                 | Interés (Ingresos Financieros) |
    | $\alpha_{MOR}$   | Tasa de mora aplicada                    | Mora (Ingresos Financieros) |
    | $\alpha_{DES}$   | Tasa de desgravamen aplicada             | Desgravamen (Ingresos Financieros) |
    | $\alpha_{ING\_CUR}$ | Tasa aplicada a los ingresos por cursos | Ingresos por Cursos       |
    | $\alpha_{ING\_SEG}$ | Tasa aplicada a los ingresos por seguros | Ingresos por Seguros      |
    | $\alpha_{COS\_FON}$ | Proporción del costo de fondeo sobre depósitos | Costo de Fondeo (Gastos) |
    | $\alpha_{DEP}$   | Tasa aplicada a los depósitos            | Depósitos (Gastos)        |
    | $\alpha_{PRO}$   | Proporción de provisión aplicada         | Provisión (Gastos)        |
    | $\alpha_{SAL\_PER}$ | Proporción de salario del personal     | Salario del Personal (Gastos Administrativos) |
    | $\alpha_{ALQ\_MAN}$ | Proporción de alquiler y mantenimiento | Alquiler y Mantenimiento (Gastos Administrativos) |
    | $\alpha_{SER\_BAS}$ | Proporción de servicios básicos        | Servicios Básicos (Gastos Administrativos) |
    | $\alpha_{CLC}$   | Proporción de costos legales de consultoría | Costos Legales de Consultoría (Gastos Administrativos) |
    | $\alpha_{PUB\_MAR}$ | Proporción de publicidad y marketing   | Publicidad y Marketing (Gastos Operativos) |
    | $\alpha_{COM\_VEN}$ | Proporción de comisiones de ventas     | Comisiones de Ventas (Gastos Operativos) |
    | $\alpha_{EFC}$   | Proporción de eventos y ferias comerciales | Eventos y Ferias Comerciales (Gastos Operativos) |
    | $\alpha_{GAS\_OFI}$ | Proporción de gastos de oficina        | Gastos de Oficina (Gastos Operativos) |
    """)

    # Grafo de dependencias
    st.subheader("Gráfico de Dependencias")
    st.markdown("""
    Este gráfico muestra las relaciones de dependencia entre las variables del modelo. Sus elementos son:
    
    1. **Nodos**:
        - Representan variables de proporciones o calculadas.
        - Se diferencian por colores:
            - **Rojo**: Variables de proporciones.
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