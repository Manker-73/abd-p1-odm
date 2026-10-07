__author__ = 'Pablo Ramos Criado'
__students__ = 'Nombres_y_Apellidos'


from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
from typing import Generator, Any, Self
from geojson import Point
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
import yaml

def getLocationPoint(address: str) -> Point:
    """ 
    Obtiene las coordenadas de una dirección en formato geojson.Point
    Utilizar la API de geopy para obtener las coordenadas de la direccion
    Cuidado, la API es publica tiene limite de peticiones, utilizar sleeps.
    """
    location = None
    intentos = 0
    maxIntentos = 5
    
    while location is None and intentos < maxIntentos:
        intentos += 1
        try:
            time.sleep(1)
            # Es necesario proporcionar un user_agent para utilizar la API
            location = Nominatim(user_agent="EnVivo_App_DataTeam_Fase1").geocode(address)
        except GeocoderTimedOut:
            # Puede lanzar una excepcion si se supera el tiempo de espera
            # Volver a intentarlo
            continue
            
    # Si tras todos los reintentos no conseguimos coordenadas, lanzamos la excepción
    if location is None:
        raise ValueError(f"No se pudieron obtener coordenadas para la dirección: {address}")
        
    # Devolvemos un GeoJSON de tipo punto con la longitud y latitud almacenadas.
    # Nota: GeoJSON requiere el orden (longitud, latitud)
    return Point((location.longitude, location.latitude))
