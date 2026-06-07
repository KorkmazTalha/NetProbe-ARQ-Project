# utils/simulator.py
import random
import time
from config import LOSS_RATE, NETWORK_DELAY

def should_drop_packet(loss_rate=LOSS_RATE):
    """
    Belirlenen kayıp oranına göre (0.0 ile 1.0 arası)
    paketin düşürülüp düşürülmeyeceğine karar verir.
    """
    if loss_rate == 0.0:
        return False
    # Rastgele bir sayı üretip oranla karşılaştırıyoruz
    return random.random() < loss_rate

def simulate_network_delay(delay_sec=NETWORK_DELAY):
    """
    Belirlenen gecikme süresi kadar (saniye cinsinden) 
    akışı dondurarak ağ gecikmesini simüle eder.
    """
    if delay_sec > 0:
        time.sleep(delay_sec)