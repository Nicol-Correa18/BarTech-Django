function toggleMenu() {
    const menu = document.querySelector('.menu');
    const overlay = document.getElementById('overlay');
    
    if (menu.style.display === 'block') {
        menu.style.display = 'none';
        overlay.style.display = 'none';
    } else {
        menu.style.display = 'block';
        overlay.style.display = 'block';
    }
}

document.getElementById('overlay').addEventListener('click', function () {
    document.querySelector('.menu').style.display = 'none';
    this.style.display = 'none'; 
});

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modal");
    const modalText = document.getElementById("modal-text");
    const closeModal = document.querySelector(".close");
    const overlay = document.getElementById("overlay");

    document.getElementById("open-terms").addEventListener("click", function () {
        modalText.innerHTML = `<h3>TÉRMINOS Y CONDICIONES</h3>
            <p><p>El presente documento establece los términos y condiciones de uso del software de gestión de inventarios desarrollado para licorerías. Al utilizar el software, el usuario acepta cumplir con estas condiciones. Si no está de acuerdo, debe abstenerse de usar el sistema. El software está diseñado para la gestión y control del inventario de productos en una licorería y solo los usuarios autorizados pueden acceder y utilizar el sistema. El usuario es responsable de la exactitud de los datos ingresados en el software y no está permitido el uso del software para fines ilegales o no autorizados. Se concede una licencia no exclusiva, intransferible y revocable para el uso del software, quedando prohibida la copia, distribución o modificación del software sin autorización expresa del desarrollador. El uso indebido del software puede derivar en la cancelación de la licencia.</p>

        <p>El usuario debe mantener la confidencialidad de las credenciales de acceso, no compartir el acceso con terceros no autorizados e informar sobre cualquier problema de seguridad detectado en el software. El desarrollador no se hace responsable por daños derivados del mal uso del software y no garantiza la disponibilidad ininterrumpida del sistema, aunque se hará todo lo posible por mantenerlo operativo. El usuario acepta que los datos almacenados en el software son de su exclusiva responsabilidad.</p>

        <p>El desarrollador se reserva el derecho de modificar estos términos en cualquier momento y cualquier cambio será notificado a los usuarios con antelación. El incumplimiento de estos términos puede resultar en la suspensión o cancelación del acceso al software. Para cualquier consulta sobre estos términos y condiciones, puede contactar al soporte técnico a través de los medios habilitados en el software.</p></p>`;
        modal.style.display = "block";
        overlay.style.display = "block";
    });

    document.getElementById("open-privacy").addEventListener("click", function () {
        modalText.innerHTML = `<h3>POLÍTICAS DE PRIVACIDAD</h3>
            <p><p>El presente documento establece la política de privacidad del software de gestión de inventarios para licorerías. El uso del software implica la aceptación de esta política y el consentimiento del usuario para el tratamiento de sus datos personales.</p>

        <p>El software recopila información como nombre de usuario, credenciales de acceso, registros de actividad y datos relacionados con la gestión de inventarios. Esta información se utiliza exclusivamente para la operatividad del sistema, garantizar la seguridad de los datos y mejorar la experiencia del usuario.</p>

        <p>El desarrollador se compromete a proteger la privacidad de los usuarios y no compartirá ni comercializará los datos personales con terceros sin autorización expresa, salvo en cumplimiento de obligaciones legales. El acceso a la información se encuentra restringido y solo es accesible por personal autorizado.</p>

        <p>El usuario puede solicitar la actualización, rectificación o eliminación de sus datos personales enviando una solicitud al soporte técnico. La eliminación de datos puede implicar la pérdida del acceso al software y sus funcionalidades.</p>

        <p>El desarrollador se reserva el derecho de modificar esta política de privacidad en cualquier momento, notificando a los usuarios sobre cambios relevantes. Para más información, los usuarios pueden contactar al soporte técnico a través de los medios habilitados en el software.</p></p>`;
        modal.style.display = "block";
        overlay.style.display = "block";
    });

    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
        overlay.style.display = "none";
    });

    overlay.addEventListener("click", function () {
        modal.style.display = "none";
        overlay.style.display = "none";
    });
});