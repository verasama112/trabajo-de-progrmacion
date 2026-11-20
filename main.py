"""
Proyecto Fase 4 - Programación (213023)
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Software FJ

Ejecución: python main.py
No utiliza bases de datos. La información se administra en objetos y listas.
Los eventos y errores se registran en software_fj.log.
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging
import re
from typing import List, Optional


# ---------- Registro de eventos y errores ----------
logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)
logger = logging.getLogger("SoftwareFJ")


# ---------- Excepciones personalizadas ----------
class SoftwareFJError(Exception):
    """Excepción base del sistema."""


class ValidacionError(SoftwareFJError):
    """Datos ingresados que no cumplen las reglas."""


class ServicioNoDisponibleError(SoftwareFJError):
    """El servicio solicitado no está disponible."""


class ReservaError(SoftwareFJError):
    """Operación inválida relacionada con una reserva."""


# ---------- Entidad abstracta ----------
class Entidad(ABC):
    def __init__(self, identificador: str):
        if not identificador or not identificador.strip():
            raise ValidacionError("El identificador no puede estar vacío.")
        self._identificador = identificador.strip()

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def describir(self) -> str:
        pass


# ---------- Cliente ----------
class Cliente(Entidad):
    def __init__(self, identificador: str, nombre: str, correo: str, telefono: str):
        super().__init__(identificador)
        if not nombre or len(nombre.strip()) < 3:
            raise ValidacionError("El nombre debe contener al menos 3 caracteres.")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo or ""):
            raise ValidacionError("El correo electrónico no tiene un formato válido.")
        if not re.fullmatch(r"[0-9+\-\s]{7,15}", telefono or ""):
            raise ValidacionError("El teléfono debe contener entre 7 y 15 caracteres numéricos.")
        self._nombre = nombre.strip()
        self._correo = correo.strip().lower()
        self._telefono = telefono.strip()

    @property
    def nombre(self):
        return self._nombre

    @property
    def correo(self):
        return self._correo

    def describir(self):
        return f"Cliente {self._identificador}: {self._nombre} ({self._correo})"


# ---------- Servicio abstracto y servicios especializados ----------
class Servicio(Entidad, ABC):
    def __init__(self, identificador: str, nombre: str, tarifa_base: float):
        super().__init__(identificador)
        if not nombre or not nombre.strip():
            raise ValidacionError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise ValidacionError("La tarifa base debe ser un número positivo.")
        self._nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = True

    @property
    def nombre(self):
        return self._nombre

    @property
    def disponible(self):
        return self._disponible

    def cambiar_disponibilidad(self, disponible: bool):
        if not isinstance(disponible, bool):
            raise ValidacionError("La disponibilidad debe ser True o False.")
        self._disponible = disponible

    @abstractmethod
    def calcular_costo(self, cantidad: float = 1, impuesto: float = 0.0,
                       descuento: float = 0.0) -> float:
        pass

    @abstractmethod
    def validar_parametros(self, cantidad: float):
        pass

    def describir(self):
        estado = "disponible" if self._disponible else "no disponible"
        return f"{self._nombre} - {estado}"


class ReservaSala(Servicio):
    def validar_parametros(self, cantidad):
        if cantidad <= 0 or cantidad > 12:
            raise ValidacionError("La reserva de sala debe ser de 1 a 12 horas.")

    def calcular_costo(self, cantidad=1, impuesto=0.0, descuento=0.0):
        self.validar_parametros(cantidad)
        return _calcular_total(self._tarifa_base * cantidad, impuesto, descuento)


class AlquilerEquipo(Servicio):
    def validar_parametros(self, cantidad):
        if cantidad <= 0 or int(cantidad) != cantidad or cantidad > 30:
            raise ValidacionError("La cantidad de equipos debe ser un entero entre 1 y 30.")

    def calcular_costo(self, cantidad=1, impuesto=0.0, descuento=0.0):
        self.validar_parametros(cantidad)
        return _calcular_total(self._tarifa_base * cantidad, impuesto, descuento)


class AsesoriaEspecializada(Servicio):
    def validar_parametros(self, cantidad):
        if cantidad <= 0 or cantidad > 40:
            raise ValidacionError("La asesoría debe tener entre 1 y 40 horas.")

    def calcular_costo(self, cantidad=1, impuesto=0.0, descuento=0.0):
        self.validar_parametros(cantidad)
        return _calcular_total(self._tarifa_base * cantidad, impuesto, descuento)


def _calcular_total(subtotal, impuesto, descuento):
    """Cálculo común con validación de porcentajes."""
    if not 0 <= impuesto <= 1:
        raise ValidacionError("El impuesto debe expresarse entre 0 y 1.")
    if not 0 <= descuento <= 1:
        raise ValidacionError("El descuento debe expresarse entre 0 y 1.")
    if descuento + impuesto > 1.5:
        raise ValidacionError("La combinación de impuesto y descuento es inconsistente.")
    return round(subtotal * (1 - descuento) * (1 + impuesto), 2)


# ---------- Reserva ----------
class Reserva(Entidad):
    ESTADOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA", "PROCESADA")

    def __init__(self, identificador: str, cliente: Cliente, servicio: Servicio,
                 cantidad: float):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise ValidacionError("Debe asociarse un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ValidacionError("Debe asociarse un servicio válido.")
        servicio.validar_parametros(cantidad)
        self._cliente = cliente
        self._servicio = servicio
        self._cantidad = cantidad
        self._estado = "PENDIENTE"
        self._total = None

    @property
    def estado(self):
        return self._estado

    @property
    def total(self):
        return self._total

    def confirmar(self):
        if self._estado != "PENDIENTE":
            raise ReservaError("Solo se puede confirmar una reserva pendiente.")
        if not self._servicio.disponible:
            raise ServicioNoDisponibleError("El servicio no está disponible.")
        self._estado = "CONFIRMADA"
        logger.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        if self._estado in ("CANCELADA", "PROCESADA"):
            raise ReservaError("No se puede cancelar una reserva cancelada o procesada.")
        self._estado = "CANCELADA"
        logger.info("Reserva %s cancelada.", self.identificador)

    def procesar(self, impuesto=0.19, descuento=0.0):
        if self._estado != "CONFIRMADA":
            raise ReservaError("La reserva debe estar confirmada para procesarse.")
        try:
            self._total = self._servicio.calcular_costo(
                self._cantidad, impuesto, descuento
            )
        except ValidacionError as exc:
            # Encadenamiento: se conserva la causa original.
            raise ReservaError("No fue posible calcular el valor de la reserva.") from exc
        else:
            self._estado = "PROCESADA"
            logger.info("Reserva %s procesada. Total: %.2f", self.identificador, self._total)
            return self._total
        finally:
            logger.info("Finalizó el intento de procesamiento de %s.", self.identificador)

    def describir(self):
        return (f"Reserva {self.identificador} | {self._cliente.nombre} | "
                f"{self._servicio.nombre} | Estado: {self._estado}")


# ---------- Sistema de gestión ----------
class SistemaSoftwareFJ:
    def __init__(self):
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []

    def registrar_cliente(self, cliente: Cliente):
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise ValidacionError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logger.info("Cliente registrado: %s", cliente.identificador)

    def registrar_servicio(self, servicio: Servicio):
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise ValidacionError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logger.info("Servicio registrado: %s", servicio.identificador)

    def crear_reserva(self, reserva: Reserva):
        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise ValidacionError("Ya existe una reserva con ese identificador.")
        self.reservas.append(reserva)
        logger.info("Reserva creada: %s", reserva.identificador)

    def calcular_costo(self, servicio: Servicio, cantidad=1,
                       impuesto=0.0, descuento=0.0):
        """
        Método con variantes de parámetros opcionales:
        calcular_costo(servicio), calcular_costo(servicio, cantidad),
        o calcular_costo(servicio, cantidad, impuesto, descuento).
        """
        if servicio not in self.servicios:
            raise ServicioNoDisponibleError("El servicio no está registrado.")
        return servicio.calcular_costo(cantidad, impuesto, descuento)


# ---------- Demostración de mínimo 10 operaciones ----------
def ejecutar_demostracion():
    sistema = SistemaSoftwareFJ()
    print("=== SISTEMA INTEGRAL SOFTWARE FJ ===")

    # 1. Registro válido de cliente
    try:
        cliente1 = Cliente("C001", "Laura Gómez", "laura@email.com", "3001234567")
        sistema.registrar_cliente(cliente1)
        print("[1] Cliente válido registrado.")
    except SoftwareFJError as e:
        logger.exception("Operación 1: %s", e)
        print("[1] Error:", e)

    # 2. Registro inválido de cliente
    try:
        cliente_invalido = Cliente("C002", "Lu", "correo-invalido", "abc")
        sistema.registrar_cliente(cliente_invalido)
    except SoftwareFJError as e:
        logger.exception("Operación 2: %s", e)
        print("[2] Cliente inválido controlado:", e)

    # 3. Registro de segundo cliente
    try:
        cliente2 = Cliente("C003", "Carlos Pérez", "carlos@email.com", "3107654321")
        sistema.registrar_cliente(cliente2)
        print("[3] Segundo cliente registrado.")
    except SoftwareFJError as e:
        logger.exception("Operación 3: %s", e)
        print("[3] Error:", e)

    # 4. Creación de servicio de sala
    try:
        sala = ReservaSala("S001", "Sala de reuniones", 50000)
        sistema.registrar_servicio(sala)
        print("[4] Servicio de sala registrado.")
    except SoftwareFJError as e:
        logger.exception("Operación 4: %s", e)
        print("[4] Error:", e)

    # 5. Creación de servicio de alquiler de equipos
    try:
        equipo = AlquilerEquipo("S002", "Alquiler de portátil", 30000)
        sistema.registrar_servicio(equipo)
        print("[5] Servicio de equipo registrado.")
    except SoftwareFJError as e:
        logger.exception("Operación 5: %s", e)
        print("[5] Error:", e)

    # 6. Creación de servicio inválido
    try:
        servicio_invalido = AsesoriaEspecializada("S003", "Asesoría", -100)
        sistema.registrar_servicio(servicio_invalido)
    except SoftwareFJError as e:
        logger.exception("Operación 6: %s", e)
        print("[6] Servicio inválido controlado:", e)

    # 7. Crear y confirmar reserva correcta
    try:
        reserva1 = Reserva("R001", cliente1, sala, 2)
        sistema.crear_reserva(reserva1)
        reserva1.confirmar()
        print("[7] Reserva confirmada.")
    except SoftwareFJError as e:
        logger.exception("Operación 7: %s", e)
        print("[7] Error:", e)

    # 8. Procesar reserva con impuesto y descuento
    try:
        total = reserva1.procesar(impuesto=0.19, descuento=0.10)
        print(f"[8] Reserva procesada. Total: ${total:,.2f}")
    except SoftwareFJError as e:
        logger.exception("Operación 8: %s", e)
        print("[8] Error:", e)

    # 9. Intento incorrecto de procesar una reserva pendiente
    try:
        reserva2 = Reserva("R002", cliente2, equipo, 1)
        sistema.crear_reserva(reserva2)
        reserva2.procesar()
    except SoftwareFJError as e:
        logger.exception("Operación 9: %s", e)
        print("[9] Procesamiento incorrecto controlado:", e)

    # 10. Reserva con servicio no disponible
    try:
        equipo.cambiar_disponibilidad(False)
        reserva3 = Reserva("R003", cliente2, equipo, 1)
        sistema.crear_reserva(reserva3)
        reserva3.confirmar()
    except SoftwareFJError as e:
        logger.exception("Operación 10: %s", e)
        print("[10] Servicio no disponible controlado:", e)

    # 11. Parámetro fuera de rango
    try:
        sala.calcular_costo(20)
    except SoftwareFJError as e:
        logger.exception("Operación 11: %s", e)
        print("[11] Cantidad inválida controlada:", e)

    # 12. Try/except/else/finally y encadenamiento de excepciones
    try:
        # La validación del impuesto genera una excepción que se encadena.
        reserva4 = Reserva("R004", cliente1, sala, 1)
        sistema.crear_reserva(reserva4)
        reserva4.confirmar()
        reserva4.procesar(impuesto=2.0)
    except ReservaError as e:
        logger.exception("Operación 12: %s", e)
        print("[12] Excepción encadenada controlada:", e)
        print("     Causa original:", repr(e.__cause__))
    except SoftwareFJError as e:
        logger.exception("Operación 12 (validación): %s", e)
        print("[12] Error controlado:", e)
    else:
        print("[12] Operación terminada sin errores.")
    finally:
        print("[12] Bloque finally ejecutado.")

    print("\n=== RESUMEN ===")
    print("Clientes:", len(sistema.clientes))
    print("Servicios:", len(sistema.servicios))
    print("Reservas:", len(sistema.reservas))
    print("Los eventos y errores se guardaron en software_fj.log")
    print("\nReservas:")
    for reserva in sistema.reservas:
        print("-", reserva.describir())


if __name__ == "__main__":
    ejecutar_demostracion()
