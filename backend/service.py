"""Reglas FastExpress. Decimal evita errores binarios en importes."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

class ValidationError(ValueError):
    pass

def validate_payload(data):
    """Valida antes de invocar el algoritmo core. Peso en pasos de 0.01 kg."""
    if not isinstance(data, dict):
        raise ValidationError("El cuerpo debe ser un objeto JSON.")
    if set(data) != {"peso", "cliente", "envio"}:
        raise ValidationError("Se requieren exactamente peso, cliente y envio.")
    raw = data["peso"]
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float, Decimal)):
        raise ValidationError("El peso debe ser un número decimal.")
    try:
        peso = Decimal(str(raw))
    except InvalidOperation:
        raise ValidationError("El peso debe ser un número decimal.") from None
    if not peso.is_finite():
        raise ValidationError("El peso debe ser finito.")
    if peso < Decimal("0.01"):
        raise ValidationError("El peso mínimo es 0.01 kg.")
    if peso > Decimal("20.00"):
        raise ValidationError("Límite excedido: máximo 20.00 kg.")
    if peso != peso.quantize(Decimal("0.01")):
        raise ValidationError("El peso debe expresarse en pasos de 0.01 kg.")
    if data["cliente"] not in ("NUEVO", "FRECUENTE", "VIP"):
        raise ValidationError("Cliente inválido: use NUEVO, FRECUENTE o VIP.")
    if data["envio"] not in ("ESTANDAR", "EXPRESS"):
        raise ValidationError("Envío inválido: use ESTANDAR o EXPRESS.")
    return peso, data["cliente"], data["envio"]

def calculate_tariff(peso, cliente, envio):
    """Core con cuatro decisiones. Precondición: validate_payload aceptó los datos.

    La tarifa por kg se aplica a TODO el peso, no de forma progresiva.
    Descuento y recargo se calculan ambos sobre subtotal = base + peso.
    Se redondea al final a centavos, con ROUND_HALF_UP.
    """
    if peso <= Decimal("5.00"):                 # D1
        rate = Decimal("2.00")
    else:
        rate = Decimal("4.00")
    subtotal = Decimal("5.00") + peso * rate
    discount_rate = Decimal("0")
    if cliente == "FRECUENTE":                  # D2
        discount_rate = Decimal("0.10")
    elif cliente == "VIP":                      # D3
        discount_rate = Decimal("0.20")
    discount = subtotal * discount_rate
    surcharge = Decimal("0")
    if envio == "EXPRESS":                      # D4
        surcharge = subtotal * Decimal("0.25")
    total = (subtotal - discount + surcharge).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {"moneda": "USD", "peso": str(peso), "cliente": cliente,
            "envio": envio, "base": "5.00", "tarifa_kg": str(rate),
            "subtotal": str(subtotal), "descuento": str(discount),
            "recargo": str(surcharge), "total": str(total)}

def quote(data):
    return calculate_tariff(*validate_payload(data))
