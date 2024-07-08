from pygltflib import GLTF2
import base64
import os
from PIL import Image
import numpy as np
import shutil
import concurrent.futures
def eliminar_contenido_carpeta(carpeta):
    """
    Elimina todo el contenido de una carpeta, incluyendo archivos y subcarpetas.

    :param carpeta: Ruta de la carpeta cuyo contenido se va a eliminar.
    """
    try:
        for elemento in os.listdir(carpeta):
            elemento_path = os.path.join(carpeta, elemento)
            if os.path.isfile(elemento_path) or os.path.islink(elemento_path):
                os.unlink(elemento_path)
            elif os.path.isdir(elemento_path):
                shutil.rmtree(elemento_path)
        print(f"Todo el contenido de la carpeta '{carpeta}' ha sido eliminado.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

def find_directories_with_semantic_txt(base_path):
    result_dirs = []

    for root_dir in ['minival', 'train', 'val']:
        current_path = os.path.join(base_path, root_dir)

        for subdir, _, files in os.walk(current_path):
            if any(file.endswith('.semantic.txt') for file in files):
                result_dirs.append(subdir)

    return result_dirs

def txt_updater(ruta_fichero, diccionario):
    # Inicializamos una lista para almacenar las líneas actualizadas
    lineas_actualizadas = []

    # Abrimos el archivo para lectura
    with open(ruta_fichero, 'r') as file:
        # Leemos todas las líneas del archivo
        lineas = file.readlines()

        # Añadimos la primera línea (encabezado) sin cambios
        lineas_actualizadas.append(lineas[0])

        # Iteramos sobre cada línea, exceptuando la primera
        for linea in lineas[1:]:
            # Eliminamos posibles espacios en blanco al inicio y final de la línea
            linea = linea.strip()
            # Separamos la línea por comas
            partes = linea.split(',')
            # Extraemos la categoría
            categoria = partes[2].replace('"', '')

            # Si la categoría está en el diccionario, actualizamos id y color
            if categoria in diccionario:
                id_categoria, color = diccionario.get(categoria, [383, "3A67F6"])
                partes[0] = str(id_categoria)
                partes[1] = color

            # Reconstruimos la línea y la añadimos a la lista de líneas actualizadas
            linea_actualizada = ','.join(partes)
            lineas_actualizadas.append(linea_actualizada + '\n')
    # Escribimos las líneas actualizadas en el archivo, sobrescribiéndolo
    with open(ruta_fichero, 'w') as file:
        file.writelines(lineas_actualizadas)


def delete_repetitions(ruta_fichero):
    # Inicializamos un conjunto para almacenar las combinaciones únicas de (id, categoria)
    combinaciones_unicas = set()
    # Inicializamos una lista para almacenar las líneas filtradas
    lineas_filtradas = []

    # Abrimos el archivo para lectura
    with open(ruta_fichero, 'r') as file:
        # Leemos todas las líneas del archivo
        lineas = file.readlines()

        # Añadimos la primera línea (encabezado) sin cambios
        lineas_filtradas.append(lineas[0])

        # Iteramos sobre cada línea, exceptuando la primera
        for linea in lineas[1:]:
            # Eliminamos posibles espacios en blanco al inicio y final de la línea
            linea = linea.strip()
            # Separamos la línea por comas
            partes = linea.split(',')
            # Extraemos el id y la categoría
            id_room = int(partes[3])
            categoria = partes[2]

            # Creamos una tupla con el id y la categoría
            combinacion = (categoria,id_room)

            # Si la combinación no está en el conjunto, la añadimos y guardamos la línea
            if combinacion not in combinaciones_unicas:
                combinaciones_unicas.add(combinacion)
                lineas_filtradas.append(linea + '\n')

    # Escribimos las líneas filtradas en un nuevo archivo o sobrescribimos el archivo original
    with open(ruta_fichero, 'w') as file:
        file.writelines(lineas_filtradas)

def modify_scene_colors(scene_txt_path, global_dictionary,images_directory):


    # Abrimos el archivo para lectura
    with open(scene_txt_path, 'r') as file:
        # Leemos todas las líneas del archivo
        lineas = file.readlines()

        # Iteramos sobre cada línea, exceptuando la primera
        for linea in lineas[1:]:
            # Eliminamos posibles espacios en blanco al inicio y final de la línea
            linea = linea.strip()
            # Separamos la línea por comas
            partes = linea.split(',')
            categoria = partes[2].replace('"', '')
            color = partes[1]
            new_color = global_dictionary.get(categoria,[0, "135DF6"])[1]
            print("Color", color)
            print("Color de reemplazo", new_color)
            find_and_replace_color_in_images(directory=images_directory,hex_color=color,hex_replacement_color=new_color)


def clean_categories(path):
    with open(path, 'r', encoding='utf-8') as archivo:
        lines = archivo.readlines()

    with open(path, 'w', encoding='utf-8') as archivo:
        for i, line in enumerate(lines):
            if i == 0:
                archivo.write(line)  # Escribir la primera línea tal cual
            else:
                partes = line.strip().split(',')
                if len(partes) >= 3:
                    # Eliminar espacios al final de la categoría
                    categoria = partes[2].strip().strip('"').rstrip()
                    partes[2] = f'"{categoria}"'
                archivo.write(','.join(partes) + '\n')
def obtain_global_dictionary(ruta_fichero):
    # Inicializamos el diccionario vacío
    diccionario = {}

    # Abrimos el archivo para lectura
    with open(ruta_fichero, 'r') as file:
        # Leemos todas las líneas del archivo
        lineas = file.readlines()

        # Iteramos sobre cada línea, exceptuando la primera
        for linea in lineas[:]:
            # Eliminamos posibles espacios en blanco al inicio y final de la línea
            linea = linea.strip()
            # Separamos la línea por comas
            partes = linea.split(',')
            # Extraemos el id, la categoría y el color
            id_categoria = int(partes[0])
            categoria = partes[1]
            color = partes[2]
            # Añadimos la entrada al diccionario
            diccionario[categoria] = (id_categoria, color)

    return diccionario
def gltf_path_construct(semantic_directory):
    # Obtener el nombre del directorio (última parte de la ruta)
    base_directory = os.path.basename(semantic_directory)
    last_part = base_directory.split('-')
    # Construir el nuevo path añadiendo el nombre del directorio y la extensión deseada
    nuevo_path = os.path.join(semantic_directory, f"{last_part[1]}.semantic.glb")
    return nuevo_path

def semantic_txt_path_construct(semantic_directory):
    # Obtener el nombre del directorio (última parte de la ruta)
    base_directory = os.path.basename(semantic_directory)
    last_part = base_directory.split('-')
    # Construir el nuevo path añadiendo el nombre del directorio y la extensión deseada
    nuevo_path = os.path.join(semantic_directory, f"{last_part[1]}.semantic.txt")
    return nuevo_path

def modificar_extension(gltf_path):
    # Asegúrate de que el archivo tenga la extensión correcta antes de modificarla
    if gltf_path.endswith('.semantic.glb'):
        # Generar la nueva ruta cambiando la extensión del archivo
        new_gltf_path = gltf_path.replace('.semantic.glb', '.semantic.modified.glb')
        return new_gltf_path
    else:
        raise ValueError("El archivo no tiene la extensión '.semantic.glb'")

def save_images_from_gltf(gltf_file_path, output_directory):
    # Cargar el archivo GLB
    gltf = GLTF2().load(gltf_file_path)

    # Asegurarse de que el directorio de salida existe
    os.makedirs(output_directory, exist_ok=True)

    # Iterar sobre las imágenes en el archivo GLB/GLTF
    for i, image in enumerate(gltf.images):
        if image.uri:
            # La imagen está incrustada como un URI de datos base64
            if image.uri.startswith("data:image"):
                # Extraer el tipo de imagen
                mime_type, base64_data = image.uri.split(",", 1)
                image_type = mime_type.split("/")[1].split(";")[0]
                image_data = base64.b64decode(base64_data)

                # Guardar la imagen
                image_path = os.path.join(output_directory, f"image_{i}.{image_type}")
                with open(image_path, "wb") as img_file:
                    img_file.write(image_data)
            else:
                # La imagen está referenciada por una URI externa
                image_path = os.path.join(output_directory, os.path.basename(image.uri))
                with open(image.uri, "rb") as img_file:
                    with open(image_path, "wb") as out_file:
                        out_file.write(img_file.read())
        elif image.bufferView is not None:
            # La imagen está incrustada en un buffer
            buffer_view = gltf.bufferViews[image.bufferView]
            buffer = gltf.buffers[buffer_view.buffer]
            buffer_data = gltf.get_data_from_buffer_uri(buffer.uri)
            image_data = buffer_data[buffer_view.byteOffset:buffer_view.byteOffset + buffer_view.byteLength]

            # Intentar determinar el tipo de imagen a partir de los primeros bytes
            if image_data.startswith(b'\x89PNG\r\n\x1a\n'):
                image_type = "png"
            elif image_data.startswith(b'\xff\xd8\xff'):
                image_type = "jpeg"
            else:
                image_type = "bin"  # Tipo binario desconocido

            # Guardar la imagen
            image_path = os.path.join(output_directory, f"image_{i}.{image_type}")
            with open(image_path, "wb") as img_file:
                img_file.write(image_data)
        else:
            print(f"No se pudo extraer la imagen {i}")
    return len(gltf.images)

def replace_image_in_gltf(gltf_file_path, new_image_path, image_index, output_gltf_file_path):
    # Cargar el archivo GLB
    gltf = GLTF2().load(gltf_file_path)

    # Leer la nueva imagen y codificarla en base64
    with open(new_image_path, "rb") as img_file:
        new_image_data = img_file.read()
    new_image_base64 = base64.b64encode(new_image_data).decode('utf-8')

    # Crear un nuevo URI de datos base64 para la imagen
    new_image_uri = f"data:image/png;base64,{new_image_base64}"

    # Reemplazar la imagen en el archivo GLB
    if image_index < len(gltf.images):
        gltf.images[image_index].uri = new_image_uri
        # Si existía un bufferView, lo eliminamos ya que no puede coexistir con el URI
        if hasattr(gltf.images[image_index], 'bufferView'):
            delattr(gltf.images[image_index], 'bufferView')
    else:
        print(f"El índice de imagen {image_index} está fuera de rango.")
        return

    # Guardar el archivo GLB modificado
    gltf.save(output_gltf_file_path)
    print(f"Imagen {image_index} reemplazada y guardada en {output_gltf_file_path}.")


def hex_to_rgb(hex_color):
    """Convierte un color hexadecimal a RGB. Si falla, devuelve el color blanco (255, 255, 255)."""
    try:
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, TypeError):
        # Devuelve el color blanco si hay un error en la conversión
        return (58, 103, 246)


