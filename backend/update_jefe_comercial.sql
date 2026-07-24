-- 1. Insertar el nuevo rol JefeComercial (si no existe previamente)
INSERT INTO roles (codigo, nombre)
SELECT 'JefeComercial', 'Jefe Comercial'
WHERE NOT EXISTS (SELECT 1 FROM roles WHERE codigo = 'JefeComercial');

-- 2. Copiar exactamente los mismos permisos del rol 'Comercial' al rol 'JefeComercial'
INSERT INTO permisos (rol_id, modulo_id, operacion_id, permitido)
SELECT 
    (SELECT id FROM roles WHERE codigo = 'JefeComercial'),
    modulo_id,
    operacion_id,
    permitido
FROM permisos
WHERE rol_id = (SELECT id FROM roles WHERE codigo = 'Comercial')
  AND NOT EXISTS (
      SELECT 1 FROM permisos p2 
      WHERE p2.rol_id = (SELECT id FROM roles WHERE codigo = 'JefeComercial') 
        AND p2.modulo_id = permisos.modulo_id 
        AND p2.operacion_id = permisos.operacion_id
  );

-- 3. Asignar el nuevo rol al usuario comercial1
UPDATE usuarios
SET rol_id = (SELECT id FROM roles WHERE codigo = 'JefeComercial')
WHERE username = 'comercial1';
