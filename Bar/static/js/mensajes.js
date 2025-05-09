// Espera 3 segundos (3000 ms) y luego oculta el contenedor de mensajes
setTimeout(function() {
    const messages = document.getElementById('messages');
    if (messages) {
        messages.style.display = 'none';
    }
}, 3000);
