# Fase 4 – Software FJ

**Curso:** Programación – 213023  
**Programa:** Ingeniería de Sistemas – UNAD

## Descripción
Aplicación de consola para gestionar clientes, servicios y reservas de Software FJ. Está desarrollada en Python mediante programación orientada a objetos. No utiliza bases de datos: administra la información en listas y objetos durante la ejecución y registra eventos/errores en `software_fj.log`.

## Requisitos
- Python 3.9 o superior.
- No necesita instalar paquetes externos.

## Ejecución
Desde la terminal, dentro de esta carpeta:

```bash
python main.py
```

## Estructura y conceptos aplicados
- `Entidad`: clase abstracta general.
- `Cliente`: encapsulación y validación de datos.
- `Servicio`: clase abstracta.
- `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`: herencia y polimorfismo.
- `Reserva`: creación, confirmación, cancelación y procesamiento.
- `SistemaSoftwareFJ`: administración de listas internas.
- Excepciones personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento de excepciones.
- `software_fj.log`: archivo generado automáticamente para eventos y errores.

## Pruebas incluidas
El programa simula 12 operaciones, entre ellas registros válidos e inválidos, creación de servicios, reservas correctas e incorrectas, servicios no disponibles y errores de cálculo. La ejecución debe continuar después de los errores controlados.

## Publicación en GitHub
1. Ingrese a su cuenta de GitHub.
2. Cree un repositorio para el grupo o solicite acceso al repositorio acordado por el equipo.
3. Cargue `main.py`, `README.md` y el informe PDF.
4. Verifique que los archivos aparezcan en la rama principal.
5. Copie el enlace real del repositorio y agréguelo al informe antes de entregar.

**Importante:** el repositorio publicado en el foro por Jorge Esteban Herrera Bermúdez es `https://github.com/jherrerabermudez14-debug/fase4-software-fj`. La página pública permite ver que existe y que contiene una carpeta `software_fj_reservas` y un README básico; no se pudo verificar el contenido de la carpeta ni confirmar que el estudiante que entrega este trabajo tenga autorización para usarlo. Por eso, el informe deja el enlace de entrega como campo para completar y no atribuye ese repositorio al usuario.
