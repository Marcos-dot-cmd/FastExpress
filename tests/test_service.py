from decimal import Decimal
import pytest
from backend.service import quote, calculate_tariff, ValidationError

# Particiones y BVA. Oráculos fijados manualmente desde la especificación.
@pytest.mark.parametrize("peso,total", [
    ("0.01","5.02"),("0.02","5.04"),("2.50","10.00"),
    ("4.99","14.98"),("5.00","15.00"),("5.01","25.04"),
    ("5.02","25.08"),("10.00","45.00"),("19.99","84.96"),
    ("20.00","85.00")])
def test_weight_boundaries(peso,total):
    assert quote(dict(peso=peso,cliente="NUEVO",envio="ESTANDAR"))["total"] == total

@pytest.mark.parametrize("cliente,envio,total", [
    ("NUEVO","ESTANDAR","15.00"),("NUEVO","EXPRESS","18.75"),
    ("FRECUENTE","ESTANDAR","13.50"),("FRECUENTE","EXPRESS","17.25"),
    ("VIP","ESTANDAR","12.00"),("VIP","EXPRESS","15.75")])
def test_decision_table(cliente,envio,total):
    assert quote(dict(peso="5.00",cliente=cliente,envio=envio))["total"] == total

@pytest.mark.parametrize("peso,cliente,envio,total", [
    ("5.00","NUEVO","ESTANDAR","15.00"),     # P1
    ("5.01","NUEVO","ESTANDAR","25.04"),    # P2
    ("5.00","FRECUENTE","ESTANDAR","13.50"), # P3
    ("5.00","VIP","ESTANDAR","12.00"),       # P4
    ("5.00","NUEVO","EXPRESS","18.75")])     # P5
def test_independent_paths(peso,cliente,envio,total):
    assert calculate_tariff(Decimal(peso),cliente,envio)["total"] == total

@pytest.mark.parametrize("peso", ["-1","0","0.001","20.01","21", "5.001",
    "abc","",None,True,False,[],{},"NaN","Infinity","-Infinity"])
def test_invalid_weights(peso):
    with pytest.raises(ValidationError):
        quote(dict(peso=peso,cliente="NUEVO",envio="ESTANDAR"))

@pytest.mark.parametrize("data", [None,[],"x",{},
    {"peso":"1","cliente":"NUEVO"},
    {"peso":"1","cliente":"NUEVO","envio":"ESTANDAR","monto":10}])
def test_invalid_payload(data):
    with pytest.raises(ValidationError):
        quote(data)

@pytest.mark.parametrize("cliente",["",None,[],{},1,"vip","OTRO"])
def test_invalid_client(cliente):
    with pytest.raises(ValidationError):
        quote(dict(peso="1",cliente=cliente,envio="ESTANDAR"))

@pytest.mark.parametrize("envio",["",None,[],{},1,"express","OTRO"])
def test_invalid_shipping(envio):
    with pytest.raises(ValidationError):
        quote(dict(peso="1",cliente="NUEVO",envio=envio))

@pytest.mark.parametrize("peso",[1,1.0,Decimal("1.00"),"1.000"])
def test_numeric_inputs(peso):
    assert quote(dict(peso=peso,cliente="NUEVO",envio="ESTANDAR"))["total"] == "7.00"

@pytest.mark.parametrize("peso,cliente,envio,total",[
    ("0.01","VIP","ESTANDAR","4.02"),
    ("0.01","VIP","EXPRESS","5.27"),
    ("0.01","FRECUENTE","EXPRESS","5.77"),
    ("20","NUEVO","EXPRESS","106.25"),
    ("5.01","VIP","EXPRESS","26.29"),
    ("5.01","FRECUENTE","EXPRESS","28.80"),
    ("0.01","NUEVO","EXPRESS","6.28")])
def test_amount_and_rounding(peso,cliente,envio,total):
    result=quote(dict(peso=peso,cliente=cliente,envio=envio))
    assert result["total"] == total
    assert result["moneda"] == "USD"
