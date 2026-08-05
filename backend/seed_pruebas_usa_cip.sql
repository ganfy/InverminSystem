-- =============================================================================
-- Seed: pruebas_usa_cip en tabla configuraciones
-- =============================================================================
-- Inserta la configuración del modo de identificación de muestras en Pruebas.
-- Valor: 'true'  ? CIPs ofuscados (CIP-XXXXXX-R1) — comportamiento original
--        'false' ? IP con sufijo  (IP-0042-R1)     — modo laboratorio interno
--
-- IDEMPOTENTE: no hace nada si la clave ya existe.
-- Compatible con: PostgreSQL y SQL Server
-- Ejecutar UNA SOLA VEZ en producción.
-- Luego se puede cambiar desde Admin > Configuración del Sistema.
-- =============================================================================

-- -- PostgreSQL ----------------------------------------------------------------
INSERT INTO configuraciones (clave, valor, descripcion)
VALUES (
    'pruebas_usa_cip',
    'true',
    'Modo de identificación de muestras en Pruebas Metalúrgicas. true: CIPs ofuscados (CIP-XXXXXX-R1). false: IP con sufijo (IP-0042-R1).'
)
ON CONFLICT (clave) DO NOTHING;

-- -- SQL Server (alternativa) --------------------------------------------------
-- IF NOT EXISTS (SELECT 1 FROM configuraciones WHERE clave = 'pruebas_usa_cip')
-- BEGIN
--     INSERT INTO configuraciones (clave, valor, descripcion)
--     VALUES (
--         'pruebas_usa_cip',
--         'true',
--         'Modo de identificacion en Pruebas Metalurgicas. true: CIPs ofuscados. false: IP con sufijo (IP-0042-R1).'
--     )
-- END
