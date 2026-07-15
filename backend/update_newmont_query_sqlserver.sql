DECLARE @v_analisis_id INT;
BEGIN TRANSACTION;

    -- CIP CIP-256000
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3300, 
        ley_grueso = 0.1990, 
        ley_final = 0.5291, 
        ley_gr_tm = 18.139, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256000'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256000' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256000' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3291
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3310
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1990
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256001
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2105, 
        ley_grueso = 0.3660, 
        ley_final = 0.5765, 
        ley_gr_tm = 19.766, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256001'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256001' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256001' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2030
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2179
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.3660
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256002
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2248, 
        ley_grueso = 0.3068, 
        ley_final = 0.5317, 
        ley_gr_tm = 18.228, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256002'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256002' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256002' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2351
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2146
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.3068
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256003
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1274, 
        ley_grueso = 0.1022, 
        ley_final = 0.2296, 
        ley_gr_tm = 7.871, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256003'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256003' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256003' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1275
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1273
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1022
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256004
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1288, 
        ley_grueso = 0.1277, 
        ley_final = 0.2565, 
        ley_gr_tm = 8.794, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256004'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256004' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256004' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1340
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1237
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1277
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256005
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1255, 
        ley_grueso = 0.0733, 
        ley_final = 0.1988, 
        ley_gr_tm = 6.817, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256005'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256005' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256005' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1246
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1264
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0733
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256006
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1170, 
        ley_grueso = 0.0910, 
        ley_final = 0.2080, 
        ley_gr_tm = 7.130, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256006'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256006' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256006' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1178
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1161
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0910
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256007
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1308, 
        ley_grueso = 0.0040, 
        ley_final = 0.1348, 
        ley_gr_tm = 4.620, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256007'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256007' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256007' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1328
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1287
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0040
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256008
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1362, 
        ley_grueso = 0.0044, 
        ley_final = 0.1406, 
        ley_gr_tm = 4.819, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256008'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256008' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256008' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1415
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1309
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0044
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256009
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3653, 
        ley_grueso = 0.0457, 
        ley_final = 0.4110, 
        ley_gr_tm = 14.091, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256009'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256009' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256009' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3570
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3735
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0457
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256010
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3536, 
        ley_grueso = 0.0506, 
        ley_final = 0.4042, 
        ley_gr_tm = 13.858, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256010'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256010' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256010' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3624
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3448
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0506
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256011
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1278, 
        ley_grueso = 0.0064, 
        ley_final = 0.1343, 
        ley_gr_tm = 4.604, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256011'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256011' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256011' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1277
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1279
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0064
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256012
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1287, 
        ley_grueso = 0.0050, 
        ley_final = 0.1338, 
        ley_gr_tm = 4.587, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256012'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256012' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256012' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1220
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1355
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0050
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256013
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3113, 
        ley_grueso = 0.0121, 
        ley_final = 0.3233, 
        ley_gr_tm = 11.086, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256013'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256013' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256013' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3038
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3188
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0121
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256014
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3241, 
        ley_grueso = 0.0113, 
        ley_final = 0.3354, 
        ley_gr_tm = 11.498, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256014'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256014' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256014' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3285
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3197
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0113
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256015
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1992, 
        ley_grueso = 0.0188, 
        ley_final = 0.2179, 
        ley_gr_tm = 7.471, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256015'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256015' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256015' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1987
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1996
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0188
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256016
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1976, 
        ley_grueso = 0.0187, 
        ley_final = 0.2164, 
        ley_gr_tm = 7.419, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256016'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256016' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256016' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1921
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2032
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0187
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256017
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2015, 
        ley_grueso = 0.0176, 
        ley_final = 0.2192, 
        ley_gr_tm = 7.514, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256017'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256017' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256017' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1918
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2113
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0176
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256018
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1852, 
        ley_grueso = 0.0246, 
        ley_final = 0.2099, 
        ley_gr_tm = 7.196, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256018'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256018' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256018' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1858
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1847
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0246
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256019
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1879, 
        ley_grueso = 0.0208, 
        ley_final = 0.2087, 
        ley_gr_tm = 7.156, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256019'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256019' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256019' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1898
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1860
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0208
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256020
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1885, 
        ley_grueso = 0.0148, 
        ley_final = 0.2033, 
        ley_gr_tm = 6.970, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256020'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256020' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256020' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1947
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1823
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0148
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256021
    UPDATE analisis_ley
    SET 
        ley_fino = 0.6037, 
        ley_grueso = 0.1311, 
        ley_final = 0.7348, 
        ley_gr_tm = 25.194, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256021'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256021' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256021' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.6074
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.5999
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1311
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256022
    UPDATE analisis_ley
    SET 
        ley_fino = 0.5592, 
        ley_grueso = 0.1736, 
        ley_final = 0.7328, 
        ley_gr_tm = 25.125, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256022'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256022' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256022' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.5574
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.5611
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1736
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256023
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3953, 
        ley_grueso = 0.0355, 
        ley_final = 0.4308, 
        ley_gr_tm = 14.770, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256023'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256023' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256023' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3938
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3968
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0355
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256024
    UPDATE analisis_ley
    SET 
        ley_fino = 0.3726, 
        ley_grueso = 0.0590, 
        ley_final = 0.4316, 
        ley_gr_tm = 14.799, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256024'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256024' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256024' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.3911
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.3541
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0590
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256025
    UPDATE analisis_ley
    SET 
        ley_fino = 0.8837, 
        ley_grueso = 0.0918, 
        ley_final = 0.9755, 
        ley_gr_tm = 33.445, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256025'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256025' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256025' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.8647
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.9027
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0918
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256026
    UPDATE analisis_ley
    SET 
        ley_fino = 0.8269, 
        ley_grueso = 0.1295, 
        ley_final = 0.9565, 
        ley_gr_tm = 32.794, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256026'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256026' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256026' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.8109
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.8430
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1295
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256027
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2614, 
        ley_grueso = 0.0836, 
        ley_final = 0.3449, 
        ley_gr_tm = 11.826, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256027'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256027' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256027' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2717
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2510
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0836
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256028
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2565, 
        ley_grueso = 0.0635, 
        ley_final = 0.3201, 
        ley_gr_tm = 10.973, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256028'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256028' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256028' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2520
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2610
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0635
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256029
    UPDATE analisis_ley
    SET 
        ley_fino = 0.1450, 
        ley_grueso = 0.0892, 
        ley_final = 0.2343, 
        ley_gr_tm = 8.032, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256029'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256029' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256029' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.1637
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.1263
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0892
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256030
    UPDATE analisis_ley
    SET 
        ley_fino = 0.9595, 
        ley_grueso = 0.0279, 
        ley_final = 0.9874, 
        ley_gr_tm = 33.854, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256030'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256030' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256030' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.9483
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.9708
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0279
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256031
    UPDATE analisis_ley
    SET 
        ley_fino = 0.9116, 
        ley_grueso = 0.0518, 
        ley_final = 0.9634, 
        ley_gr_tm = 33.030, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256031'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256031' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256031' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.9041
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.9190
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0518
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256032
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2564, 
        ley_grueso = 0.1306, 
        ley_final = 0.3869, 
        ley_gr_tm = 13.266, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256032'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256032' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256032' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2581
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2546
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1306
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256033
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2663, 
        ley_grueso = 0.0990, 
        ley_final = 0.3653, 
        ley_gr_tm = 12.525, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256033'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256033' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256033' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2620
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2706
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0990
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256034
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2750, 
        ley_grueso = 0.1259, 
        ley_final = 0.4009, 
        ley_gr_tm = 13.744, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256034'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256034' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256034' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2840
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2659
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1259
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256035
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2821, 
        ley_grueso = 0.0716, 
        ley_final = 0.3537, 
        ley_gr_tm = 12.126, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256035'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256035' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256035' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2655
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2987
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0716
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256036
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2784, 
        ley_grueso = 0.0603, 
        ley_final = 0.3387, 
        ley_gr_tm = 11.614, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256036'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256036' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256036' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2747
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2822
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0603
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256037
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2687, 
        ley_grueso = 0.0757, 
        ley_final = 0.3444, 
        ley_gr_tm = 11.806, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256037'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256037' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256037' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2667
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2706
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0757
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256038
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2772, 
        ley_grueso = 0.1335, 
        ley_final = 0.4107, 
        ley_gr_tm = 14.082, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256038'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256038' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256038' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2938
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2605
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1335
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256039
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2685, 
        ley_grueso = 0.0543, 
        ley_final = 0.3227, 
        ley_gr_tm = 11.065, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256039'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256039' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256039' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2759
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2610
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0543
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256040
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2713, 
        ley_grueso = 0.1244, 
        ley_final = 0.3958, 
        ley_gr_tm = 13.569, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256040'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256040' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256040' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2576
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2851
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.1244
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256041
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2544, 
        ley_grueso = 0.0818, 
        ley_final = 0.3362, 
        ley_gr_tm = 11.526, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256041'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256041' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256041' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2415
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2673
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0818
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256042
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2618, 
        ley_grueso = 0.0395, 
        ley_final = 0.3013, 
        ley_gr_tm = 10.330, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256042'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256042' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256042' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2746
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2489
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0395
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

    -- CIP CIP-256043
    UPDATE analisis_ley
    SET 
        ley_fino = 0.2622, 
        ley_grueso = 0.0386, 
        ley_final = 0.3008, 
        ley_gr_tm = 10.313, 
        lote_id = (SELECT TOP 1 lote_id FROM mapeo_cip WHERE codigo_cip = 'CIP-256043'),
        fecha_analisis = ISNULL(fecha_analisis, GETDATE())
    WHERE cip = 'CIP-256043' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    SELECT @v_analisis_id = id FROM analisis_ley WHERE cip = 'CIP-256043' AND laboratorio = 'PAITITI' AND tipo_analisis = 'planta' AND material = 'Au' AND vigente = 1;

    UPDATE analisis_detalle
    SET ley = 0.2585
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO1';

    UPDATE analisis_detalle
    SET ley = 0.2660
    WHERE analisis_id = @v_analisis_id AND origen = 'FINO2';

    UPDATE analisis_detalle
    SET ley = 0.0386
    WHERE analisis_id = @v_analisis_id AND origen = 'GRUESO';

COMMIT TRANSACTION;
