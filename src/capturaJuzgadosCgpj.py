import concurrent.futures;
import urllib.request;
from queue import Queue
import json;
from bs4 import BeautifulSoup;
import requests;
import os;
import itertools;

os.chdir('.\\data');
translation = str.maketrans('áéíóú ', 'aeiou-');

DATA_FILENAME =  'juzgados-cpgj-datos-capturados.json';
ERROR_FILENAME = 'juzgados-cpgj-errores-captura.json';
MAX_THREADS = 50;
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
          juzgado[td.get('data-cabecera').lower().translate(translation)] = td.text;
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

def courtsDetailsExtractor(data):
  def extractCourtsDetails(content, url=None) -> dict:
    result = { 
      'nombre': '',
      'url': '',
      'titulares': []
    };
    soup = BeautifulSoup(content, 'html.parser');
    result['nombre'] = soup.find('h2', class_='titu7').text if soup.find('h2', class_='titu7') else 'Nombre no encontrado en el contenido';
    result['url'] = url if url else 'URL no especificada';
    dlMapa = soup.find('div', {'id': 'txtMapa'});
    dlMapa = dlMapa.find('dl') if dlMapa else None;
    if dlMapa:      
      dts = [dt.text.strip().lower().translate(translation).replace(':','') for dt in dlMapa.find_all('dt')];
      dds = [dt.text.strip() for dt in dlMapa.find_all('dd')];
      for idx, key in enumerate(dts):
        result[key] = dds[idx];
    titulares = soup.find('div', {'id':'listaTit'});
    titulares = soup.find('tbody') if titulares else None;
    if titulares:
      titulares = [titular.text.strip() for titular in titulares.find_all('td', class_=None)];
      result['titulares'] = titulares;
    return result;

  def getCourtContent(url) -> str:
    with urllib.request.urlopen(url, timeout=5000) as conn:
      result = conn.read();
      return result;

  def getCourtsDetails(data):  
    juzgados = list(itertools.chain.from_iterable([j for j in [provincia['juzgados'] for provincia in data['provincias']]]));
    urls = [j['url'] for j in juzgados if 'url' in j];    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
      future_to_url = {executor.submit(getCourtContent, url): url for url in urls};
      totales = len(urls);
      actuales = 0;
      for future in concurrent.futures.as_completed(future_to_url.keys()):
        url = future_to_url[future];
        try:
          content = future.result();
        except Exception as exc:
          actuales+=1;
          error = { 'url': url, 'excepcion': exc, 'tipo': 'requesting content' };
          print(f'{url} generó una excepción: {exc} [{100*actuales/totales:.2f}% procesado]');
          datos['errores'].append(error);
        else:
          actuales+=1;
          ok = { 'url': url, 'bytes': len(content) };
          print(f'{url} contiene {len(content)} bytes [{100*actuales/totales:.2f}% procesado]');
          datos['ok'].append(ok);
          queueData = { 'url': url, 'data': content };
          queue.put(queueData);
    queue.put(None);
    return;

  def processCourtsData():
    procesados = 0;
    while True:
      content = queue.get();      
      if content is None:
        break;
      try:
        datosExtraidos = extractCourtsDetails(content['data'], content['url']);
        datos['juzgados'].append(datosExtraidos);
        procesados += 1;
        print(f'[{procesados}] juzgados con sus datos extraidos');
      except Exception as exc:        
        procesados += 1;
        error = { 'url': content['url'], 'exception': exc, 'tipo': 'processing content' };
        print(error);
        datos.errores.push(error);
  
  queue = Queue();
  datos = { 'errores': [], 'ok': [], 'juzgados': []};
  #extractCourtsDetails(getCourtContent(data['provincias'][0]['juzgados'][0]['url']));
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(getCourtsDetails, data);
    executor.submit(processCourtsData);
  print(datos);
  return datos;

data=getData();
juzgados = courtsDetailsExtractor(data);
data['detalleJuzgados'] = juzgados['juzgados'];
with open(DATA_FILENAME, 'w') as f:
  json.dump(data, f, indent=1);
#getData();

  