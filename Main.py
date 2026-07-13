from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
# Importamos el hardware de plyer
from plyer import vibrator, notification 
import threading, time, requests

class TradingApp(MDApp):
    def build(self):
        self.screen = MDScreen()
        self.search_input = MDTextField(hint_text="Ej: BTCUSDT", pos_hint={"center_x": 0.5, "center_y": 0.8}, size_hint=(0.8, None))
        self.btn = MDRaisedButton(text="Analizar 15m", pos_hint={"center_x": 0.5, "center_y": 0.7}, on_release=self.update_coin)
        self.lbl = MDLabel(text="Iniciando...", halign="center", pos_hint={"center_y": 0.4}, font_style="H6")
        self.screen.add_widget(self.search_input); self.screen.add_widget(self.btn); self.screen.add_widget(self.lbl)
        
        self.symbol = "BTCUSDT"
        self.ultima_señal = "" # Para detectar el cambio
        threading.Thread(target=self.market_loop, daemon=True).start()
        return self.screen

    def update_coin(self, instance):
        if self.search_input.text.strip():
            self.symbol = self.search_input.text.upper().strip()

    def market_loop(self):
        while True:
            try:
                url = f"https://api.binance.com/api/v3/klines?symbol={self.symbol}&interval=15m&limit=20"
                data = requests.get(url, timeout=5).json()
                closes = [float(candle[4]) for candle in data]
                current_price = closes[-1]
                
                ema_fast = sum(closes[-5:]) / 5
                ema_slow = sum(closes) / 20
                
                # Definir señal actual
                es_alcista = ema_fast > ema_slow
                señal_actual = "ALCISTA" if es_alcista else "BAJISTA"
                
                # --- LÓGICA DE ALERTA (Cambio de estado) ---
                if self.ultima_señal != "" and self.ultima_señal != señal_actual:
                    self.trigger_alert(señal_actual)
                
                self.ultima_señal = señal_actual
                
                # UI Update
                color = "#2ecc71" if es_alcista else "#e74c3c"
                texto = f"ACTIVO: {self.symbol}\nPRECIO: ${current_price:.2f}\n\nSEÑAL: {señal_actual}\n\nTP: ${current_price*1.025:.2f} | SL: ${current_price*0.985:.2f}"
                Clock.schedule_once(lambda dt: self.update_ui(texto, color))
                
            except:
                pass
            time.sleep(10)

    def trigger_alert(self, nueva_señal):
        # Vibrar por 0.5 segundos
        vibrator.vibrate(0.5)
        # Notificación push
        notification.notify(
            title="Cambio de Tendencia",
            message=f"La tendencia ahora es: {nueva_señal}",
            app_name="TradingBot"
        )

    def update_ui(self, texto, color):
        self.lbl.text = texto
        self.lbl.theme_text_color = "Custom"
        self.lbl.text_color = get_color_from_hex(color)

if __name__ == "__main__":
    TradingApp().run()
