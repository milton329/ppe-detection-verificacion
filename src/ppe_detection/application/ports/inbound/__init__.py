"""Puertos inbound.

Con un único adapter inbound (la API HTTP) los propios casos de uso
concretos (`DetectPPEUseCase`, etc.) actúan como el puerto inbound: no se
introduce un `Protocol` adicional sin un segundo implementador que lo
justifique. Si aparece otro adapter inbound (p. ej. un CLI) que necesite
una interfaz explícita compartida, se define aquí.
"""
