import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import json

# Inicializar la conexión a Neo4j
def init_connection():
    uri = "bolt://localhost:7687"  # Esto sigue igual si estás usando la instancia local de Neo4j
    username = "neo4j"
    password = "12345678"  # Actualizado a tu contraseña
    return GraphDatabase.driver(uri, auth=(username, password))

if 'neo4j_conn' not in st.session_state:
    st.session_state.neo4j_conn = init_connection()

# Función para ejecutar consultas Cypher
def run_query(query):
    # Manejar la sesión explícitamente y devolver los resultados en forma de lista de diccionarios
    with st.session_state.neo4j_conn.session() as session:
        result = session.run(query)
        # Convertir los resultados a una lista de diccionarios usando .data()
        return result.data()

def agregar_aplicacion():
    st.subheader("Agregar Nueva Aplicación")
    nombre_app = st.text_input("Nombre de la aplicación")
    descripcion_app = st.text_area("Descripción de la aplicación")
    
    if st.button("Agregar Aplicación"):
        if nombre_app:
            query = f"""
            CREATE (a:Aplicacion {{name: '{nombre_app}', descripcion: '{descripcion_app}'}})
            """
            run_query(query)
            st.success(f"Aplicación '{nombre_app}' agregada con éxito.")
        else:
            st.error("Por favor ingresa un nombre para la aplicación.")

def consultar_aplicaciones_por_tecnologia():
    st.subheader("Consultar Aplicaciones por Tecnología")
    tecnologia = st.text_input("Nombre de la tecnología")
    
    if st.button("Buscar Aplicaciones"):
        if tecnologia:
            query = f"""
            MATCH (a:Aplicacion)-[:USA]->(t:Tecnologia {{name: '{tecnologia}'}})
            RETURN a.name AS Aplicacion
            """
            resultados = run_query(query)
            
            # Crear una lista de aplicaciones a partir de los resultados
            apps = []
            for record in resultados:
                apps.append(record["Aplicacion"])

            if apps:
                st.write(f"Aplicaciones que usan la tecnología '{tecnologia}':")
                for app in apps:
                    st.write(app)
            else:
                st.warning(f"No se encontraron aplicaciones que usen '{tecnologia}'.")
        else:
            st.error("Por favor ingresa el nombre de la tecnología.")


def aplicaciones_por_tecnologia():
    st.subheader("Aplicaciones por Tecnología")
    tecnologia = st.text_input("Nombre de la Tecnología")
    
    if st.button("Buscar"):
        if tecnologia:
            query = f"""
            MATCH (a:Aplicacion)-[:USA]->(t:Tecnologia {{name: '{tecnologia}'}})
            RETURN t.name AS Tecnologia, count(a) AS Cantidad_de_Aplicaciones
            """
            resultados = run_query(query)
            if resultados:
                for record in resultados:
                    st.write(f"Tecnología: {record['Tecnologia']}, Cantidad de Aplicaciones: {record['Cantidad_de_Aplicaciones']}")
            else:
                st.warning(f"No se encontraron aplicaciones que usen '{tecnologia}'.")
        else:
            st.error("Por favor ingresa el nombre de la tecnología.")


def aplicaciones_similares():
    st.subheader("Aplicaciones Similares")
    nombre_app = st.text_input("Nombre de la Aplicación")
    
    if st.button("Buscar Aplicaciones Similares"):
        if nombre_app:
            query = f"""
            MATCH (a1:Aplicacion {{name: '{nombre_app}'}})-[:USA]->(t:Tecnologia)<-[:USA]-(a2:Aplicacion)
            WHERE a1 <> a2
            RETURN a2.name AS Aplicacion_Similar, count(t) AS Cantidad_de_Coincidencias
            """
            resultados = run_query(query)
            if resultados:
                for record in resultados:
                    st.write(f"Aplicación Similar: {record['Aplicacion_Similar']}, Tecnologías Comunes: {record['Cantidad_de_Coincidencias']}")
            else:
                st.warning(f"No se encontraron aplicaciones similares para '{nombre_app}'.")
        else:
            st.error("Por favor ingresa el nombre de la aplicación.")


def creadores_aplicaciones():
    st.subheader("Aplicaciones por Creador")
    nombre_creador = st.text_input("Nombre del Creador")
    
    if st.button("Buscar Aplicaciones"):
        if nombre_creador:
            query = f"""
            MATCH (d:Desarrollador {{name: '{nombre_creador}'}})-[:CREA]->(a:Aplicacion)
            RETURN a.name AS Aplicacion
            """
            resultados = run_query(query)
            if resultados:
                for record in resultados:
                    st.write(f"Aplicación: {record['Aplicacion']}")
            else:
                st.warning(f"No se encontraron aplicaciones creadas por '{nombre_creador}'.")
        else:
            st.error("Por favor ingresa el nombre del creador.")


