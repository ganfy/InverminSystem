DO $$
DECLARE
    v_analisis_id INT;
BEGIN
    -- CIP CIP-256000
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256000', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1253, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1703, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.9078, 1.3647, 1);

    -- CIP CIP-256001
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256001', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1086, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1166, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.755, 2.51, 1);

    -- CIP CIP-256002
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256002', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1259, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1149, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.9175, 2.1038, 1);

    -- CIP CIP-256003
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256003', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0684, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0683, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.3184, 0.7008, 1);

    -- CIP CIP-256004
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256004', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0715, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.066, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.2899, 0.8755, 1);

    -- CIP CIP-256005
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256005', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0684, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0674, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.067, 0.5029, 1);

    -- CIP CIP-256006
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256006', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0631, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0622, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.9493, 0.6238, 1);

    -- CIP CIP-256007
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256007', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0715, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0695, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.998, 0.0274, 1);

    -- CIP CIP-256008
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256008', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0757, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.07, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.6958, 0.0299, 1);

    -- CIP CIP-256009
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256009', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1896, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1984, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.3497, 0.3136, 1);

    -- CIP CIP-256010
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256010', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.194, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1816, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.8707, 0.3169, 1);

    -- CIP CIP-256011
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256011', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0686, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0687, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.4732, 0.0142, 1);

    -- CIP CIP-256012
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256012', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0652, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0724, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.5253, 0.0346, 1);

    -- CIP CIP-256013
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256013', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1625, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1705, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.7038, 0.0827, 1);

    -- CIP CIP-256014
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256014', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1759, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1712, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.9405, 0.0775, 1);

    -- CIP CIP-256015
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256015', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1066, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1071, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.2891, 0.1286, 1);

    -- CIP CIP-256016
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256016', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1037, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1097, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.4885, 0.1285, 1);

    -- CIP CIP-256017
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256017', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1032, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1137, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.8827, 0.121, 1);

    -- CIP CIP-256018
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256018', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0994, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0988, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.7379, 0.1889, 1);

    -- CIP CIP-256019
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256019', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1018, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0998, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.2998, 0.1127, 1);

    -- CIP CIP-256020
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256020', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1016, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0979, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.5044, 0.1013, 1);

    -- CIP CIP-256021
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256021', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.3241, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.3201, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.4018, 0.8991, 1);

    -- CIP CIP-256022
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256022', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.2994, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.3014, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.5271, 1.1901, 1);

    -- CIP CIP-256023
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256023', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.21, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.2116, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.1151, 0.2103, 1);

    -- CIP CIP-256024
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256024', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.211, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.191, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.3291, 0.4049, 1);

    -- CIP CIP-256025
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256025', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1566, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1767, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 5.2235, 0.6293, 1);

    -- CIP CIP-256026
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256026', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.131, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1481, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 6.491, 0.8885, 1);

    -- CIP CIP-256027
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256027', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1453, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1342, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.6391, 0.572, 1);

    -- CIP CIP-256028
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256028', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1252, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.14, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.26, 0.4257, 1);

    -- CIP CIP-256029
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256029', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.0667, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.0669, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 5.7622, 0.6119, 1);

    -- CIP CIP-256030
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256030', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.5008, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.5127, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 5.2424, 0.1911, 1);

    -- CIP CIP-256031
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256031', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.4856, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.4936, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.4965, 0.2552, 1);

    -- CIP CIP-256032
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256032', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1412, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1393, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 11.6055, 0.8954, 1);

    -- CIP CIP-256033
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256033', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1433, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.148, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 11.5601, 0.6791, 1);

    -- CIP CIP-256034
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256034', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1535, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1427, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 9.8884, 0.8633, 1);

    -- CIP CIP-256035
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256035', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1426, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1604, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.4848, 0.4908, 1);

    -- CIP CIP-256036
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256036', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 25, 0.1477, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 25, 0.1517, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.6882, 0.4134, 1);

    -- CIP CIP-256037
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256037', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.142, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.145, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.0261, 0.5189, 1);

    -- CIP CIP-256038
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256038', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.158, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1401, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.725, 0.9157, 1);

    -- CIP CIP-256039
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256039', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.146, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1381, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 5.6192, 0.3722, 1);

    -- CIP CIP-256040
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256040', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1274, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1521, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.1092, 0.2532, 1);

    -- CIP CIP-256041
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256041', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1297, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1436, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 8.5171, 0.5608, 1);

    -- CIP CIP-256042
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256042', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.1405, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.1328, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.208, 0.2711, 1);

    -- CIP CIP-256043
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente)
    VALUES ('CIP-256043', 'PAITITI', 'planta', 'Au', true)
    RETURNING id INTO v_analisis_id;

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO1', 15, 0.138, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'FINO2', 15, 0.142, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, numero_ensayo)
    VALUES (v_analisis_id, 'GRUESO', 7.2412, 0.2645, 1);

END $$;
