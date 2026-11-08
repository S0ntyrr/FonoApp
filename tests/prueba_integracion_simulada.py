import sys,types,os
from pathlib import Path
os.environ['MONGODB_URI']='mongodb://127.0.0.1:27017'
os.environ['SESSION_HTTPS_ONLY']='false'
os.environ['SESSION_SECRET_KEY']='test-only-secret-key-no-production'
# SIMULACIÓN TEMPORAL para importar endpoints sin el driver Motor ni MongoDB
motor=types.ModuleType('motor'); asyncmod=types.ModuleType('motor.motor_asyncio')
class AsyncIOMotorDatabase: pass
class AsyncIOMotorClient:
 def __init__(self,*a,**kw): pass
 def __getitem__(self,k): return {}
 def close(self):pass
asyncmod.AsyncIOMotorClient=AsyncIOMotorClient;asyncmod.AsyncIOMotorDatabase=AsyncIOMotorDatabase
sys.modules['motor']=motor;sys.modules['motor.motor_asyncio']=asyncmod
bson=types.ModuleType('bson'); be=types.ModuleType('bson.errors')
class InvalidId(Exception):pass
class ObjectId(str):
 def __new__(cls,v='000000000000000000000001'):
  if len(str(v))!=24: raise InvalidId('24hex')
  return str.__new__(cls,str(v))
bson.ObjectId=ObjectId;be.InvalidId=InvalidId
sys.modules['bson']=bson;sys.modules['bson.errors']=be
bcrypt=types.ModuleType('bcrypt');bcrypt.gensalt=lambda: b'fake-salt'; bcrypt.hashpw=lambda value,salt:value; bcrypt.checkpw=lambda a,b:a==b;sys.modules['bcrypt']=bcrypt
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)
from app.main import app
from fastapi import Request
from starlette.testclient import TestClient
@app.get('/_test_login',include_in_schema=False)
def test_login(request:Request, rol:str='paciente', email:str=''):
 request.session['user']={'email':email or ('paciente@test.local' if rol=='paciente' else 'medico@test.local'),'rol':rol}
 return {'ok':True}
print('Registered routes:',len(app.routes))
client=TestClient(app)
assert client.get('/_test_login?rol=paciente').status_code==200
urls = ['/juegos/respiracion/globo','/juegos/respiracion/molino','/juegos/respiracion/burbujas','/juegos/respiracion/pitillos','/juegos/practica/praxias','/juegos/resonancia/imitacion','/juegos/articulacion/fonemas','/juegos/articulacion/abcd','/juegos/articulacion/pronunciacion-5','/juegos/articulacion/moto-voz','/juegos/articulacion/completa-palabra','/juegos/resonancia/escaleras','/juegos/resonancia/veoveo']
for url in urls:
 try:
  r=client.get(url)
  print(r.status_code,url,len(r.content))
  assert r.status_code==200,(url,r.text[:300]);assert b'<!DOCTYPE html>' in r.content
 except Exception as exc:
  print('FAILED',url,str(exc)[:260]);raise
for src in ['/static/img/molino-demostracion.gif','/static/img/soplo-boca.gif','/static/img/bocas/fonema-rr.gif','/static/js/fono-juegos-nuevos.js']:
 r=client.get(src);print('asset',src,r.status_code,len(r.content));assert r.status_code==200
print('Smoke test OK')
# Prueba simulada de flujo completo (sin base MongoDB real): carga de dos clips,
# vinculación a un intento y consulta del médico con control de permisos.
from app.database import get_db
from types import SimpleNamespace
from datetime import datetime
import re,asyncio

class Cursor:
 def __init__(self,data):self.data=list(data)
 def sort(self,k,v):
  self.data.sort(key=lambda x:x.get(k) or datetime.min,reverse=v<0);return self
 def skip(self,n):self.data=self.data[n:];return self
 def limit(self,n):self.data=self.data[:n];return self
 def __aiter__(self):self._it=iter(self.data);return self
 async def __anext__(self):
  try:return next(self._it)
  except StopIteration:raise StopAsyncIteration

class Coll:
 def __init__(self):self.records=[]
 def match(self,d,q):
  for key,needle in q.items():
   if key=='$or':
    if not any(self.match(d,e) for e in needle):return False
    continue
   v=d.get(key)
   if isinstance(needle,dict):
    if '$in' in needle and v not in needle['$in']:return False
    if '$exists' in needle and (key in d)!=needle['$exists']:return False
    if '$regex' in needle and not re.search(needle['$regex'],str(v),re.I if 'i' in needle.get('$options','') else 0):return False
    if '$gte' in needle and not(v>=needle['$gte']):return False
    if '$lt' in needle and not(v<needle['$lt']):return False
   elif v!=needle:return False
  return True
 async def find_one(self,q,*a,**kw):return next((d for d in self.records if self.match(d,q)),None)
 async def insert_one(self,d):
  if '_id' not in d:d['_id']=ObjectId(f'{len(self.records)+1:024x}')
  self.records.append(d);return SimpleNamespace(inserted_id=d['_id'])
 async def update_one(self,q,update,upsert=False):
  d=await self.find_one(q)
  if not d and upsert:
   d={k:v for k,v in q.items() if not isinstance(v,dict)};await self.insert_one(d)
  if d:
   for k,v in update.get('$set',{}).items():d[k]=v
   for k,v in update.get('$setOnInsert',{}).items():d.setdefault(k,v)
   for k,v in update.get('$inc',{}).items():d[k]=d.get(k,0)+v
  return SimpleNamespace(matched_count=int(bool(d)))
 async def update_many(self,q,update):
  for d in self.records:
   if self.match(d,q):d.update(update.get('$set',{}))
 def find(self,q=None,*a,**kw):return Cursor([d for d in self.records if self.match(d,q or {})])