def top_5_tecnologias():
    st.subheader("Top 5 Tecnologías Emergentes")
    
    if st.button("Mostrar los 5 mejores"):
        query = """
        MATCH (t:Tecnologia)<-[:USA]-(a:Aplicacion)
        WITH t, count(a) AS Usos
        RETURN t.name AS Tecnologia, Usos
        ORDER BY Usos DESC
        LIMIT 5
        """
        resultados = run_query(query)
        
        if resultados:
            for record in resultados:
                st.write(f"Tecnología: {record['Tecnologia']}, Usos: {record['Usos']}")
        else:
            st.warning("No se encontraron tecnologías emergentes.")


def creadores_no_trabajaron_juntos():
    st.subheader("Creadores que Nunca Han Trabajado Juntos")
    tecnologias = st.text_input("Lista de Tecnologías (separadas por comas)")
    
    if st.button("Buscar Creadores"):
        if tecnologias:
            tec_list = tecnologias.split(',')
            tec_list_str = ','.join([f"'{tec.strip()}'" for tec in tec_list])
            query = f"""
            MATCH (d1:Desarrollador)-[:CREA]->(a:Aplicacion)-[:USA]->(t:Tecnologia)
            WHERE t.name IN [{tec_list_str}]
            WITH d1, collect(t.name) AS Tecnologias_Usadas
            MATCH (d2:Desarrollador)
            WHERE NOT (d1)-[:CREA]->(:Aplicacion)<-[:CREA]-(d2)
            AND all(tn IN [{tec_list_str}] WHERE tn IN Tecnologias_Usadas)
            RETURN d1.name AS Creador1, d2.name AS Creador2
            """
            resultados = run_query(query)
            if resultados:
                for record in resultados:
                    st.write(f"Creador 1: {record['Creador1']}, Creador 2: {record['Creador2']}")
            else:
                st.warning("No se encontraron creadores que nunca hayan trabajado juntos.")
        else:
            st.error("Por favor ingresa una lista de tecnologías.")


def aplicaciones_por_region():
    st.subheader("Aplicaciones por Región")
    region = st.text_input("Nombre de la Región")
    
    if st.button("Buscar Aplicaciones"):
        if region:
            query = f"""
            MATCH (d:Desarrollador)-[:UBICADO_EN]->(l:Ubicacion {{nombre: '{region}'}})-[:CREA]->(a:Aplicacion)
            RETURN a.name AS Aplicacion, l.nombre AS Region
            """
            resultados = run_query(query)
            if resultados:
                for record in resultados:
                    st.write(f"Aplicación: {record['Aplicacion']}, Región: {record['Region']}")
            else:
                st.warning(f"No se encontraron aplicaciones para la región '{region}'.")
        else:
            st.error("Por favor ingresa una región.")