def color_in_image(image_path, target_color):
    """Revisa si el color objetivo está presente en la imagen."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')  # Asegúrate de que la imagen está en formato RGB
        pixels = img.load()

        for y in range(img.height):
            for x in range(img.width):
                if pixels[x, y] == target_color:
                    return True
    return False


def replace_color_in_image(image_path, target_color, replacement_color):
    """Reemplaza el color objetivo por el color de reemplazo en la imagen."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')  # Asegúrate de que la imagen está en formato RGB
        data = np.array(img)

        # Definir el color objetivo y el color de reemplazo
        target_color = np.array(target_color, dtype=np.uint8)
        replacement_color = np.array(replacement_color, dtype=np.uint8)

        # Crear una máscara donde el color objetivo coincide
        mask = np.all(data == target_color, axis=-1)

        # Aplicar el color de reemplazo usando la máscara
        data[mask] = replacement_color

        # Convertir de nuevo a imagen y guardar
        modified_img = Image.fromarray(data)

        # Guardar la imagen modificada en el directorio de salida
        file_name, file_extension = os.path.splitext(image_path)
        modified_file_name = image_path
        modified_img.save(modified_file_name)
        print(f"Imagen modificada guardada en: {modified_file_name}")


def process_image(image_path, target_color, replacement_color):
    """Procesa una imagen para buscar y reemplazar un color específico."""
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        data = np.array(img)
        target_color_np = np.array(target_color, dtype=np.uint8)

        if np.any(np.all(data == target_color_np, axis=-1)):
            replace_color_in_image(image_path, target_color, replacement_color)
            return image_path
    return None