class DB(dict):
 def __missing__(self,k):self[k]=Coll();return self[k]

db=DB();db['usuarios'].records.append({'email':'medico@test.local','rol':'medico'})
db['asignaciones'].records.append({'medico_email':'medico@test.local','paciente_email':'paciente@test.local','estado':'aceptada'})
app.dependency_overrides[get_db]=lambda:db
client.get('/_test_login?rol=medico')
r=client.get('/doctor/tareas');print('doctor tareas GET',r.status_code);assert r.status_code==200
r=client.post('/doctor/tareas',data={'paciente_email':'paciente@test.local','url_juego':'/juegos/articulacion/fonemas','nivel':'2','fonema':'R','instrucciones':'Practicar en familia'},follow_redirects=False)
print('doctor tarea POST',r.status_code);assert r.status_code==303
assert len(db['tareas_terapeuticas'].records)==1
tarea_id=str(db['tareas_terapeuticas'].records[0]['_id'])
client.get('/_test_login?rol=paciente')
urls=[]
for blob in (b'RIFFfakeone',b'RIFFfaketwo'):
 r=client.post('/juegos/evidencia-audio',files={'audio':('prueba.wav',blob,'audio/wav')},data={'categoria':'articulacion','juego':'fonemas'})
 print('subir audio',r.status_code);assert r.status_code==200,r.text
 urls.append(r.json()['audio_url'])
import json
r=client.post('/juegos/resultado',data={
 'categoria':'articulacion','juego':'fonemas','paso_completado':5,'total_pasos':5,
 'completado':'true','puntos':70,'nivel':2,'ruta':'/juegos/articulacion/fonemas',
 'tarea_id':tarea_id,'audio_url':urls[0],'audios_extra_json':json.dumps([urls[1]])
})
print('resultado+2audios',r.status_code,r.text[:250]);assert r.status_code==200,r.text
assert len(db['intentos_juegos'].records)==1
assert db['intentos_juegos'].records[0]['audio_urls']==urls
assert db['tareas_terapeuticas'].records[0]['estado']=='completada'
assert client.get(urls[0]).status_code==200
client.get('/_test_login?rol=medico')
assert client.get(urls[0]).status_code==200
r=client.get('/doctor/grabaciones')
print('doctor grabaciones',r.status_code,'players',r.text.count('<audio '));assert r.status_code==200
assert r.text.count('<audio ')>=2
client.get('/_test_login?rol=paciente')
r=client.post('/juegos/resultado',data={
 'categoria':'articulacion','juego':'fonemas','paso_completado':5,'total_pasos':5,
 'completado':'true','audio_url':urls[0]
})
print('no reutilizar audio',r.status_code);assert r.status_code==400
# Un segundo intento del mismo juego nunca debe borrar el primero.
r=client.post('/juegos/evidencia-audio',files={'audio':('nuevo.wav',b'RIFFsecondattempt','audio/wav')},data={'categoria':'articulacion','juego':'fonemas'})
assert r.status_code==200
tercer_audio=r.json()['audio_url']
r=client.post('/juegos/resultado',data={
 'categoria':'articulacion','juego':'fonemas','paso_completado':3,'total_pasos':5,
 'completado':'false','audio_url':tercer_audio,
})
assert r.status_code==200
assert len(db['intentos_juegos'].records)==2
assert db['intentos_juegos'].records[0]['audio_urls']==urls
assert db['intentos_juegos'].records[1]['audio_urls']==[tercer_audio]
# Un tercero no debe poder escuchar audios ajenos.
client.get('/_test_login?rol=paciente&email=intruso@test.local')
assert client.get(urls[0]).status_code==403
# Un doctor sin relación activa no debe escuchar los clips.
client.get('/_test_login?rol=medico&email=otro_doctor@test.local')
assert client.get(urls[0]).status_code==403
# Doctor asignado puede acceder a todos los intentos, también páginas históricas.
client.get('/_test_login?rol=medico')
r=client.get('/doctor/grabaciones')
assert r.status_code==200 and r.text.count('<audio ')>=3
assert client.get('/doctor/grabaciones?pagina=2').status_code==200
print('Persistencia multi-intento, paginación y control de acceso OK')
print('Flow end-to-end with mocked DB OK')
