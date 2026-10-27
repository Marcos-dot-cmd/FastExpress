import sys,threading,json,urllib.request,os
from pathlib import Path
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
from backend.app import create_app
server=make_server('127.0.0.1',0,create_app(),threaded=True)
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
results=[];version=''
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('FASTEXPRESS_CHROMIUM'),headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--disable-gpu','--no-zygote'])
  page=browser.new_page(viewport={'width':1366,'height':1000},locale='es-CO')
  page.goto(base)
  combinations=[('NUEVO','ESTANDAR','15.00'),('NUEVO','EXPRESS','18.75'),('FRECUENTE','ESTANDAR','13.50'),('FRECUENTE','EXPRESS','17.25'),('VIP','ESTANDAR','12.00'),('VIP','EXPRESS','15.75')]
  for c,e,total in combinations:
   page.locator('#peso').fill('5.00');page.locator('#cliente').select_option(c);page.locator('#envio').select_option(e)
   page.locator('#submit').click()
   expect(page.locator('#breakdown')).to_be_visible()
   expect(page.locator('#total')).to_contain_text(total.replace('.',','))
   results.append({'caso':f'UI-{c}-{e}','esperado':total,'obtenido':page.locator('#total').inner_text(),'estado':'APROBADO'})
  page.screenshot(path=str(root/'evidencias/interfaz_escritorio.png'),full_page=True,animations='disabled')
  # Límites HTML y bloqueo del formulario.
  for value in ['0','20.01','5.001','']:
   page.locator('#peso').fill(value)
   assert not page.locator('#peso').evaluate('(el)=>el.checkValidity()')
   results.append({'caso':'UI-PESO-'+repr(value),'estado':'APROBADO','esperado':'checkValidity falso'})
  page.locator('#peso').fill('20.01');page.locator('#submit').click()
  page.screenshot(path=str(root/'evidencias/validacion_peso.png'),full_page=True,animations='disabled')
  # Nueva cotización mediante teclado.
  page.locator('#peso').fill('5.01');page.locator('#cliente').select_option('NUEVO');page.locator('#envio').select_option('ESTANDAR')
  page.locator('#peso').focus();page.keyboard.press('Tab');assert page.locator('#cliente').evaluate('(el)=>el===document.activeElement')
  page.keyboard.press('Tab');assert page.locator('#envio').evaluate('(el)=>el===document.activeElement')
  page.keyboard.press('Tab');assert page.locator('#submit').evaluate('(el)=>el===document.activeElement')
  page.keyboard.press('Enter');expect(page.locator('#total')).to_contain_text('25,04')
  results.append({'caso':'UI-TECLADO','estado':'APROBADO'})
  page.set_viewport_size({'width':390,'height':844})
  assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
  page.screenshot(path=str(root/'evidencias/interfaz_movil.png'),full_page=True,animations='disabled')
  results.append({'caso':'UI-MOVIL-390','estado':'APROBADO'})
  page.route('**/api/cotizaciones',lambda route:route.abort())
  page.locator('#submit').click();expect(page.locator('#error')).to_contain_text('No hay conexión')
  expect(page.locator('#submit')).to_be_enabled();expect(page.locator('#breakdown')).to_be_hidden()
  page.screenshot(path=str(root/'evidencias/error_conexion.png'),full_page=True,animations='disabled')
  results.append({'caso':'UI-RED','estado':'APROBADO'})
  page.unroute('**/api/cotizaciones')
  # Captura real del reporte HTML generado por Coverage.py.
  page.set_viewport_size({'width':1280,'height':800})
  page.goto((root/'evidencias/htmlcov/index.html').as_uri())
  expect(page.locator('h1')).to_contain_text('100%')
  page.screenshot(path=str(root/'evidencias/captura_cobertura.png'),clip={'x':0,'y':0,'width':1280,'height':350})
  results.append({'caso':'CAPTURA-HTML-COVERAGE','estado':'APROBADO'})
  version=browser.version;browser.close()
 # Petición HTTP real, distinta del cliente de Flask.
 http=[]
 for c,e,total in combinations:
  req=urllib.request.Request(base+'/api/cotizaciones',data=json.dumps({'peso':'5.00','cliente':c,'envio':e}).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as response:
   result=json.load(response);assert result['total']==total
   http.append({'cliente':c,'envio':e,'esperado':total,'obtenido':result['total'],'http':response.status,'estado':'APROBADO'})
 (root/'evidencias/prueba_http_real.json').write_text(json.dumps(http,indent=2,ensure_ascii=False),encoding='utf-8')
 (root/'evidencias/pruebas_navegador.json').write_text(json.dumps({'navegador':f'Chromium {version} headless','casos':results},indent=2,ensure_ascii=False),encoding='utf-8')
 print(json.dumps(results,ensure_ascii=False,indent=2))
finally:
 server.shutdown()