def find_and_replace_color_in_images(directory, hex_color, hex_replacement_color):
    """Encuentra imágenes que contienen el color especificado y lo reemplaza."""
    target_color = hex_to_rgb(hex_color)
    replacement_color = hex_to_rgb(hex_replacement_color)
    found_images = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.png'):
                    image_path = os.path.join(root, file)
                    futures.append(executor.submit(process_image, image_path, target_color, replacement_color))

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found_images.append(result)
                print("¡Color encontrado y reemplazado en:", result)

    return found_images

scene_dataset_path = "/home/rafa/rafarepos/semnav/data/modify_scene_datasets/hm3d"
log_txt = "modify_dataset_log.txt"
semantic_directories = find_directories_with_semantic_txt(scene_dataset_path)
for semantic_directory in semantic_directories:
    gltf_path = gltf_path_construct(semantic_directory)
    with open(log_txt,'a') as file:
        file.write(f'A escribir {gltf_path} \n')
    scene_txt_path = semantic_txt_path_construct(semantic_directory)
    output_path = "glb_images"
    clean_categories(scene_txt_path)
    new_gltf_path = modificar_extension(gltf_path)
    n_images = save_images_from_gltf(gltf_path, output_path)
    global_dictionary_txt_path = "last_global_dictionary.txt"
    global_dictionary = obtain_global_dictionary(global_dictionary_txt_path)
    modify_scene_colors(scene_txt_path,global_dictionary,output_path)
    for i in range(n_images):
        iter_image = f"image_{i}.png"
        iter_image_path = os.path.join(output_path,iter_image)
        replace_image_in_gltf(gltf_path,iter_image_path,i,gltf_path)
    delete_repetitions(scene_txt_path)
    txt_updater(scene_txt_path,global_dictionary)
    eliminar_contenido_carpeta(output_path)
    with open(log_txt,'a') as file:
        file.write(f'Escrito {gltf_path} \n')