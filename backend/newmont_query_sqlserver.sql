DECLARE @v_analisis_id INT;
BEGIN TRANSACTION;

    -- CIP CIP-256000
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256000', 'PAITITI', 'planta', 'Au', 1, 0.3300, 0.1990, 0.5291);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1753, 0.3291, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1763, 0.3310, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 6.9078, 1.3647, 0.1990, 1);

    -- CIP CIP-256001
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256001', 'PAITITI', 'planta', 'Au', 1, 0.2105, 0.3660, 0.5765);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1086, 0.2030, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1166, 0.2179, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.7550, 2.5100, 0.3660, 1);

    -- CIP CIP-256002
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256002', 'PAITITI', 'planta', 'Au', 1, 0.2248, 0.3068, 0.5317);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1259, 0.2351, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1149, 0.2146, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.9175, 2.1038, 0.3068, 1);

    -- CIP CIP-256003
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256003', 'PAITITI', 'planta', 'Au', 1, 0.1274, 0.1022, 0.2296);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0684, 0.1275, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0683, 0.1273, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.3184, 0.7008, 0.1022, 1);

    -- CIP CIP-256004
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256004', 'PAITITI', 'planta', 'Au', 1, 0.1288, 0.1277, 0.2565);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0715, 0.1340, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0660, 0.1237, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.2899, 0.8755, 0.1277, 1);

    -- CIP CIP-256005
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256005', 'PAITITI', 'planta', 'Au', 1, 0.1255, 0.0733, 0.1988);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0664, 0.1246, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0674, 0.1264, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.0670, 0.5029, 0.0733, 1);

    -- CIP CIP-256006
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256006', 'PAITITI', 'planta', 'Au', 1, 0.1170, 0.0910, 0.2080);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0631, 0.1178, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0622, 0.1161, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.9489, 0.6238, 0.0910, 1);

    -- CIP CIP-256007
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256007', 'PAITITI', 'planta', 'Au', 1, 0.1308, 0.0040, 0.1348);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0715, 0.1328, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0693, 0.1287, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.9660, 0.0274, 0.0040, 1);

    -- CIP CIP-256008
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256008', 'PAITITI', 'planta', 'Au', 1, 0.1362, 0.0044, 0.1406);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0757, 0.1415, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0700, 0.1309, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.6956, 0.0299, 0.0044, 1);

    -- CIP CIP-256009
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256009', 'PAITITI', 'planta', 'Au', 1, 0.3653, 0.0457, 0.4110);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1896, 0.3570, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1984, 0.3735, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 6.3487, 0.3136, 0.0457, 1);

    -- CIP CIP-256010
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256010', 'PAITITI', 'planta', 'Au', 1, 0.3536, 0.0506, 0.4042);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1940, 0.3624, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1846, 0.3448, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.8707, 0.3469, 0.0506, 1);

    -- CIP CIP-256011
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256011', 'PAITITI', 'planta', 'Au', 1, 0.1278, 0.0064, 0.1343);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0686, 0.1277, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0687, 0.1279, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.4732, 0.0442, 0.0064, 1);

    -- CIP CIP-256012
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256012', 'PAITITI', 'planta', 'Au', 1, 0.1287, 0.0050, 0.1338);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0652, 0.1220, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0724, 0.1355, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.5253, 0.0346, 0.0050, 1);

    -- CIP CIP-256013
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256013', 'PAITITI', 'planta', 'Au', 1, 0.3113, 0.0121, 0.3233);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1625, 0.3038, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1705, 0.3188, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.7038, 0.0827, 0.0121, 1);

    -- CIP CIP-256014
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256014', 'PAITITI', 'planta', 'Au', 1, 0.3241, 0.0113, 0.3354);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1759, 0.3285, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1712, 0.3197, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.9405, 0.0775, 0.0113, 1);

    -- CIP CIP-256015
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256015', 'PAITITI', 'planta', 'Au', 1, 0.1992, 0.0188, 0.2179);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1066, 0.1987, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1071, 0.1996, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.2894, 0.1286, 0.0188, 1);

    -- CIP CIP-256016
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256016', 'PAITITI', 'planta', 'Au', 1, 0.1976, 0.0187, 0.2164);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1037, 0.1921, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1097, 0.2032, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 9.4885, 0.1285, 0.0187, 1);

    -- CIP CIP-256017
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256017', 'PAITITI', 'planta', 'Au', 1, 0.2015, 0.0176, 0.2192);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1032, 0.1918, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1137, 0.2113, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.8827, 0.1210, 0.0176, 1);

    -- CIP CIP-256018
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256018', 'PAITITI', 'planta', 'Au', 1, 0.1852, 0.0246, 0.2099);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0994, 0.1858, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0988, 0.1847, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.7379, 0.1689, 0.0246, 1);

    -- CIP CIP-256019
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256019', 'PAITITI', 'planta', 'Au', 1, 0.1879, 0.0208, 0.2087);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1018, 0.1898, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0998, 0.1860, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.2596, 0.1427, 0.0208, 1);

    -- CIP CIP-256020
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256020', 'PAITITI', 'planta', 'Au', 1, 0.1885, 0.0148, 0.2033);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1046, 0.1947, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0979, 0.1823, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.5044, 0.1013, 0.0148, 1);

    -- CIP CIP-256021
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256021', 'PAITITI', 'planta', 'Au', 1, 0.6037, 0.1311, 0.7348);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.3244, 0.6074, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.3204, 0.5999, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.4048, 0.8991, 0.1311, 1);

    -- CIP CIP-256022
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256022', 'PAITITI', 'planta', 'Au', 1, 0.5592, 0.1736, 0.7328);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.2994, 0.5574, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.3014, 0.5611, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.5274, 1.1904, 0.1736, 1);

    -- CIP CIP-256023
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256023', 'PAITITI', 'planta', 'Au', 1, 0.3953, 0.0355, 0.4308);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.2100, 0.3938, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.2116, 0.3968, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.1151, 0.2433, 0.0355, 1);

    -- CIP CIP-256024
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256024', 'PAITITI', 'planta', 'Au', 1, 0.3726, 0.0590, 0.4316);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.2110, 0.3911, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1910, 0.3541, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 9.3394, 0.4049, 0.0590, 1);

    -- CIP CIP-256025
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256025', 'PAITITI', 'planta', 'Au', 1, 0.8837, 0.0918, 0.9755);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.4566, 0.8647, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.4767, 0.9027, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 5.2235, 0.6293, 0.0918, 1);

    -- CIP CIP-256026
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256026', 'PAITITI', 'planta', 'Au', 1, 0.8269, 0.1295, 0.9565);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.4310, 0.8109, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.4481, 0.8430, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 6.4940, 0.8883, 0.1295, 1);

    -- CIP CIP-256027
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256027', 'PAITITI', 'planta', 'Au', 1, 0.2614, 0.0836, 0.3449);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1453, 0.2717, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1342, 0.2510, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.6391, 0.5730, 0.0836, 1);

    -- CIP CIP-256028
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256028', 'PAITITI', 'planta', 'Au', 1, 0.2565, 0.0635, 0.3201);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1352, 0.2520, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1400, 0.2610, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.2600, 0.4357, 0.0635, 1);

    -- CIP CIP-256029
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256029', 'PAITITI', 'planta', 'Au', 1, 0.1450, 0.0892, 0.2343);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.0867, 0.1637, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.0669, 0.1263, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 5.7622, 0.6119, 0.0892, 1);

    -- CIP CIP-256030
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256030', 'PAITITI', 'planta', 'Au', 1, 0.9595, 0.0279, 0.9874);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.5008, 0.9483, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.5127, 0.9708, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 5.2414, 0.1911, 0.0279, 1);

    -- CIP CIP-256031
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256031', 'PAITITI', 'planta', 'Au', 1, 0.9116, 0.0518, 0.9634);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.4856, 0.9041, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.4936, 0.9190, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.4965, 0.3552, 0.0518, 1);

    -- CIP CIP-256032
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256032', 'PAITITI', 'planta', 'Au', 1, 0.2564, 0.1306, 0.3869);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1412, 0.2581, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1393, 0.2546, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 11.9955, 0.8954, 0.1306, 1);

    -- CIP CIP-256033
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256033', 'PAITITI', 'planta', 'Au', 1, 0.2663, 0.0990, 0.3653);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1433, 0.2620, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1480, 0.2706, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 11.9601, 0.6791, 0.0990, 1);

    -- CIP CIP-256034
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256034', 'PAITITI', 'planta', 'Au', 1, 0.2750, 0.1259, 0.4009);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1535, 0.2840, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1437, 0.2659, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 9.6884, 0.8633, 0.1259, 1);

    -- CIP CIP-256035
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256035', 'PAITITI', 'planta', 'Au', 1, 0.2821, 0.0716, 0.3537);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1426, 0.2655, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1604, 0.2987, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.4848, 0.4908, 0.0716, 1);

    -- CIP CIP-256036
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256036', 'PAITITI', 'planta', 'Au', 1, 0.2784, 0.0603, 0.3387);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1477, 0.2747, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1517, 0.2822, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.6882, 0.4134, 0.0603, 1);

    -- CIP CIP-256037
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256037', 'PAITITI', 'planta', 'Au', 1, 0.2687, 0.0757, 0.3444);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1429, 0.2667, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1450, 0.2706, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.0261, 0.5189, 0.0757, 1);

    -- CIP CIP-256038
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256038', 'PAITITI', 'planta', 'Au', 1, 0.2772, 0.1335, 0.4107);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1580, 0.2938, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1401, 0.2605, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.7250, 0.9157, 0.1335, 1);

    -- CIP CIP-256039
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256039', 'PAITITI', 'planta', 'Au', 1, 0.2685, 0.0543, 0.3227);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1460, 0.2759, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1381, 0.2610, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 5.6192, 0.3722, 0.0543, 1);

    -- CIP CIP-256040
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256040', 'PAITITI', 'planta', 'Au', 1, 0.2713, 0.1244, 0.3958);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1374, 0.2576, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1521, 0.2851, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.1992, 0.8532, 0.1244, 1);

    -- CIP CIP-256041
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256041', 'PAITITI', 'planta', 'Au', 1, 0.2544, 0.0818, 0.3362);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1297, 0.2415, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1436, 0.2673, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 8.5171, 0.5608, 0.0818, 1);

    -- CIP CIP-256042
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256042', 'PAITITI', 'planta', 'Au', 1, 0.2618, 0.0395, 0.3013);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1465, 0.2746, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1328, 0.2489, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.2080, 0.2711, 0.0395, 1);

    -- CIP CIP-256043
    INSERT INTO analisis_ley (cip, laboratorio, tipo_analisis, material, vigente, ley_fino, ley_grueso, ley_final)
    VALUES ('CIP-256043', 'PAITITI', 'planta', 'Au', 1, 0.2622, 0.0386, 0.3008);
    SET @v_analisis_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO1', 15.0000, 0.1380, 0.2585, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'FINO2', 15.0000, 0.1420, 0.2660, 1);

    INSERT INTO analisis_detalle (analisis_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_analisis_id, 'GRUESO', 7.3443, 0.2645, 0.0386, 1);

COMMIT TRANSACTION;