def cargar_datos_csv():
    st.subheader("Cargar Datos desde CSV")
    file = st.file_uploader("Sube un archivo CSV", type=["csv"])
    
    if file:
        data = pd.read_csv(file)
        st.write(data.head())  # Mostrar una vista previa de los datos

        if st.button("Cargar en Neo4j"):
            for _, row in data.iterrows():
                # Crear nodo Aplicacion sin limitar el tamaño y manejando caracteres especiales
                nombre_app = row['Title'] if pd.notna(row['Title']) else 'Null'
                descripcion_app = row['What it Does'] if pd.notna(row['What it Does']) else 'Null'
                
                # Utilizamos json.dumps para escapar correctamente cualquier carácter especial
                nombre_app_escaped = json.dumps(nombre_app)
                descripcion_app_escaped = json.dumps(descripcion_app)
                
                query_app = f"""
                CREATE (a:Aplicacion {{name: {nombre_app_escaped}, descripcion: {descripcion_app_escaped}}})
                """
                run_query(query_app)

                # Crear nodos de Desarrolladores
                desarrolladores = [dev.strip() for dev in str(row['By']).split(',')] if pd.notna(row['By']) else ['Null']
                for dev in desarrolladores:
                    dev_escaped = json.dumps(dev)  # Escapar caracteres especiales
                    query_dev = f"MERGE (d:Desarrollador {{name: {dev_escaped}}})"
                    run_query(query_dev)

                    # Relacionar desarrollador con la aplicación
                    query_rel = f"""
                    MATCH (d:Desarrollador {{name: {dev_escaped}}}), (a:Aplicacion {{name: {nombre_app_escaped}}})
                    CREATE (d)-[:CREA]->(a)
                    """
                    run_query(query_rel)

                # Crear nodos de Tecnologias
                tecnologias = [tech.strip() for tech in str(row['Built With']).split(',')] if pd.notna(row['Built With']) else ['Null']
                for tech in tecnologias:
                    tech_escaped = json.dumps(tech)  # Escapar caracteres especiales
                    query_tec = f"MERGE (t:Tecnologia {{name: {tech_escaped}}})"
                    run_query(query_tec)

                    # Relacionar aplicación con la tecnología
                    query_rel_tec = f"""
                    MATCH (a:Aplicacion {{name: {nombre_app_escaped}}}), (t:Tecnologia {{name: {tech_escaped}}})
                    CREATE (a)-[:USA]->(t)
                    """
                    run_query(query_rel_tec)

                # Crear nodo Ubicacion y relacionarlo con el Desarrollador
                ubicacion = str(row['Location']) if pd.notna(row['Location']) else 'Null'
                ubicacion_escaped = json.dumps(ubicacion)  # Escapar caracteres especiales
                query_ubicacion = f"MERGE (l:Ubicacion {{nombre: {ubicacion_escaped}}})"
                run_query(query_ubicacion)

                for dev in desarrolladores:
                    query_rel_ubic = f"""
                    MATCH (d:Desarrollador {{name: {dev_escaped}}}), (l:Ubicacion {{nombre: {ubicacion_escaped}}})
                    CREATE (d)-[:UBICADO_EN]->(l)
                    """
                    run_query(query_rel_ubic)

            st.success("Datos cargados correctamente con nodos y relaciones.")


def actualizar_aplicacion():
    st.subheader("Actualizar Descripción de la Aplicación")
    nombre_app = st.text_input("Nombre de la aplicación a actualizar")
    nueva_descripcion = st.text_area("Nueva descripción")
    
    if st.button("Actualizar Aplicación"):
        if nombre_app and nueva_descripcion:
            query = f"""
            MATCH (a:Aplicacion {{name: '{nombre_app}'}})
            SET a.descripcion = '{nueva_descripcion}'
            """
            run_query(query)
            st.success(f"Descripción de '{nombre_app}' actualizada con éxito.")
        else:
            st.error("Por favor ingresa el nombre de la aplicación y la nueva descripción.")


def listar_aplicaciones():
    st.subheader("Listar Todas las Aplicaciones")
    
    query = "MATCH (a:Aplicacion) RETURN a.name AS Nombre, a.descripcion AS Descripción"
    
    try:
        aplicaciones = run_query(query)  # Obtener los datos utilizando la función run_query actualizada
    except Exception as e:
        st.error(f"Error al obtener los registros: {str(e)}")
        aplicaciones = []

    if aplicaciones:
        st.write("Lista de Aplicaciones:")
        
        # Crear un DataFrame con las aplicaciones
        df = pd.DataFrame(aplicaciones)
        
        # Mostrar el DataFrame como una tabla en Streamlit
        st.dataframe(df)
    else:
        st.warning("No se encontraron aplicaciones.")



def eliminar_relacion_usa():
    st.subheader("Eliminar Relación 'USA'")
    nombre_app = st.text_input("Nombre de la aplicación")
    nombre_tec = st.text_input("Nombre de la tecnología")
    
    if st.button("Eliminar Relación"):
        if nombre_app and nombre_tec:
            query = f"""
            MATCH (a:Aplicacion {{name: '{nombre_app}'}})-[r:USA]->(t:Tecnologia {{name: '{nombre_tec}'}})
            DELETE r
            """
            run_query(query)
            st.success(f"Relación 'USA' entre '{nombre_app}' y '{nombre_tec}' eliminada con éxito.")
        else:
            st.error("Por favor ingresa tanto el nombre de la aplicación como el de la tecnología.")


def cerrar_conexion():
    if st.session_state.neo4j_conn:
        st.session_state.neo4j_conn.close()
        st.session_state.neo4j_conn = None
        st.success("Conexión a Neo4j cerrada.")


