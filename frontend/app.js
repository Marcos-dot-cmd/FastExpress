const form = document.querySelector('#quote-form');
const errorBox = document.querySelector('#error');
const button = document.querySelector('#submit');
const buttonLabel = button.querySelector('.label');
const money = value => new Intl.NumberFormat('es-CO', {style:'currency',currency:'USD',currencyDisplay:'code'}).format(Number(value));
form.addEventListener('submit', async event => {
  event.preventDefault();
  errorBox.hidden = true;
  document.querySelector('#breakdown').hidden = true;
  document.querySelector('#empty').hidden = false;
  document.querySelector('#result-title').textContent = 'Tu cotización aparecerá aquí';
  if (!form.reportValidity()) return;
  button.disabled = true;
  button.setAttribute('aria-busy', 'true');
  buttonLabel.textContent = 'Calculando…';
  try {
    let response;
    try {
      response = await fetch('/api/cotizaciones', {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({peso:form.peso.value,cliente:form.cliente.value,envio:form.envio.value})
      });
    } catch {
      // Cada navegador usa un mensaje distinto para los fallos de red.
      throw new Error('No hay conexión con el servidor. Vuelve a intentarlo.');
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'No se pudo cotizar.');
    ['base','subtotal','descuento','recargo','total'].forEach(key => {
      document.getElementById(key).textContent = money(data[key]);
    });
    document.querySelector('#weight-cost').textContent = money(Number(data.subtotal)-Number(data.base));
    document.querySelector('#result-title').textContent = 'Tu envío está cotizado';
    document.querySelector('#empty').hidden = true;
    document.querySelector('#breakdown').hidden = false;
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.hidden = false;
  } finally {
    button.disabled = false;
    button.removeAttribute('aria-busy');
    buttonLabel.textContent = 'Calcular cotización';
  }
});
