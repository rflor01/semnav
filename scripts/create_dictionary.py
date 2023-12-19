import os


def construir_global_semantic(archivos_semanticos):
    global_semantic = {}
    id_categoria = 1

    for linea in archivos_semanticos:
        partes = linea.strip().split(',')

        if len(partes) == 4:
            categoria = partes[2]
            color = partes[1]

            # Si la categoría no existe en global_semantic, agrégala
            if categoria not in global_semantic:
                global_semantic[categoria] = {"id": id_categoria, "color": color}
                id_categoria += 1

    return global_semantic
def buscar_archivos_semanticos(directorio_raiz):
    archivos_semanticos = []
    # Recorre todos los directorios y subdirectorios
    for carpeta_actual, _, archivos in os.walk(directorio_raiz):
        # Busca archivos que coincidan con el patrón "*.semantic.txt"
        for archivo in archivos:
            if archivo.endswith(".semantic.txt"):
                # Imprime la ruta completa del archivo encontrado
                ruta_completa = os.path.join(carpeta_actual, archivo)
                with open(ruta_completa, 'r') as archivo:
                    lineas = archivo.readlines()[1:]  # Ignora la primera línea
                    archivos_semanticos.extend(lineas)
    return archivos_semanticos

def guardar_global_semantic(global_semantic, archivo_salida):
    with open(archivo_salida, 'w') as archivo:
        archivo.write("ID,COLOR,CATEGORIA\n")
        for categoria, info in global_semantic.items():
            archivo.write(f"{info['id']},{info['color']},{categoria}\n")

# Reemplaza 'directorio_a_buscar' con la ruta del directorio que deseas explorar
directorio_a_buscar = "/home/rafa/repositorios/semnav/data/scene_datasets/hm3d/train"
archivos_semantics = buscar_archivos_semanticos(directorio_a_buscar)
global_semantic = construir_global_semantic(archivos_semantics)
ruta_del_global_semantic = "/home/rafa/repositorios/semnav/scripts/global_semantic.semantic.txt"
guardar_global_semantic(global_semantic,ruta_del_global_semantic)