def eliminar_aplicacion():
    st.subheader("Eliminar Aplicación")
    nombre_app = st.text_input("Nombre de la aplicación a eliminar")
    
    if st.button("Eliminar Aplicación"):
        if nombre_app:
            query = f"""
            MATCH (a:Aplicacion {{name: '{nombre_app}'}})
            DETACH DELETE a
            """
            run_query(query)
            st.success(f"Aplicación '{nombre_app}' eliminada con éxito.")
        else:
            st.error("Por favor ingresa un nombre de aplicación.")



# CRUD para Aplicación
def crud_aplicacion():
    st.subheader("CRUD Aplicación")
    acciones = ["Crear Aplicación", "Leer Aplicaciones", "Actualizar Aplicación", "Eliminar Aplicación"]
    accion = st.selectbox("Selecciona una acción", acciones)

    if accion == "Crear Aplicación":
        agregar_aplicacion()
    elif accion == "Leer Aplicaciones":
        listar_aplicaciones()
    elif accion == "Actualizar Aplicación":
        actualizar_aplicacion()
    elif accion == "Eliminar Aplicación":
        eliminar_aplicacion()

# CRUD para Desarrollador
def crud_desarrollador():
    st.subheader("CRUD Desarrollador")
    acciones = ["Crear Desarrollador", "Leer Desarrolladores", "Actualizar Desarrollador", "Eliminar Desarrollador"]
    accion = st.selectbox("Selecciona una acción", acciones)

    if accion == "Crear Desarrollador":
        nombre_dev = st.text_input("Nombre del Desarrollador")
        if st.button("Crear Desarrollador"):
            query = f"CREATE (d:Desarrollador {{name: '{nombre_dev}'}})"
            run_query(query)
            st.success(f"Desarrollador '{nombre_dev}' creado con éxito.")
    elif accion == "Leer Desarrolladores":
        query = "MATCH (d:Desarrollador) RETURN d.name AS Nombre"
        resultados = run_query(query)
        st.write(pd.DataFrame(resultados))
    elif accion == "Actualizar Desarrollador":
        nombre_dev = st.text_input("Nombre del Desarrollador a actualizar")
        nuevo_nombre = st.text_input("Nuevo nombre")
        if st.button("Actualizar Desarrollador"):
            query = f"MATCH (d:Desarrollador {{name: '{nombre_dev}'}}) SET d.name = '{nuevo_nombre}'"
            run_query(query)
            st.success(f"Desarrollador '{nombre_dev}' actualizado a '{nuevo_nombre}'")
    elif accion == "Eliminar Desarrollador":
        nombre_dev = st.text_input("Nombre del Desarrollador a eliminar")
        if st.button("Eliminar Desarrollador"):
            query = f"MATCH (d:Desarrollador {{name: '{nombre_dev}'}}) DELETE d"
            run_query(query)
            st.success(f"Desarrollador '{nombre_dev}' eliminado con éxito.")

# CRUD para Ubicación
def crud_ubicacion():
    st.subheader("CRUD Ubicación")
    acciones = ["Crear Ubicación", "Leer Ubicaciones", "Actualizar Ubicación", "Eliminar Ubicación"]
    accion = st.selectbox("Selecciona una acción", acciones)

    if accion == "Crear Ubicación":
        nombre_ubic = st.text_input("Nombre de la Ubicación")
        if st.button("Crear Ubicación"):
            query = f"CREATE (l:Ubicacion {{nombre: '{nombre_ubic}'}})"
            run_query(query)
            st.success(f"Ubicación '{nombre_ubic}' creada con éxito.")
    elif accion == "Leer Ubicaciones":
        query = "MATCH (l:Ubicacion) RETURN l.nombre AS Nombre"
        resultados = run_query(query)
        st.write(pd.DataFrame(resultados))
    elif accion == "Actualizar Ubicación":
        nombre_ubic = st.text_input("Nombre de la Ubicación a actualizar")
        nuevo_nombre = st.text_input("Nuevo nombre")
        if st.button("Actualizar Ubicación"):
            query = f"MATCH (l:Ubicacion {{nombre: '{nombre_ubic}'}}) SET l.nombre = '{nuevo_nombre}'"
            run_query(query)
            st.success(f"Ubicación '{nombre_ubic}' actualizada a '{nuevo_nombre}'")
    elif accion == "Eliminar Ubicación":
        nombre_ubic = st.text_input("Nombre de la Ubicación a eliminar")
        if st.button("Eliminar Ubicación"):
            query = f"MATCH (l:Ubicacion {{nombre: '{nombre_ubic}'}}) DELETE l"
            run_query(query)
            st.success(f"Ubicación '{nombre_ubic}' eliminada con éxito.")

