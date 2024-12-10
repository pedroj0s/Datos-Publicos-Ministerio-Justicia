import concurrent.futures;
import json;
from bs4 import BeautifulSoup;
import requests;

DATA_FILENAME =  'juzgados-cpgj-datos-capturados.json';
ERROR_FILENAME = 'juzgados-cpgj-errores-captura.json';
ROOT_URL = 'https://www.poderjudicial.es';
PROVINCIAS_URL = f'{ROOT_URL}/cgpj/es/Servicios/Directorio/Directorio-de-Organos-Judiciales/';
BASE_URL = "https://www.poderjudicial.es/cgpj/es/Servicios/Directorio/Directorio-de-Organos-Judiciales/";


def getData() -> dict:
  data = {
    'provincias': []
  };
  errores = {};

  def getProvincias():
    page = requests.get(BASE_URL);
    soup = BeautifulSoup(page.content, 'html.parser');
    marco =  soup.find('div', class_="divListado");#  {tag.name for tag in soup.find_all("li", class_ = "divListado")};
    for a in marco.find_all('a'):
      data['provincias'].append({
        'nombre': a.text,
        'url': f'{ROOT_URL}{a['href']}',
        'paginasJuzgados': [f'{ROOT_URL}{a['href']}'],
        'juzgados': []
      });
    return;

  def getPaginasProvincia(provincia):
    page = requests.get(provincia['url']);
    soup = BeautifulSoup(page.content, 'html.parser');
    siguientePagina = soup.find('a', {'rel': 'next'});
    while siguientePagina:
      provincia['paginasJuzgados'].append(f'{ROOT_URL}{siguientePagina['href']}');
      getJuzgados(provincia, None, page.content);
      page = requests.get(f'{ROOT_URL}{siguientePagina['href']}');
      soup = BeautifulSoup(page.content, 'html.parser');
      siguientePagina = soup.find('a', {'rel': 'next'});
  
  def getJuzgados(provincia, url, content=None) -> dict:
    if not content:
      page = requests.get(url);
      soup = BeautifulSoup(page.content, 'html.parser');
    else:
      soup = BeautifulSoup(content, 'html.parser');
    marco = soup.find('table', class_='tablaDatos tablaDatos1');    
    for tr in marco.find('tbody').find_all('tr'):
      juzgado = {};
      for td in tr.find_all(['td', 'th'], { 'data-cabecera': True }):
        link = td.find('a');
        if link:
          juzgado['nombre'] = link.text;
          juzgado['url'] = f'{ROOT_URL}{link['href']}';
        else:
          juzgado[td.get('data-cabecera')] = td.text;
      provincia['juzgados'].append(juzgado);
    return;
  

  getProvincias();
  for provincia in data['provincias']:    
    print(f'Capturando páginas de {provincia['nombre']}');
    getPaginasProvincia(provincia);
    print(f'Paginas de {provincia['nombre']} completadas => [{len(provincia['paginasJuzgados'])}] páginas');
    continue;
    for idx, urlPaginaJuzgado in enumerate(provincia['paginasJuzgados']):
      print(f'Capturando página {idx+1} de {provincia['nombre']}  [{len(provincia['juzgados'])}] juzgados capturados');
      getJuzgados(provincia, urlPaginaJuzgado);
  with open(DATA_FILENAME, 'w') as f:
    json.dump(data, f);
  if(errores):
    with open(ERROR_FILENAME, 'w') as f:
      json.dump(errores,f);
  return data;


getData();

  