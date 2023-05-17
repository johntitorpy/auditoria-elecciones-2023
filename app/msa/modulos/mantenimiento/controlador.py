"""Controlador del modulo Mantenimiento."""
import json
import os
from os import popen
from time import sleep
from multiprocessing import Lock

from gi.repository.GObject import timeout_add
from msa.constants import PATH_CD
from msa.core.armve.constants import (AUTOFEED_1, AUTOFEED_2, AUTOFEED_SELECT,
                                      DEV_AGENT, DEV_PRINTER, DEV_RFID,
                                      PRINT_HIGH, PRINT_LOW, PRINT_MID,
                                      PRINT_SHIGH, PRINT_SLOW, PRINT_STEP)
from msa.core.audio.constants import VALORES_VOLUMEN
from msa.core.hardware.settings import USAR_PIR, USAR_PRESENCIA, DEFAULT_BRIGHTNESS
from msa.core.hardware.temperature import get_temp
from msa.modulos.base.actions import BaseActionController
from msa.modulos.base.controlador import ControladorBase
from msa.modulos.constants import COMANDO_EXPULSION_CD
from msa.modulos.mantenimiento.constants import (BATTERY_THRESHOLD,
                                                 DECREMENTO_BRILLO,
                                                 DECREMENTO_FAN,
                                                 INCREMENTO_BRILLO,
                                                 INCREMENTO_FAN,
                                                 INTERVALO_REFRESCO,
                                                 INTERVALO_REFRESCO_BATERIA,
                                                 POTENCIA_ALTA, POTENCIA_BAJA,
                                                 TEXTOS,
                                                 TIEMPO_DESACTIVACION_CHEQUEO)

from msa.core.logging import get_logger
from msa.core.led_action.constants import PREVIOUS_LED_ACTION
logger = get_logger("controlador_mantenimiento")


class Actions(BaseActionController):

    """Actions para el controlador del menu."""

    def click_boton(self, data):
        """Callback de cuando se hace click en el boton."""
        # Lo corro asincronico porque si queda dentro de un thread de webkit
        # cuando cambio de modulo tira un segfault
        self.call_async(self.controlador.modulo._btn_presionado, data)

    def load_maintenance(self, data):
        """Carga el modulo de mantenimiento."""
        self.call_async(self.controlador.inicio_mantenimiento)

    def volume(self, data):
        """Cambia el volumen."""
        self.controlador.set_volume(data)

    def brightness(self, data):
        """Cambia el brillo."""
        self.controlador.set_brightness(data)

    def check_rfid(self, data):
        """Chequea el rfid."""
        self.controlador.rfid_check(data)

    def check_fan(self, data):
        """Chequea el fan."""
        self.controlador.fan_check()

    def fan_auto_mode(self, data):
        """Establece el automode del fan."""
        self.controlador.set_fan_auto_mode(data)

    def fan_speed(self, data):
        """Pregunta la velocidad del fan."""
        self.controlador.process_fan_speed(data)

    def eject_cd(self, data):
        """Expulsa el CD."""
        self.controlador.eject_cd()

    def printer_test(self, data):
        """Lanza el test de impresion."""
        self.controlador.modulo.printer_begin_test()

    def printer_test_cancel(self, data):
        """Cancela el test de impresion."""
        self.controlador.modulo.printer_end_test()

    def respuesta_dialogo(self, data):
        """Cancela el test de impresion."""
        if not data:
            self.controlador.printer_cancel_test()

    def presencia_mode(self, data):
        """Pide el modo del PRESENCIA."""
        self.controlador.set_presencia_mode(data)

    def presencia_registro(self, data):
        """ 
        Determina si tenemos que seguir escuchando o no 
        los eventos de presencia 
        """
        if data:
            self.controlador.add_presencia()
        else:
            
            self.controlador.remove_presencia()


    def md5check(self, data):
        """Llama al chequeo del DVD."""
        self.controlador.md5check()

    def autofeed_mode(self, data):
        """Setea el modo de autofeed."""
        self.controlador.set_autofeed_mode(data)

    def get_autofeed_mode(self, data):
        """Setea el modo del autofeed."""
        self.controlador.get_autofeed_mode()

    def reset_device(self, data):
        """Resetea el dispositivo."""
        self.controlador.reset_device(data)

    def print_quality(self, data):
        """Modifica la calidad de impresion."""
        self.controlador.set_print_quality(data)

    def get_print_quality(self, data):
        """Obtiene la calidad de impresion."""
        self.controlador.get_print_quality()

    def refresh(self, data):
        """Actualiza los datos de la pantalla."""
        self.controlador.get_temperature()
        self.controlador.get_fan_speed()
        self.controlador.get_fan_mode(True)
        self.controlador.get_power_source()

    def refresh_batteries_status(self, data):
        """Refresca el estado de las baterias."""
        self.controlador.get_battery_status()


