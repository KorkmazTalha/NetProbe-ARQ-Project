# src/protocol.py
import hashlib

def calculate_checksum(data: bytes) -> str:
    """Verinin bütünlüğünü doğrulamak için MD5 hash'i üretir."""
    return hashlib.md5(data).hexdigest()

def create_packet(packet_type: str, seq_no: int, payload: bytes) -> bytes:
    """
    Özel protokolümüze uygun paket oluşturur.
    Format: TYPE | SEQ_NO | CHECKSUM | PAYLOAD
    """
    checksum = calculate_checksum(payload)
    
    # Header kısmını string olarak hazırlayıp encode ediyoruz
    header = f"{packet_type}|{seq_no}|{checksum}|".encode('utf-8')
    
    # Header ve gerçek veriyi (payload) byte olarak birleştiriyoruz
    return header + payload

def parse_packet(packet_bytes: bytes):
    """
    Gelen ham byte verisini ayrıştırır.
    Sistem header'ı çözebilmek için ilk 3 ayraca göre böler, kalanı payload yapar.
    """
    try:
        # İlk 3 tane '|' karakterine göre veriyi bölüyoruz
        parts = packet_bytes.split(b'|', 3)
        
        packet_type = parts[0].decode('utf-8')
        seq_no = int(parts[1].decode('utf-8'))
        checksum = parts[2].decode('utf-8')
        payload = parts[3]
        
        return packet_type, seq_no, checksum, payload
    except Exception as e:
        # Paket bozuk geldiyse veya ayrıştırılamıyorsa None dönüyoruz
        return None