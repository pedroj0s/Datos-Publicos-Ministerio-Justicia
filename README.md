# Datos públicos del Ministerio de Justicia de España y del Consejo General del Poder Judicial

<img src="https://github.com/user-attachments/assets/cab172b9-2d26-4141-a82f-e6011008cc1f" alt="Datos públicos sobre la Justicia Española" width="300">


## Descripción del Proyecto

Este proyecto tiene como objetivo facilitar la recopilación de información pública proporcionada por el [Ministerio de Justicia](https://www.mjusticia.gob.es) y el [Consejo General del Poder Judicial](https://www.poderjudicial.es/), por ejemplo:

1. [x] [Listado de registros civiles existentes y su ubicación][1].
2. [x] [Información de contacto de cada registro civil][1].
3. [ ] Información sobre el titular/responsable de cada registro civil.
4. [x] [Información sobre juzgados existentes y su ubicación][2].
5. [x] [Información de contacto sobre cada uno de los juzgados][2].
6. [x] [Titulares de cada juzgado según la información pública del CGPJ -Consejo General del Poder Judicial][2].

El proyecto incluye scripts en Python que automatizan la recolección de estos datos a través de APIs públicas, scraping web (cuando sea permitido), o el procesamiento de archivos descargables proporcionados por el Ministerio de Justicia.

Con este repositorio, se busca centralizar y organizar la información para análisis o uso en otras aplicaciones.

En caso de usar el código fuente o los datos del repositorio en cualquier otro proyecto, **se requiere citar la autoría**.

## Ficheros JSON con datos actualizados (11/12/2024):
1. [Listado de registros civiles existentes][1].
2. [Información sobre juzgados, sus respectivas ubicaciones, información de contacto e información sobre los titulares][2].

   
### Estructura del fichero con los datos públicos sobre Registros Civiles obtenidos desde la web del Ministerio del Interior

El archivo JSON [registros-civiles-datos-capturados.json][1] contiene información estructurada sobre los registros civiles en España, organizada por provincias. A continuación, se detalla la estructura del archivo:
```
{
    "provincias": [
        {
            "nombre": "Nombre de la provincia",
            "registros": [
                {
                    "nombre": "Nombre del registro civil",
                    "municipio": "Nombre del municipio",
                    "direccion": "Dirección del registro",
                    "codigo_postal": "Código postal",
                    "telefono": "Número de teléfono",
                    "email": "Correo electrónico",
                    "horario": "Horario de atención",
                    "observaciones": "Información adicional"
                }
                // Más registros civiles...
            ]
        }
        // Más provincias...
    ]
}
```

### Estructura del ficheros con los datos públicos sobre los Juzgados Españoles obtenidos desde la web del CGPJ -Consejo General del Poder Judicial-
Este fichero contiene tanto la información general sobre los juzgados y las URLs desde las que ha sido obtenida esta información como el detalle de los mismos y un listado de sus titulares.

#### Raíz del JSON
El objeto raíz contiene las claves ```provincias``` y ```detalleJuzgados```, una contiene las fuentes de datos relativos a los juzgados de cada provincia y la otra el detalle de cada uno de los juzgados existentes a nivel estatal.

- **`provincias`**: Lista de objetos, cada uno representando una provincia y sus respectivas páginas con información general sobre los juzgados ubicados en la provincia.
- **`detalleJuzgados`**: Lista de objetos, cada uno representando el detalle de un juzgado.

#### Estructura de cada objeto en la clave `provincias`
Cada objeto dentro de `provincias` tiene los siguientes campos:

```
{
  "provincias": [
    {
      "nombre": "string",
      "juzgados": [
        {
          "codigo-postal": "string", // Código postal 
          "direccion": "string",     // Dirección del juzgado
          "municipio": "string",     // Localidad donde se encuentra
          "nombre": "string",        // Nombre del juzgado
          "telefono/s": "string",    // Teléfonos de contacto
          "url": "string"            // Url donde se pueden consultar los detalles del juzgado
        }
      ],
      "paginasJuzgados": ["string", "string"], // Páginas desde se ha obtenido la información del juzgado, no incluye la primera
      "url": "string"                          // Página inicial desde donde se ha obtenido la información de los juzgados
    }
    // Otras provincias...
  ]
}
```


#### Estructura de cada objeto en la clave `detalleJuzgados`
```
{
  "detalleJuzgados": [
    {
      "codigo-postal": "string",                  // Código postal del juzgado
      "comunidad-autonoma": "string",            // Comunidad Autónoma a la que pertenece
      "direccion": "string",                     // Dirección física
      "e-mail": "string",                        // Dirección de correo electrónico
      "fax": "string",                           // Número de fax
      "municipio": "string",                     // Municipio donde se ubica
      "nombre": "string",                        // Nombre del juzgado
      "provincia": "string",                     // Provincia a la que pertenece
      "telefono/s": "string",                    // Números de teléfono separados por coma
      "titulares": ["titular1", "tit2", ...],    // Listado con el nombre y apellidos de cada uno de los titulares del juzgado
      "url": "string"                            // URL con más información sobre el juzgado
    }
    // Otros juzgados...
  ]
}
```
   
[1]: <https://github.com/pedroj0s/Datos-Publicos-Ministerio-Justicia/blob/229f268c3dbad00e66c473e06c5078b666015d0d/data/registros-civiles-datos-capturados.json> "Datos de los Registros Civiles existentes."
[2]: <https://github.com/pedroj0s/Datos-Publicos-Ministerio-Justicia/blob/2587d15dd1e924f08c939644d3b9e7f79f31adc2/data/juzgados-cpgj-datos-capturados.json> "Datos de juzgados españoles obtenidos desde el CGPJ."
