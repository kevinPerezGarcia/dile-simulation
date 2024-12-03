import streamlit as st
from sympy import symbols, Eq, solve, latex
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Configuración de la aplicación
st.title("DILE - Simulación")

# Pestañas
main_tabs = st.tabs(["Simulación", "Comparación", "Información"])

with main_tabs[0]:
    # Establecer parámetros como variables simbólicas
    alpha_INT, alpha_MOR, alpha_DES, alpha_ING_CUR = symbols('alpha_INT alpha_MOR alpha_DES alpha_ING_CUR')
    alpha_ING_SEG, alpha_COS_FON, alpha_DEP, alpha_PRO = symbols('alpha_ING_SEG alpha_COS_FON alpha_DEP alpha_PRO')
    alpha_SAL_PER, alpha_ALQ_MAN, alpha_SER_BAS, alpha_CLC = symbols('alpha_SAL_PER alpha_ALQ_MAN alpha_SER_BAS alpha_CLC')
    alpha_PUB_MAR, alpha_COM_VEN, alpha_EFC, alpha_GAS_OFI = symbols('alpha_PUB_MAR alpha_COM_VEN alpha_EFC alpha_GAS_OFI')

    # Establecer variables exógenas como simbólicas
    CAR = symbols('CAR')

    # Establecer variables endógenas como simbólicas
    TOT_ING = symbols('TOT_ING')
    ING_FIN = symbols('ING_FIN')
    INT, MOR, DES = symbols('INT MOR DES')
    ING_CUR, ING_SEG = symbols('ING_CUR ING_SEG')
    TOT_GAS, COS_FON, DEP, PRO = symbols('TOT_GAS COS_FON DEP PRO')
    UTI_BRU = symbols('UTI_BRU')
    GAS_ADM, SAL_PER, ALQ_MAN, SER_BAS, CLC = symbols('GAS_ADM SAL_PER ALQ_MAN SER_BAS CLC')
    GAS_OPE, PUB_MAR, COM_VEN, EFC, GAS_OFI = symbols('GAS_OPE PUB_MAR COM_VEN EFC GAS_OFI')
    UTI_NET = symbols('UTI_NET')

    # Definir varibles endógenas
    endogenous_vars = [TOT_ING, ING_FIN, INT, MOR, DES, ING_CUR, ING_SEG, TOT_GAS, COS_FON, DEP, PRO, UTI_BRU, GAS_ADM, SAL_PER, ALQ_MAN, SER_BAS, CLC, GAS_OPE, PUB_MAR, COM_VEN, EFC, GAS_OFI, UTI_NET]

    # Definir ecuaciones
    equations = [
        Eq(TOT_ING, ING_FIN + ING_CUR + ING_SEG),
        Eq(ING_FIN, INT + MOR + DES),
        Eq(INT, alpha_INT * CAR),
        Eq(MOR, alpha_MOR * CAR),
        Eq(DES, alpha_DES * CAR),
        Eq(ING_CUR, alpha_ING_CUR * CAR),
        Eq(ING_SEG, alpha_ING_SEG * CAR),
        Eq(TOT_GAS, DEP + COS_FON + PRO),
        Eq(COS_FON, alpha_COS_FON * DEP),
        Eq(DEP, alpha_DEP * CAR),
        Eq(PRO, alpha_PRO * CAR),
        Eq(UTI_BRU, TOT_ING - TOT_GAS),
        Eq(GAS_ADM, SAL_PER + ALQ_MAN + SER_BAS + CLC),
        Eq(SAL_PER, alpha_SAL_PER * ING_FIN),
        Eq(ALQ_MAN, alpha_ALQ_MAN * ING_FIN),
        Eq(SER_BAS, alpha_SER_BAS * ING_FIN),
        Eq(CLC, alpha_CLC * ING_FIN),
        Eq(GAS_OPE, PUB_MAR + COM_VEN + EFC + GAS_OFI),
        Eq(PUB_MAR, alpha_PUB_MAR * ING_FIN),
        Eq(COM_VEN, alpha_COM_VEN * ING_FIN),
        Eq(EFC, alpha_EFC * ING_FIN),
        Eq(GAS_OFI, alpha_GAS_OFI * ING_FIN),
        Eq(UTI_NET, UTI_BRU - GAS_ADM - GAS_OPE),
    ]

    st.sidebar.header("Parámetros del Modelo")

    # Entrada de valor para variables exógenas
    CAR_value = st.sidebar.number_input("Cartera ($CAR$)", value=1000000, step=100000)
    
    # Entrada de valor para parámetros
    alpha_values = {
        alpha_INT : st.sidebar.slider("Proporción de Tasa de Interés ($\u03B1_{INT}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_MOR : st.sidebar.slider("Proporción de Tasa de Mora ($\u03B1_{MOR}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_DES : st.sidebar.slider("Proporción de Tasa de Desgravamen ($\u03B1_{DES}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_ING_CUR : st.sidebar.slider("Proporción de Ingresos por Cursos ($\u03B1_{ING\_CUR}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_ING_SEG : st.sidebar.slider("Proporción de Ingresos por Seguros ($\u03B1_{ING\_SEG}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_COS_FON : st.sidebar.slider("Proporción del Costo de Fondeo ($\u03B1_{COS\_FON}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_DEP : st.sidebar.slider("Proporción de Depósitos ($\u03B1_{DEP}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_PRO : st.sidebar.slider("Proporción de Provisión ($\u03B1_{PRO}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_SAL_PER : st.sidebar.slider("Proporción de Salario del Personal ($\u03B1_{SAL\_PER}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_ALQ_MAN : st.sidebar.slider("Proporción de Alquiler y Mantenimiento ($\u03B1_{ALQ\_MAN}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_SER_BAS : st.sidebar.slider("Proporción de Servicios Básicos ($\u03B1_{SER\_BAS}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_CLC : st.sidebar.slider("Proporción de Costos Legales de Consultoría ($\u03B1_{CLC}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_PUB_MAR : st.sidebar.slider("Proporción de Publicidad y Marketing ($\u03B1_{PUB\_MAR}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_COM_VEN : st.sidebar.slider("Proporción de Comisiones de Ventas ($\u03B1_{COM\_VEN}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_EFC : st.sidebar.slider("Proporción de Eventos y Ferias Comerciales ($\u03B1_{EFC}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
        alpha_GAS_OFI : st.sidebar.slider("Proporción de Gastos de Oficina ($\u03B1_{GAS\_OFI}$)", min_value=0.0, max_value=1.0, value=0.1, step=0.01),
    }

    # Asignación de valores a varibles exógenas y parámetros
    control_variables = {CAR: CAR_value, **alpha_values}
    
    # Conversión de un sistema de ecuaciones simbólico a uno numérico
    numerical_equations_system = [eq.subs(control_variables) for eq in equations]

    # Resolver el sistema de ecuaciones
    output_variables = solve(numerical_equations_system, endogenous_vars, dict=True)[0]    

    # Mostrar tabla de resultads
    if output_variables:
        data = {
            "Monto": [
                control_variables[CAR],
                output_variables[TOT_ING],
                output_variables[ING_FIN],
                output_variables[INT],
                output_variables[MOR],
                output_variables[DES],
                output_variables[ING_CUR],
                output_variables[ING_SEG],
                output_variables[TOT_GAS],
                output_variables[COS_FON],
                output_variables[DEP],
                output_variables[PRO],
                output_variables[UTI_BRU],
                output_variables[GAS_ADM],
                output_variables[SAL_PER],
                output_variables[SER_BAS],
                output_variables[CLC],
                output_variables[GAS_OPE],
                output_variables[PUB_MAR],
                output_variables[COM_VEN],
                output_variables[EFC],
                output_variables[GAS_OFI],
                output_variables[UTI_NET],
            ]
        }

    indices = [
        "Cartera",
        "Total de Ingresos",
        "Ingresos Financieros",
        "- Interés",
        "- Mora",
        "- Desgravamen",
        "Ingresos por Cursos",
        "Ingresos por Seguros",
        "Total de Gastos",
        "- Costo de Fondeo",
        "* Depósitos",
        "- Provisión",
        "Utilidad Bruta",
        "Gastos Administrativos",
        "- Salario del Personal",
        "- Alquiler y Mantenimiento",
        "- Servicios Básicos",
        "- Costos Legales de Consultoría",
        "Gastos Operativos",
        "- Publicidad y Marketing",
        "- Eventos y Ferias Comerciales",
        "- Gastos de Oficina",
        "Utilidad Neta"
    ]

    estado_resultados = pd.DataFrame(data, index=indices)

    # Mostrar la tabla como una tabla estática (con índices como conceptos)
    st.table(estado_resultados)
    
    # Crear un grafo de dependencias
    graph = nx.DiGraph()

    # Agregar nodos y relaciones
    for eq in equations:
        lhs = eq.lhs
        rhs = eq.rhs
        graph.add_node(str(lhs), type="endogenous")
        for symbol in rhs.free_symbols:
            graph.add_node(str(symbol), type="exogenous" if symbol in [CAR, alpha_INT, alpha_MOR, alpha_DES, alpha_ING_CUR, alpha_ING_SEG, alpha_COS_FON, alpha_DEP, alpha_PRO, alpha_SAL_PER, alpha_ALQ_MAN, alpha_SER_BAS, alpha_CLC, alpha_PUB_MAR, alpha_COM_VEN, alpha_EFC, alpha_GAS_OFI] else "parameter")
            graph.add_edge(str(symbol), str(lhs))

    # Manejo de escenarios guardados
    if "saved_scenarios" not in st.session_state:
        st.session_state.saved_scenarios = {}

    # Nombrar escenario
    scenario_name = st.text_input("Nombre del escenario: ")

    # Función para guardar escenario actual
    def save_scenario():
        if output_variables:
            scenario_data = {"Variables de resultado": output_variables}
            scenario_data.update({"Variables de control": control_variables})
            st.session_state.saved_scenarios.update({scenario_name: scenario_data})

    # Botón para guardar escenario
    if st.button("Guardar Escenario"):
        save_scenario()
        st.success("Escenario guardado con éxito")


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
    | - Costo de Fondeo               | $COS\_FON$ | $COS\_FON = \alpha_{COS\_FON} \cdot DEP$ |
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
    
