UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10421580605' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10416085884' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20601620147' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20610873309' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20610873309' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10315432397' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10473108823' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10473108823' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    comision = 53.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20612275603' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.035,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20535021563' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.035,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10239291240' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.035,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10768340108' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.035,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10770876970' AND e_acop.razon_social LIKE '%Alfred%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.46,
    dscto_ley_comercial = 0.007,
    lim_ley_inferior = 0.020,
    lim_ley_superior = 0.099,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10082235774' AND e_acop.razon_social LIKE '%Melchor%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.46,
    dscto_ley_comercial = 0.007,
    lim_ley_inferior = 0.020,
    lim_ley_superior = 0.099,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20517242919' AND e_acop.razon_social LIKE '%Melchor%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.130,
    umbral_recup_medio = 0.150,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10457401928' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.130,
    umbral_recup_medio = 0.150,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10761932735' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.130,
    umbral_recup_medio = 0.150,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10408856049' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606333219' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10414969564' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.130,
    umbral_recup_medio = 0.150,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20613105621' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.130,
    umbral_recup_medio = 0.150,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10473594281' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10422176905' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.130,
    umbral_recup_medio = 0.150,
    lim_ley_comercial = 0.548,
    dscto_ley_comercial = 0.035,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10313031921' AND e_acop.razon_social LIKE '%Richard%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    comision = 10.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20612921866' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    comision = 10.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614635101' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20169040231' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20608774000' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20601769396-' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20610807004' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.15,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606562480' AND e_acop.razon_social LIKE '%Ronald%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.13,
    umbral_recup_medio = 0.17,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20601769396' AND e_acop.razon_social LIKE '%Evelyn%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.13,
    umbral_recup_medio = 0.17,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10014997313' AND e_acop.razon_social LIKE '%Oscar%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20612937096' AND e_acop.razon_social LIKE '%Walter%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20612719757'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20611329556' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606102519' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606094010' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20611748486' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10479968131' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606526599' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20604990000' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20611739509' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20609542722' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10306762465' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 75.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20548542422' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20604990000' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606102519' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20611000350' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10756747652' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20609578786' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10424767285' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20612791148' AND e_acop.razon_social LIKE '%Walter%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10445192410' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20603329059' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606527439' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614284740' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614031698' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606480840' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20611329556' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20613170848' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20603162812' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20609653036' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.417,
    dscto_ley_comercial = 0.025,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614329646' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20612223395' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20612554863' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10470098142' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614253348' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20611749784' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10304814751' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20615424031' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20613823710' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.4,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 80.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20613018604' AND e_acop.razon_social LIKE '%Robinson%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.12,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20610807004' AND e_acop.razon_social LIKE '%Renzo%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.12,
    umbral_recup_medio = 0.20,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20606562480' AND e_acop.razon_social LIKE '%Nelly%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.13,
    umbral_recup_medio = 0.17,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20613935151' AND e_acop.razon_social LIKE '%Dante%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.13,
    umbral_recup_medio = 0.17,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614284740' AND e_acop.razon_social LIKE '%Dante%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '10404377324'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.035,
    lim_ley_superior = 0.099,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20612137502'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20601463173' AND e_acop.razon_social LIKE '%Yuri%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '123456' AND e_acop.razon_social LIKE '%Beto%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10486077447' AND e_acop.razon_social LIKE '%Martin%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 85.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10737057025' AND e_acop.razon_social LIKE '%Karina%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.376,
    dscto_ley_comercial = 0.024,
    lim_ley_inferior = 0.030,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '10486077447,'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20614284740' AND e_acop.razon_social LIKE '%Walter%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.050,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '10304932789'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.366,
    dscto_ley_comercial = 0.022,
    lim_ley_inferior = 0.050,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20612590002'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20448645097'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.13,
    umbral_recup_medio = 0.17,
    lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20601769396' AND e_acop.razon_social LIKE '%Zudaire%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.46,
    dscto_ley_comercial = 0.007,
    lim_ley_inferior = 0.020,
    lim_ley_superior = 0.099,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20506072248' AND e_acop.razon_social LIKE '%Melchor%'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20000000001'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '10602688050'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20611795794'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '10800995405'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20554057862'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '10403381361'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20609745372'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20606534923'
);

UPDATE parametros_comerciales
SET lim_ley_comercial = 0.317,
    dscto_ley_comercial = 0.019,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    
    WHERE e_prov.ruc = '20611424541'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.36666666666666664,
    dscto_ley_comercial = 0.022,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20603169094' AND e_acop.razon_social LIKE '%YEREMY%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.36666666666666664,
    dscto_ley_comercial = 0.022,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 90.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '10801024969' AND e_acop.razon_social LIKE '%YEREMY%'
);

UPDATE parametros_comerciales
SET umbral_recup_bajo = 0.149,
    umbral_recup_medio = 0.199,
    lim_ley_comercial = 0.33,
    dscto_ley_comercial = 0.033,
    lim_ley_inferior = 0.040,
    lim_ley_superior = 0.099,
    maquila = 69.0,
    gasto_acopio_llampo = gasto_acopio + 10,
    gasto_consumo_llampo = gasto_consumo + 40
WHERE provacop_id IN (
    SELECT pa.id 
    FROM proveedor_acopiador pa
    JOIN entidades e_prov ON e_prov.id = pa.proveedor_id
    JOIN entidades e_acop ON e_acop.id = pa.acopiador_id
    WHERE e_prov.ruc = '20000000000' AND e_acop.razon_social LIKE '%ALFRED%'
);
