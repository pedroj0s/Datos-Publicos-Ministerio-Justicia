import json;
import os.path;
from selenium import webdriver;
from selenium.webdriver.common.by import By;
from selenium.webdriver.common.keys import Keys;

browser = webdriver.Firefox();
#browser.get('http://yahoo.com');
#assert 'Yahoo' in browser.title;

#elem = browser.find_element(By.NAME, 'agree');
#elem.click();
#elem = browser.find_element(By.NAME, 'p');
#elem.send_keys('seleniumhq', Keys.RETURN);

#browser.implicitly_wait(100);
#browser.quit();
DATA_FILENAME = 'registros-civiles-datos-capturados.json';
ERROR_FILENAME = 'registros-civiles-errores-captura.json';

def extractDatosRegistro() -> dict:
  data = {};
  errores = {};

  def getListadoProvincias(items):
    browser.get('https://www.mjusticia.gob.es/BUSCADIR/ServletControlador?apartado=buscadorGeneral&tipo=RC&lang=es_es');
    marco = browser.find_element(By.CLASS_NAME, 'listado_provincias_munis')
    enlaces = marco.find_elements(By.TAG_NAME, 'a');  
    items['provincias'] = [];
    for link in enlaces:
      items['provincias'].append({ 
        'nombre': link.text, 
        'url': link.get_attribute('href'),
        'registros' : []
      });

  def getListadoRegistros(provincia):
    print(f'Leyendo {provincia['nombre']} - {provincia['url']}');
    browser.get(provincia['url']);
    if not len(browser.find_elements(By.CLASS_NAME, 'listado_02'))>0:
      provincia['registros'].append({ 
        'nombre': provincia['nombre'],
        'url': provincia['url'],
        'info': {}
      });
      return;
    marco = browser.find_element(By.CLASS_NAME, 'listado_02');
    enlaces = marco.find_elements(By.TAG_NAME, 'a');
    for link in enlaces:
      provincia['registros'].append({ 
        'nombre': link.text,
        'url': link.get_attribute('href'),
        'info': {}
      });

  def getDatosRegistro(registro):
    print(f'Leyendo {registro['nombre']} - {registro['url']}');
    browser.get(registro['url']);
    if not len(browser.find_elements(By.CLASS_NAME, 'cuerpo'))>0:
      return;
    marco = browser.find_element(By.CLASS_NAME, 'cuerpo');
    info = registro['info'];
    if len(marco.find_elements(By.CLASS_NAME, 'tituloInterior_05')) > 0:
      info['lugar'] = marco.find_element(By.CLASS_NAME, 'tituloInterior_05').find_element(By.TAG_NAME, 'h3').text;
      info['nombre'] = marco.find_elements(By.CLASS_NAME, 'tituloInterior_05')[1].find_element(By.TAG_NAME, 'h3').text if len(marco.find_elements(By.CLASS_NAME, 'tituloInterior_05'))>1 else '';
    otraData = marco.find_elements(By.XPATH, '//*[@class="listado_05"]/li');
    for od in otraData:
      strongData = od.find_element(By.TAG_NAME, 'strong').text;
      info[strongData] = od.text.replace(strongData, '');
    if len(marco.find_elements(By.XPATH, '//*[@class="cuerpo"]/ul/ul/li'))>0:
      otraData = marco.find_element(By.XPATH, '//*[@class="cuerpo"]/ul/ul/li') ;
      strongData = otraData.find_element(By.TAG_NAME, 'strong').text;
      info[strongData] = otraData.text.replace(strongData, '');
    

  getListadoProvincias(data);
  for provincia in data['provincias']:
    getListadoRegistros(provincia);  
    print(provincia);

  for provincia in data['provincias']:
    for registro in provincia['registros']:
      try:
        getDatosRegistro(registro);
        print(registro);
      except Exception as e:
        print(f'Error {repr(e)}');
        errores[f'{registro['nombre']} - {registro['url']}'] = repr(e);

  with open(DATA_FILENAME, 'w') as f:
    json.dump(data, f);
  if(len(errores.keys)>0):
    with open(ERROR_FILENAME, 'w') as f:
      json.dump(errores,f);
  return data;

def getData() -> dict:
  if os.path.exists(DATA_FILENAME):
    with open(DATA_FILENAME, 'r') as jsonfile:      
      return json.load(jsonfile);
  return extractDatosRegistro();

print(getData());