import os
import numpy as np
import colorsys


def tiene_elementos_repetidos(lista):
    # Convertir la lista a un conjunto para eliminar duplicados
    conjunto_sin_duplicados = set(lista)

    # La longitud del conjunto es diferente de la longitud original si hay duplicados
    return len(conjunto_sin_duplicados) != len(lista)

def decimal_a_hexadecimal(valor):
    hex_value = hex(int(valor))[2:]
    return hex_value.zfill(6)
def generate_unique_colors_hex(num_colors):
    # Generar colores en el espacio HSV con tonos equidistantes
    global sumador
    sumador = 16777216//num_colors
    print("Sum to generate colors is")
    print(sumador)
    color = sumador
    hex_colors= np.zeros(num_colors)
    order_vector = np.arange(1636)

    # Barajar (shuffle) el vector para obtener un orden aleatorio
    np.random.shuffle(order_vector)
    for i in range(num_colors):
        hex_colors[order_vector[i]] = color
        color = color+sumador

    lista_hexadecimal = np.vectorize(decimal_a_hexadecimal)(hex_colors)


    return  lista_hexadecimal

def construir_global_semantic(archivos_semanticos):
    global_semantic = {}
    id_categoria = 0

    for linea in archivos_semanticos:
        partes = linea.strip().split(',')

        if len(partes) == 4:
            categoria = partes[2].strip().replace('"', '')
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
def hex_to_decimal(hex_string):
    # Convertir el string hexadecimal a decimal
    decimal_value = int(hex_string, 16)
    return decimal_value

def guardar_global_semantic(global_semantic, archivo_salida,rgb_list):
    j = 0
    with open(archivo_salida, 'w') as archivo:
        archivo.write("ID,COLOR,CATEGORIA\n")
        for categoria, info in global_semantic.items():
            archivo.write(f"{info['id']},{rgb_list[j]},{categoria}\n")
            j = j+1

def guardar_global_semantic_2(global_semantic, archivo_salida):
    j = 0
    with open(archivo_salida, 'w') as archivo:
        archivo.write("ID,COLOR,CATEGORIA\n")
        for categoria in global_semantic.items():
            archivo.write(f"{categoria[1]['id']},{categoria[1]['color'].upper()},{categoria[0]}\n")

def apply_new_id(global_semantic, rgb_list_1635_categories):
    counter = 0
    for category in global_semantic:
        global_semantic[category]["color"] = rgb_list_1635_categories[counter]
        global_semantic[category]["id"] = int(hex_to_decimal(global_semantic[category]["color"]) / sumador)
        counter = counter + 1
    return global_semantic

def actualizar_archivos(folder_path,global_semantic):
    for carpeta_actual, _, archivos in os.walk(folder_path):
        # Busca archivos que coincidan con el patrón "*.semantic.txt"
        for archivo in archivos:
            if archivo.endswith(".semantic.txt"):
                file_path = os.path.join(carpeta_actual, archivo)
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                with open(file_path, 'w') as file:
                    # Escribir la primera línea sin cambios
                    file.write(lines[0])

                    # Actualizar las líneas restantes
                    for line in lines[1:]:
                        parts = line.strip().split(',')
                        categoria = parts[2].strip('"')
                        if categoria in global_semantic:
                            parts[0] = str(global_semantic[categoria]["id"])
                        file.write(','.join(parts) + '\n')

# Reemplaza 'directorio_a_buscar' con la ruta del directorio que deseas explorar
train_search_directory = "/home/carlosgutierrez/data/scene_datasets/semantics/hm3d/train"
archivos_semantics_train = buscar_archivos_semanticos(train_search_directory)
val_search_directory = "/home/carlosgutierrez/data/scene_datasets/semantics/hm3d/val"
archivos_semantics_val = buscar_archivos_semanticos(val_search_directory)
archivos_semantics_train.extend(archivos_semantics_val)
global_semantic = construir_global_semantic(archivos_semantics_train)
ruta_del_global_semantic = "/home/carlosgutierrez/repositorios/semnav/scripts/global_semantic.semantic.txt"
rgb_list_1635_categories = generate_unique_colors_hex(1636)
#repeat = tiene_elementos_repetidos(rgb_list_1635_categories[1:])
global_semantic = apply_new_id(global_semantic,rgb_list_1635_categories)
print(global_semantic)
guardar_global_semantic_2(global_semantic,ruta_del_global_semantic)
actualizar_archivos(train_search_directory, global_semantic)
actualizar_archivos(val_search_directory, global_semantic)
#guardar_global_semantic(global_semantic,ruta_del_global_semantic,rgb_list_1635_categories)