class Model:
    """ 
    Clase de modelo abstracta
    Crear tantas clases que hereden de esta clase como  
    colecciones/modelos se deseen tener en la base de datos.

    Attributes
    ----------
        required_vars : set[str]
            conjunto de atributos requeridos por el modelo
        admissible_vars : set[str]
            conjunto de atributos admitidos por el modelo
        db : pymongo.collection.Collection
            conexion a la coleccion de la base de datos
    
    Methods
    -------
        __setattr__(name: str, value: str | dict) -> None
            Sobreescribe el metodo de asignacion de valores a los 
            atributos del objeto con el fin de controlar qué atributos 
            son modificados y cuando son modificados.
        __getattr__(name: str) -> Any
            Sobreescribe el metodo de acceso a atributos del objeto 
        save()  -> None
            Guarda el modelo en la base de datos
        delete() -> None
            Elimina el modelo de la base de datos
        find(filter: dict[str, str | dict]) -> ModelCursor
            Realiza una consulta de lectura en la BBDD.
            Devuelve un cursor de modelos ModelCursor
        aggregate(pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor
            Devuelve el resultado de una consulta aggregate.
        find_by_id(id: str) -> dict | None
            Busca un documento por su id utilizando la cache y lo devuelve.
            Si no se encuentra el documento, devuelve None.
        init_class(db_collection: pymongo.collection.Collection, required_vars: set[str], admissible_vars: set[str]) -> None
            Inicializa las variables de clase en la inicializacion del sistema.

    """
    _required_vars: set[str]
    _admissible_vars: set[str]
    _location_var: str | None = None
    _db: pymongo.collection.Collection
    _internal_vars: set[str] = frozenset(('_modified_vars', '_required_vars', '_admissible_vars', '_db', '_data', '_location_var'))

    def __init__(self, **kwargs: dict[str, str | dict | list]) -> None:
        """
        Inicializa el modelo con los valores proporcionados en kwargs
        Comprueba que los valores proporcionados en kwargs son admitidos
        por el modelo y que las atributos requeridos son proporcionadas.
        """
        self._data: dict[str, str | dict | list] = {}
        # Inicializamos el set para llevar el control de atributos modificados
        self._modified_vars = set()
        
        # 1. Comprobar que no falta ningún atributo requerido
        atributos_faltantes = self._required_vars - kwargs.keys()
        if atributos_faltantes:
            raise ValueError(f"Faltan atributos requeridos para el modelo: {atributos_faltantes}")
            
        # 2. Comprobar que no hay atributos no admitidos (ignoramos '_id' de Mongo)
        atributos_invalidos = kwargs.keys() - self._required_vars - self._admissible_vars - {'_id'}
        if atributos_invalidos:
            raise ValueError(f"Se han proporcionado atributos no admitidos: {atributos_invalidos}")

        # Asigna todos los valores en kwargs a las atributos con 
        # nombre las claves en kwargs
        self._data.update(kwargs)

    def __setattr__(self, name: str, value: str | dict) -> None:
        """ Sobreescribe el metodo de asignacion de valores a los 
        atributos del objeto con el fin de controlar que atributos 
        son modificados y cuando son modificados.
        """
        if name in self._internal_vars:
            super().__setattr__(name, value)
            return
            
        # 1. Comprobar que el atributo a modificar es válido
        if name not in self._required_vars and name not in self._admissible_vars and name != '_id':
            raise ValueError(f"No se puede asignar el atributo '{name}' porque no es admitido por el modelo.")

        # 2. Registrar el atributo como modificado
        self._modified_vars.add(name)

        # Asigna el valor value a la variable name
        self._data[name] = value

    def __setattr__(self, name: str, value: str | dict) -> None:
        """ Sobreescribe el metodo de asignacion de valores a los 
        atributos del objeto con el fin de controlar que atributos 
        son modificados y cuando son modificados.
        """
        if name in self._internal_vars:
            super().__setattr__(name, value)
            return
        #TODO
        # Realizar las comprabociones y gestiones necesarias
        # antes de la asignacion.

        # Asigna el valor value a la variable name
        self._data[name] = value

    def __getattr__(self, name: str) -> Any:
        """ Sobreescribe el metodo de acceso a atributos del objeto
        __getattr__ solo es llamado cuando no encuentra el atributo
        en el objeto 
        """
        if name in self._internal_vars:
            return super().__getattribute__(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError
        
    def save(self) -> None:
        """
        Guarda el modelo en la base de datos
        Si el modelo no existe en la base de datos, se crea un nuevo
        documento con los valores del modelo. En caso contrario, se
        actualiza el documento existente con los nuevos valores del
        modelo.
        """
        #TODO
        pass #No olvidar eliminar esta linea una vez implementado

    def save(self) -> None:
        """
        Guarda el modelo en la base de datos
        Si el modelo no existe en la base de datos, se crea un nuevo
        documento con los valores del modelo. En caso contrario, se
        actualiza el documento existente con los nuevos valores del
        modelo.
        """
        es_nuevo = '_id' not in self._data
        
        # 1. Gestionar la geolocalización antes de guardar
        if self._location_var and self._location_var in self._data:
            # Geolocalizamos si el documento es nuevo o si se ha modificado la dirección
            if es_nuevo or self._location_var in self._modified_vars:
                direccion = self._data[self._location_var]
                punto_geojson = getLocationPoint(direccion)
                campo_loc = f"{self._location_var}_loc"
                
                self._data[campo_loc] = punto_geojson
                
                # Si estamos actualizando, registramos también la localización modificada
                if not es_nuevo:
                    self._modified_vars.add(campo_loc)

        # 2. Persistir los datos en MongoDB
        if es_nuevo:
            # Documento nuevo: insertamos todo el diccionario _data
            resultado = self._db.insert_one(self._data)
            self._data['_id'] = resultado.inserted_id
        else:
            # Documento existente: actualizamos solo lo estrictamente modificado
            if self._modified_vars:
                datos_a_actualizar = {campo: self._data[campo] for campo in self._modified_vars}
                self._db.update_one({'_id': self._data['_id']}, {'$set': datos_a_actualizar})
                
        # 3. Limpiamos el registro de variables modificadas tras el éxito
        self._modified_vars.clear()

    def delete(self) -> None:
        """
        Elimina el modelo de la base de datos
        """
        # Solo podemos borrar si existe un _id
        if '_id' in self._data:
            self._db.delete_one({'_id': self._data['_id']})
            # Opcional: quitamos el _id de memoria para reflejar que ya no está en la base
            del self._data['_id']

    @classmethod
    def find(cls, filter: dict[str, str | dict]) -> Any:
        """ 
        Utiliza el metodo find de pymongo para realizar una consulta
        de lectura en la BBDD.
        find debe devolver un cursor de modelos ModelCursor
        """ 
        # cls es el puntero a la clase actual
        # Realizamos la consulta cruda a pymongo
        cursor_pymongo = cls._db.find(filter)
        
        # Devolvemos el cursor envuelto en nuestro iterador personalizado
        return ModelCursor(cls, cursor_pymongo)

    @classmethod
    def aggregate(cls, pipeline: list[dict]) -> pymongo.command_cursor.CommandCursor:
        """ 
        Devuelve el resultado de una consulta aggregate. 
        No hay nada que hacer en esta funcion.
        Se utilizara para las consultas solicitadas
        en el segundo proyecto de la practica.

        Parameters
        ----------
            pipeline : list[dict]
                lista de etapas de la consulta aggregate 
        Returns
        -------
            pymongo.command_cursor.CommandCursor
                cursor de pymongo con el resultado de la consulta
        """ 
        return cls._db.aggregate(pipeline)
    
    @classmethod
    def find_by_id(cls, id: str) -> Self | None:
        """ 
        NO IMPLEMENTAR HASTA EL TERCER PROYECTO
        Busca un documento por su id utilizando la cache y lo devuelve.
        Si no se encuentra el documento, devuelve None.

        Parameters
        ----------
            id : str
                id del documento a buscar
        Returns
        -------
            Self | None
                Modelo del documento encontrado o None si no se encuentra
        """ 
        #TODO
        pass

    @classmethod
    def init_class(cls, db_collection: pymongo.collection.Collection, indexes:dict[str,str], required_vars: set[str], admissible_vars: set[str]) -> None:
        """ 
        Inicializa los atributos de clase en la inicializacion del sistema.
        Aqui se deben inicializar o asegurar los indices. Tambien se puede
        alguna otra inicialización/comprobaciones o cambios adicionales
        que estime el alumno.

        Parameters
        ----------
            db_collection : pymongo.collection.Collection
                Conexion a la collecion de la base de datos.
            indexes: Dict[str,str]
                Set de indices y tipo de indices para la coleccion
            required_vars : set[str]
                Set de atributos requeridos por el modelo
            admissible_vars : set[str] 
                Set de atributos admitidos por el modelo
        """
        cls._db = db_collection
        cls._required_vars = required_vars
        cls._admissible_vars = admissible_vars
        
        # Recorrer indexes y crear cada índice segun su tipo
        if indexes:
            for campo, tipo in indexes.items():
                if tipo == "unique":
                    # Índice único ascendente
                    cls._db.create_index([(campo, pymongo.ASCENDING)], unique=True)
                elif tipo == "asc":
                    # Índice ascendente normal
                    cls._db.create_index([(campo, pymongo.ASCENDING)])
                elif tipo == "geosphere":
                    # Índice geoespacial 2dsphere
                    cls._db.create_index([(campo, pymongo.GEOSPHERE)])

class ModelCursor:
    """ 
    Cursor para iterar sobre los documentos del resultado de una
    consulta. Los documentos deben ser devueltos en forma de objetos
    modelo.

    Attributes
    ----------
        model_class : Model
            Clase para crear los modelos de los documentos que se iteran.
        cursor : pymongo.cursor.Cursor
            Cursor de pymongo a iterar

    Methods
    -------
        __iter__() -> Generator
            Devuelve un iterador que recorre los elementos del cursor
            y devuelve los documentos en forma de objetos modelo.
    """

    def __init__(self, model_class: Model, cursor: pymongo.cursor.Cursor):
        """
        Inicializa el cursor con la clase de modelo y el cursor de pymongo

        Parameters
        ----------
            model_class : Model
                Clase para crear los modelos de los documentos que se iteran.
            cursor: pymongo.cursor.Cursor
                Cursor de pymongo a iterar
        """
        self.model = model_class
        self.cursor = cursor
    
    def __iter__(self) -> Generator:
        """
        Devuelve un iterador que recorre los elementos del cursor
        y devuelve los documentos en forma de objetos modelo.
        """
        # alive nos indica si quedan elementos en el cursor de MongoDB
        while self.cursor.alive:
            try:
                # Extraemos el siguiente diccionario usando next()
                documento = self.cursor.next()
                
                # Desempaquetamos el diccionario (**documento) para instanciar 
                # un nuevo objeto del modelo correspondiente y lo devolvemos con yield
                yield self.model(**documento)
                
            except StopIteration:
                # Cuando next() agota los elementos, lanza StopIteration
                break

def initApp(definitions_path: str = "./models.yml", mongodb_uri="mongodb://localhost:27017/", db_name="abd", scope=globals()) -> None:
    """ 
    Declara las clases que heredan de Model para cada uno de los 
    modelos de las colecciones definidas en definitions_path.
    Inicializa las clases de los modelos proporcionando los indices y 
    atributos admitidos y requeridos para cada una de ellas y la conexión a la
    collecion de la base de datos.
    """
    # Inicializar cliente de base de datos
    client = MongoClient(mongodb_uri)
    db = client[db_name]

    # Leer el fichero de definiciones de modelos YAML
    with open(definitions_path, 'r', encoding='utf-8') as f:
        definitions = yaml.safe_load(f)

    # Declarar tantas clases modelo colecciones existan en la base de datos
    if definitions:
        for collection_name, config in definitions.items():
            # Crear la clase dinámicamente en tiempo de ejecución
            scope[collection_name] = type(collection_name, (Model,), {})
            
            # Obtener los atributos como conjuntos (sets)
            required_vars = set(config.get("required_vars") or [])
            admissible_vars = set(config.get("admissible_vars") or [])
            
            # Preparar el diccionario de índices
            indexes = {}
            if config.get("unique_indexes"):
                for idx in config["unique_indexes"]:
                    indexes[idx] = "unique"
                    
            if config.get("regular_indexes"):
                for idx in config["regular_indexes"]:
                    indexes[idx] = "asc"
                    
            # Gestionar la variable de localización
            location_var = config.get("location_index")
            if location_var:
                # Asignar a la variable interna el nombre base del campo
                scope[collection_name]._location_var = location_var
                # Añadir el índice geoespacial sobre el sufijo _loc
                indexes[f"{location_var}_loc"] = "geosphere"

            # Inicializar la clase con la configuración recopilada
            db_collection = db[collection_name]
            scope[collection_name].init_class(
                db_collection=db_collection, 
                indexes=indexes, 
                required_vars=required_vars, 
                admissible_vars=admissible_vars
            )
if __name__ == '__main__':
    
    # Inicializar base de datos y modelos con initApp
    #TODO
    initApp()

    #Ejemplo
    m = MiModelo(nombre="Pablo", apellido="Ramos", edad=18)
    m.save()
    m.nombre="Pedro"
    print(m.nombre)

    # Hacer pruebas para comprobar que funciona correctamente el modelo
    #TODO
    # Crear modelo

    # Asignar nuevo valor a variable admitida del objeto 

    # Asignar nuevo valor a variable no admitida del objeto 

    # Guardar

    # Asignar nuevo valor a variable admitida del objeto

    # Guardar

    # Buscar nuevo documento con find

    # Obtener primer documento

    # Modificar valor de variable admitida

    # Guardar