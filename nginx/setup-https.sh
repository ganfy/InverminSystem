#!/bin/bash
# =============================================================================
# setup-https.sh — Configurar HTTPS con certificado auto-firmado
# Para usar cuando NO hay dominio DNS (solo IP pública: 20.163.45.40)
#
# Ejecutar en el servidor Azure (vía SSH):
#   chmod +x setup-https.sh
#   sudo ./setup-https.sh
# =============================================================================

set -e

IP_PUBLICA="20.163.45.40"
SSL_DIR="/opt/invermin/ssl"

echo "=== Configurando HTTPS para InverminSystem ==="
echo "IP pública: $IP_PUBLICA"

# 1. Crear directorio SSL
mkdir -p "$SSL_DIR"

# 2. Generar certificado auto-firmado (válido 2 años)
echo ""
echo "Generando certificado auto-firmado..."
openssl req -x509 -nodes -days 730 -newkey rsa:2048 \
    -keyout "$SSL_DIR/server.key" \
    -out "$SSL_DIR/server.crt" \
    -subj "/C=PE/ST=Arequipa/L=Arequipa/O=Invermin Paititi SAC/CN=$IP_PUBLICA" \
    -addext "subjectAltName=IP:$IP_PUBLICA"

echo "✓ Certificado generado en $SSL_DIR"

# 3. Verificar que el puerto 443 esté disponible
echo ""
echo "Verificando puerto 443..."
if ss -tlnp | grep -q ':443'; then
    echo "  ⚠  Puerto 443 ya en uso. Verificar qué proceso lo ocupa:"
    ss -tlnp | grep ':443'
else
    echo "  ✓ Puerto 443 disponible"
fi

# 4. Verificar puertos abiertos en NSG (informativo)
echo ""
echo "=== Estado de puertos en el servidor ==="
echo "Puertos en escucha:"
ss -tlnp | grep -E ':80|:443|:8080|:8000'

echo ""
echo "=== PRÓXIMOS PASOS ==="
echo ""
echo "1. Actualizar docker-compose.prod.yml para usar nginx con SSL:"
echo "   Ver: docker-compose.ssl.yml en el repositorio"
echo ""
echo "2. Abrir puerto 443 en Azure NSG (si no está abierto):"
echo "   Portal Azure → VM → Redes → Reglas de entrada → Agregar:"
echo "   Puerto: 443 | Protocolo: TCP | Acción: Permitir | Prioridad: 100"
echo ""
echo "3. Reconstruir y levantar:"
echo "   docker compose -f docker-compose.ssl.yml up -d --build"
echo ""
echo "4. Actualizar frontend/.env.production:"
echo "   VITE_API_URL=https://$IP_PUBLICA"
echo ""
echo "5. En dispositivos móviles — primera vez:"
echo "   - Abrir https://$IP_PUBLICA en el navegador"
echo "   - Aceptar la advertencia del certificado auto-firmado"
echo "   - En Android: Menú → 'Añadir a pantalla de inicio' para crear acceso directo"
echo "   - En iOS: Ajustes → General → VPN y gestión → Confiar en el certificado"
echo ""
echo "=== Script completado ==="