# CRUD para Tecnología
def crud_tecnologia():
    st.subheader("CRUD Tecnología")
    acciones = ["Crear Tecnología", "Leer Tecnologías", "Actualizar Tecnología", "Eliminar Tecnología"]
    accion = st.selectbox("Selecciona una acción", acciones)

    if accion == "Crear Tecnología":
        nombre_tec = st.text_input("Nombre de la Tecnología")
        if st.button("Crear Tecnología"):
            query = f"CREATE (t:Tecnologia {{name: '{nombre_tec}'}})"
            run_query(query)
            st.success(f"Tecnología '{nombre_tec}' creada con éxito.")
    elif accion == "Leer Tecnologías":
        query = "MATCH (t:Tecnologia) RETURN t.name AS Nombre"
        resultados = run_query(query)
        st.write(pd.DataFrame(resultados))
    elif accion == "Actualizar Tecnología":
        nombre_tec = st.text_input("Nombre de la Tecnología a actualizar")
        nuevo_nombre = st.text_input("Nuevo nombre")
        if st.button("Actualizar Tecnología"):
            query = f"MATCH (t:Tecnologia {{name: '{nombre_tec}'}}) SET t.name = '{nuevo_nombre}'"
            run_query(query)
            st.success(f"Tecnología '{nombre_tec}' actualizada a '{nuevo_nombre}'")
    elif accion == "Eliminar Tecnología":
        nombre_tec = st.text_input("Nombre de la Tecnología a eliminar")
        if st.button("Eliminar Tecnología"):
            query = f"MATCH (t:Tecnologia {{name: '{nombre_tec}'}}) DELETE t"
            run_query(query)
            st.success(f"Tecnología '{nombre_tec}' eliminada con éxito.")
   

def main():
    st.title("Sistema de Gestión de Competencia Gemini - Neo4j")
    
    menu = [
        "Agregar Aplicación", 
        "Consultar Aplicaciones por Tecnología", 
        "Cargar Datos desde CSV", 
        "Eliminar Aplicación", 
        "Actualizar Aplicación", 
        "Listar Aplicaciones", 
        "Eliminar Relación 'USA'",
        "Cerrar Conexión",

        "Aplicaciones por Tecnología", 
        "Aplicaciones Similares", 
        "Creadores de Aplicaciones", 
        "Top 5 Tecnologías Emergentes",
        "Creadores que Nunca Han Trabajado Juntos",
        "Aplicaciones por Región",
        "CRUD Aplicación",
        "CRUD Desarrollador", 
        "CRUD Ubicación", 
        "CRUD Tecnología"
    ]
    
    seleccion = st.sidebar.selectbox("Selecciona una opción", menu)
    
    if seleccion == "Agregar Aplicación":
        agregar_aplicacion()
    elif seleccion == "Consultar Aplicaciones por Tecnología":
        consultar_aplicaciones_por_tecnologia()
    elif seleccion == "Cargar Datos desde CSV":
        cargar_datos_csv()
    elif seleccion == "Eliminar Aplicación":
        eliminar_aplicacion()
    elif seleccion == "Actualizar Aplicación":
        actualizar_aplicacion()
    elif seleccion == "Listar Aplicaciones":
        listar_aplicaciones()
    elif seleccion == "Eliminar Relación 'USA'":
        eliminar_relacion_usa()
    elif seleccion == "Cerrar Conexión":
        cerrar_conexion()
       
    
    # Nuevas consultas:
    elif seleccion == "Aplicaciones por Tecnología":
        aplicaciones_por_tecnologia()
    elif seleccion == "Aplicaciones Similares":
        aplicaciones_similares()
    elif seleccion == "Creadores de Aplicaciones":
        creadores_aplicaciones()
    elif seleccion == "Top 5 Tecnologías Emergentes":
        top_5_tecnologias()
    elif seleccion == "Creadores que Nunca Han Trabajado Juntos":
        creadores_no_trabajaron_juntos()
    elif seleccion == "Aplicaciones por Región":
        aplicaciones_por_region()

     #CRUDS
    elif seleccion == "CRUD Aplicación":
        crud_aplicacion()   
    elif seleccion == "CRUD Ubicación":
        crud_ubicacion()  
    elif seleccion == "CRUD Tecnología":     
        crud_tecnologia()
    elif seleccion == "CRUD Desarrollador":
        crud_desarrollador()

if __name__ == "__main__":
    main()