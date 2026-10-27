import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app=create_app()
    app.config["TESTING"]=True
    return app.test_client()

def test_health(client):
    assert client.get("/api/health").json["status"] == "ok"

def test_index(client):
    response=client.get("/")
    assert response.status_code==200
    assert b"FastExpress" in response.data

@pytest.mark.parametrize("asset",["app.js","styles.css"])
def test_assets(client,asset):
    assert client.get("/assets/"+asset).status_code == 200

def test_success(client):
    result=client.post("/api/cotizaciones",json=dict(peso="5",cliente="VIP",envio="EXPRESS"))
    assert result.status_code==200
    assert result.json["total"]=="15.75"
    assert result.json["subtotal"]=="15.00"

def test_invalid_weight(client):
    result=client.post("/api/cotizaciones",json=dict(peso="20.01",cliente="NUEVO",envio="ESTANDAR"))
    assert result.status_code==400
    assert "Límite excedido" in result.json["error"]

@pytest.mark.parametrize("body,content_type",[("{","application/json"),("peso=1","text/plain"),("{}",None)])
def test_malformed(client,body,content_type):
    assert client.post("/api/cotizaciones",data=body,content_type=content_type).status_code==400

def test_null(client):
    response=client.post("/api/cotizaciones",data="null",content_type="application/json")
    assert response.status_code==400

def test_size(client):
    assert client.post("/api/cotizaciones",data="x"*17000,content_type="application/json").status_code==413

def test_missing_route(client):
    assert client.get("/no-existe").status_code==404

def test_traversal(client):
    assert client.get("/assets/../backend/service.py").status_code==404

def test_wrong_method(client):
    assert client.get("/api/cotizaciones").status_code==405
