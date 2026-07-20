USE paititi;
GO

DECLARE @v_recuperacion_id INT;
BEGIN TRANSACTION;

    -- IP-4108
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4108', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0268, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4108';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0230, 0.9200, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0230, 0.9200, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4109
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4109', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0162, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4109';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0139, 0.5560, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0139, 0.5560, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4110
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4110', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0149, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4110';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0128, 0.5120, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0128, 0.5120, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4111
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4111', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0163, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4111';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0140, 0.5600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0140, 0.5600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4112
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4112', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.3656, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4112';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.3134, 12.5360, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.3134, 12.5360, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4113
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4113', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0196, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4113';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0168, 0.6720, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0168, 0.6720, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4114
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4114', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0197, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4114';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0169, 0.6760, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0169, 0.6760, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4115
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4115', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0149, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4115';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0128, 0.5120, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0128, 0.5120, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4116
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4116', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0138, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4116';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0118, 0.4720, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0118, 0.4720, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4117
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4117', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0081, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4117';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0069, 0.2760, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0069, 0.2760, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4118
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4118', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0184, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4118';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0158, 0.6320, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0158, 0.6320, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4119
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4119', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0041, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4119';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 30.0000, 0.0042, 0.1400, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 30.0000, 0.0042, 0.1400, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 30.0000, 0.0000, 0.0000, 1);

    -- IP-4120
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4120', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0051, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4120';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0044, 0.1760, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0044, 0.1760, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4121
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4121', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0082, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4121';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0070, 0.2800, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0070, 0.2800, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4122
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4122', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0058, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4122';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0050, 0.2000, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0050, 0.2000, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4103
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4103', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0508, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4103';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 30.0000, 0.0522, 1.7400, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 30.0000, 0.0522, 1.7400, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 30.0000, 0.0000, 0.0000, 1);

    -- IP-4124
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4124', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0119, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4124';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0102, 0.4080, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0102, 0.4080, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4123
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4123', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0163, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4123';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0140, 0.5600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0140, 0.5600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4125
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4125', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0119, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4125';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0102, 0.4080, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0102, 0.4080, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4126
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4126', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0105, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4126';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0090, 0.3600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0090, 0.3600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4127
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4127', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0134, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4127';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0115, 0.4600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0115, 0.4600, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

    -- IP-4128
    INSERT INTO analisis_recuperacion (lote_id, cip, laboratorio, estado, sub_tipo, origen_datos, ley_cola, vigente, fecha_analisis)
    SELECT TOP 1 id, 'IP-4128', 'PAITITI', 'COMPLETADO', 'SOLIDOS', 'manual', 0.0082, 1, GETDATE()
    FROM lotes WHERE ip = 'IP-4128';

    SET @v_recuperacion_id = SCOPE_IDENTITY();

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU1', 25.0000, 0.0070, 0.2800, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU2', 25.0000, 0.0070, 0.2800, 1);

    INSERT INTO analisis_detalle (recuperacion_id, origen, peso, mineral_mg, ley, numero_ensayo)
    VALUES (@v_recuperacion_id, 'AU_AG', 25.0000, 0.0000, 0.0000, 1);

COMMIT TRANSACTION;