class Controlador(ControladorBase):

    """Controller para la interfaz web de voto."""

    def __init__(self, modulo):
        """Constructor del controlador de Mantenimiento."""
        super(Controlador, self).__init__(modulo)
        self.textos = TEXTOS
        self.set_actions(Actions(self))

        self.modulo._start_audio()

    def document_ready(self, data):
        """Callback que ejecuta el browser en el document.ready()"""
        self.modulo._inicio()

    def inicio_mantenimiento(self):
        """Corre el inicio de los datos del modulo de mantenimiento."""
        self._volume_lock = Lock()
        self.get_volume()
        if self.rampa.tiene_conexion is not None:
            self.get_rfid_antenna_level()
            self.get_build()
            self.get_fan_mode(True)
            self.get_fan_speed()
            self.get_temperature()
            self.get_brightness()
            self.get_power_source()
            self.get_presencia_status()
            self.get_presencia_mode(True)
        self.send_command("inicio_mantenimiento")

        self.timeout_bateria = timeout_add(10000, self.get_battery_status)
        self.send_command("inicio_intervals")

    def get_volume(self):
        """Devuelve el volumen."""
        level = self.modulo._player.get_volume()
        if level is not None:
            self.volume_level = level + 1
            self.send_command("mostrar_volumen",
                              {'volumen': self.volume_level})

    def _update_player_volume(self):
        """Sincroniza el volumen actual con el del controlador de sonido del
        sistema operativo."""
        self.modulo._player.set_volume(self.volume_level - 1)
        self.send_command("mostrar_volumen", {'volumen': self.volume_level})
        self.modulo.play_sonido_ok()

    def set_volume(self, data):
        """Establece el volumen."""
        self._volume_lock.acquire()

        if self.volume_level < len(VALORES_VOLUMEN) and data == "arriba":
            self.volume_level += 1
            self._update_player_volume()
        elif self.volume_level > 1 and data == "abajo":
            self.volume_level -= 1
            self._update_player_volume()

        self._volume_lock.release()

    def get_power_source(self):
        """Devuelve la fuente de alimentacion."""
        if self.rampa.tiene_conexion:
            power_source = self.rampa.get_power_source()
            if power_source is not None:
                self.power_source = power_source['byte']
                self.send_command("mostrar_fuente_energia",
                                  {'power_source': self.power_source})
        else:
            self.send_command("mostrar_fuente_energia",
                              {'power_source': 0})

    def get_battery_status(self):
        """Devuelve el estado de la batería."""
        if self.rampa.tiene_conexion:
            battery_data = self.rampa.get_power_status()
            batteries = None

            if battery_data is not None:
                if battery_data["batt_number"] > 0:
                    json_battery = battery_data["batt_data"]
                    batteries = []
                    lowest_current = 0
                    battery_discharging = 0
                    for battery in json_battery:
                        full_charge = battery["full_charge"]
                        remaining = battery["remaining"]
                        battery["battery_level"] = \
                            int(int(remaining) * 100 / (full_charge))
                        battery["discharging"] = False
                        if battery["corriente"] < lowest_current:
                            lowest_current = battery["corriente"]
                            battery_discharging = battery["slot_number"]
                        elif battery["corriente"] > BATTERY_THRESHOLD:
                            battery["charging"] = True
                        batteries.append(battery)

                    if battery_discharging:
                        for battery in batteries:
                            if battery["slot_number"] == battery_discharging:
                                battery["discharging"] = True
                    batteries.reverse()
                else:
                    batteries = 0

            self.send_command("mostrar_bateria", {'baterias': batteries})
        return True

    def get_brightness(self):
        """Devuelve el brillo de la pantalla."""
        if self.rampa.tiene_conexion:
            brightness = self.rampa.get_actual_brightness()
            if brightness is not None:
                self.brightness_level = int(brightness)
                self.send_command("mostrar_brillo",
                                {'brillo': self.brightness_level})

    def set_brightness(self, data):
        """Establece el brillo."""
        if data == "arriba" and int(self.brightness_level) < 100:
            self.brightness_level = self.brightness_level + INCREMENTO_BRILLO
        # consulto por mayor a 20 para que nunca llegue a ser 0 para que no 
        # quede la pantalla totalmente oscura
        elif data == "abajo" and int(self.brightness_level) > 20:
            self.brightness_level = self.brightness_level - DECREMENTO_BRILLO
        self.set_specific_brightness(self.brightness_level)
        self.rampa.set_actual_brightness(self.brightness_level)
        self.send_command("mostrar_brillo", {'brillo': self.brightness_level})

    def get_build(self):
        """Devuelve el build de la placa."""
        build = self.rampa.get_arm_build()
        machine_type = self.rampa.get_arm_version()
        self.send_command("mostrar_build", {'build': build,
                                            'machine': machine_type})

    def get_rfid_antenna_level(self):
        """Devuelve el nivel de la antena de RFID."""
        level = self.rampa.get_antenna_level()
        if level is not None:
            level = level['byte']
            if level:
                antenna_level = POTENCIA_ALTA
            else:
                antenna_level = POTENCIA_BAJA
            self.send_command("mostrar_potencia_rfid",
                            {'potencia': antenna_level})

    def rfid_check(self, data):
        """Chequea el rfid."""
        self.send_command("mostrar_rfid", data)

    def get_fan_speed(self):
        """Devuelve la velocidad del Fan."""
        if self.rampa.tiene_conexion and not self.fan_mode:
            self.fan_speed = self.rampa.get_fan_speed()
            try:
                self.fan_speed = self.fan_speed['byte']
                self.send_command("mostrar_velocidad_ventilador",
                                  {'velocidad': self.fan_speed})
            except:
                pass
        return False

    def set_fan_speed(self, data):
        """Establece la velocidad del fan."""
        self.rampa.set_fan_speed(data)

    def get_fan_mode(self, display=False):
        """
        Devuelve el modo del fan.

        True = modo automatico. False = modo manual
        """
        try:
            modo_actual = self.fan_mode
        except:
            if self.rampa.tiene_conexion:
                self.fan_mode = self.rampa.get_fan_mode()
            else:
                self.fan_mode = True
            modo_actual = self.fan_mode
        if display:
            self.send_command("mostrar_modo_ventilador",
                              {'modo_auto': modo_actual})
        return modo_actual

    def set_fan_auto_mode(self, data):
        """
        Establece el modo del fan.

        True = modo automatico. False = modo manual
        """
        self.fan_mode = int(data)
        self.rampa.set_fan_mode(self.fan_mode)
        timeout_add(1000, self.get_fan_speed)

    def process_fan_speed(self, data):
        """Procesa la velocidad del fan. Muestra la velocidad en pantalla."""
        if data == "arriba" and int(self.fan_speed) < 100:
            self.fan_speed = self.fan_speed + INCREMENTO_FAN
        elif data == "abajo" and int(self.fan_speed) > 0:
            self.fan_speed = self.fan_speed - DECREMENTO_FAN
        self.set_fan_speed(self.fan_speed)
        self.send_command("mostrar_velocidad_ventilador",
                          {'velocidad': self.fan_speed})

    def fan_check(self):
        """Test de funcionamiento del Fan."""
        current_mode_auto = self.get_fan_mode()
        if current_mode_auto:
            reset_auto_mode = True
            self.set_fan_auto_mode(False)
        else:
            reset_auto_mode = False
            pre_velocity = self.fan_speed
        self.set_fan_speed(0)
        sleep(1)
        self.set_fan_speed(100)
        sleep(8)
        self.set_fan_speed(0)
        sleep(1)
        if reset_auto_mode:
            self.set_fan_auto_mode(1)
        else:
            self.set_fan_speed(pre_velocity)

    def get_temperature(self):
        """Devuelve la temperatura de la maquina."""
        temperature = get_temp()
        self.send_command("mostrar_temperatura", {'temperatura': temperature})

    def refresh_batteries(self):
        """Refresca los datos de bateria."""
        self.get_power_source()
        self.send_command("refresh_batteries")

    def eject_cd(self):
        """Expulsa el Disco."""
        os.system(COMANDO_EXPULSION_CD)

    def get_presencia_status(self):
        """Devuelve el estado del PIR."""
        if USAR_PRESENCIA and self.rampa.tiene_conexion is not None:
            presencia_status = self.rampa.get_presencia_status()
            try:
                presencia_status = presencia_status['byte']
                self.send_command("mostrar_estado_presencia", {'estado': presencia_status})
            except:
                pass

    def presencia_detection_status(self, detection_status):
        """Muestra el estado del PRESENCIA."""
        self.send_command("mostrar_estado_presencia",
                          {'estado': detection_status})

    def print_test(self):
        """Realiza el test de impresion."""
        self.send_command("mostrar_test_impresora", {'estado': 'imprimiendo'})
        tipo_tag = "Prueba"
        seleccion_tag = ""
        self.rampa.set_led_action('impresion_mantenimiento', 'espera_en_antena')
        self.rampa.imprimir_serializado(tipo_tag, seleccion_tag,
                                               transpose=False)

    def printer_begin_test(self):
        """Empieza el test de impresion."""
        self.rampa.set_led_action('pantalla_espera_sufragio', PREVIOUS_LED_ACTION)
        self.send_command("mostrar_test_impresora", {'estado': 'esperando'})

    def printer_end_test(self):
        """Finaliza el test de impresion."""
        self.send_command("ocultar_test_impresora")
    
    def printer_cancel_test(self):
        """Finaliza el test de impresion."""
        self.printer_end_test()
        self.rampa.set_led_action('espera_en_antena')

    def get_presencia_mode(self, display=False):
        """Devuelve el modo del PIR."""
        try:
            modo_actual = self.presencia_mode
        except:
            if self.rampa.tiene_conexion:
                self.presencia_mode = self.rampa.get_presencia_mode()
                modo_actual = self.presencia_mode
            else:
                modo_actual = None
        if display:
            self.send_command("mostrar_modo_presencia",
                              {'presencia_activada': modo_actual})
        return modo_actual
    
    def actualizar_checkbox(self, modo_actual):
        self.send_command("mostrar_modo_presencia",
                          {'presencia_activada': modo_actual})
        
    def bloquear_desbloquear_checkbox(self, bloqueo=False):
        """
        Este método manda a desbloquear o bloquear el checkbox de utilización de 
        asistencia dependiendo de por quién fue llamado.
        Cuando es lanzado por el evento de plugged, debe bloquear.
        Cuando es lanzado por el evento de unplugged, debe desbloquear. 
        """
        logger.warning('bloquear desbloquear --> %s', bloqueo)
        self.send_command("bloquear_desbloquear_checkbox",
                          {'bloqueo': bloqueo})

    def set_presencia_mode(self, data):
        """Establece el modo del PRESENCIA."""
        logger.warning('set presencia mode')
        self.presencia_mode = int(data)
        self.rampa.set_presencia_mode(self.presencia_mode)
        self.modulo.start_presencia()

    def add_presencia(self):
        """
        logger.warning('add presencia')
        self.rampa.registrar_presencia()
        """
        pass

    def remove_presencia(self):
        """
        logger.warning('remove presencia')
        self.rampa.remover_presence_changed()
        """
        pass
        
    def get_autofeed_mode(self):
        """Devuelve el modo de autofeed."""
        mode = self.rampa.get_autofeed_mode()
        self.autofeed_mode = mode.get('af_type')

        if self.autofeed_mode == AUTOFEED_1:
            modo = 1
        elif self.autofeed_mode == AUTOFEED_2:
            modo = 2
        else:
            modo = 0
        self.send_command("mostrar_autofeed",
                          {'autofeed': modo})

    def set_autofeed_mode(self, data):
        """Establece el modo de autofeed."""
        modo = int(data)
        if modo == 0:
            self.autofeed_mode = AUTOFEED_SELECT
        elif modo == 1:
            self.autofeed_mode = AUTOFEED_1
        else:
            self.autofeed_mode = AUTOFEED_2
        self.rampa.set_autofeed_mode(self.autofeed_mode)

    def md5check(self):
        """Chequea los md5 del disco."""
        md5 = self.modulo.md5_checkfiles(PATH_CD)
        if not md5:
            md5 = "La prueba de integridad ha finalizado correctamente"
        else:
            md5 = "La prueba de integridad ha fallado"
        self.send_command("mostrar_md5", {'md5': md5})

    def reset_device(self, data):
        """Resetea el dispositivo solicitado."""
        device_name = data
        if device_name == "rfid":
            device_id = DEV_RFID
        elif device_name == "printer":
            device_id = DEV_PRINTER
        else:
            device_id = DEV_AGENT

        self.rampa.reset(device_id)

    def set_print_quality(self, data):
        """Establece la calidad de impresion."""
        quality = int(data)
        self.rampa.set_printer_quality(quality)

    def get_print_quality(self):
        """Obtiene la calidad de impresion."""
        data = self.rampa.get_printer_quality()
        self.print_quality = data[0]['byte']

        error = PRINT_STEP / 2
        if self.print_quality < (PRINT_SLOW + error):
            print_quality_adjusted = PRINT_SLOW
        elif self.print_quality < (PRINT_LOW + error):
            print_quality_adjusted = PRINT_LOW
        elif self.print_quality < (PRINT_MID + error):
            print_quality_adjusted = PRINT_MID
        elif self.print_quality < (PRINT_HIGH + error):
            print_quality_adjusted = PRINT_HIGH
        else:
            print_quality_adjusted = PRINT_SHIGH

        self.send_command("mostrar_print_quality",
                          {'print_quality': print_quality_adjusted})

    def get_constants(self):
        """Genera las constantes para enviar a la UI."""
        niveles_impresion = [PRINT_SLOW, PRINT_LOW, PRINT_MID, PRINT_HIGH,
                             PRINT_SHIGH]

        local_constants = {
            "intervalo_refresco": INTERVALO_REFRESCO,
            "intervalo_refresco_bateria": INTERVALO_REFRESCO_BATERIA,
            "tiempo_desactivacion_chequeo": TIEMPO_DESACTIVACION_CHEQUEO,
            "niveles_impresion": niveles_impresion,
            "usar_pir": True,
        }
        constants = self.base_constants_dict()
        constants.update(local_constants)
        return constants
