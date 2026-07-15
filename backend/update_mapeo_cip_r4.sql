USE paititi;
GO

BEGIN TRANSACTION;

ALTER TABLE analisis_recuperacion NOCHECK CONSTRAINT ALL;
ALTER TABLE analisis_ley NOCHECK CONSTRAINT ALL;

DECLARE @v_old_cip VARCHAR(50);

    -- IP-4108
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4108' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4108' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4108' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4108' WHERE cip = @v_old_cip;
    END

    -- IP-4109
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4109' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4109' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4109' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4109' WHERE cip = @v_old_cip;
    END

    -- IP-4110
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4110' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4110' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4110' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4110' WHERE cip = @v_old_cip;
    END

    -- IP-4111
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4111' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4111' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4111' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4111' WHERE cip = @v_old_cip;
    END

    -- IP-4112
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4112' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4112' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4112' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4112' WHERE cip = @v_old_cip;
    END

    -- IP-4113
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4113' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4113' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4113' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4113' WHERE cip = @v_old_cip;
    END

    -- IP-4114
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4114' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4114' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4114' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4114' WHERE cip = @v_old_cip;
    END

    -- IP-4115
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4115' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4115' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4115' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4115' WHERE cip = @v_old_cip;
    END

    -- IP-4116
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4116' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4116' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4116' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4116' WHERE cip = @v_old_cip;
    END

    -- IP-4117
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4117' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4117' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4117' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4117' WHERE cip = @v_old_cip;
    END

    -- IP-4118
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4118' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4118' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4118' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4118' WHERE cip = @v_old_cip;
    END

    -- IP-4119
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4119' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4119' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4119' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4119' WHERE cip = @v_old_cip;
    END

    -- IP-4120
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4120' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4120' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4120' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4120' WHERE cip = @v_old_cip;
    END

    -- IP-4121
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4121' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4121' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4121' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4121' WHERE cip = @v_old_cip;
    END

    -- IP-4122
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4122' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4122' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4122' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4122' WHERE cip = @v_old_cip;
    END

    -- IP-4103
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4103' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4103' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4103' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4103' WHERE cip = @v_old_cip;
    END

    -- IP-4124
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4124' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4124' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4124' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4124' WHERE cip = @v_old_cip;
    END

    -- IP-4123
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4123' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4123' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4123' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4123' WHERE cip = @v_old_cip;
    END

    -- IP-4125
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4125' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4125' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4125' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4125' WHERE cip = @v_old_cip;
    END

    -- IP-4126
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4126' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4126' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4126' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4126' WHERE cip = @v_old_cip;
    END

    -- IP-4127
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4127' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4127' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4127' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4127' WHERE cip = @v_old_cip;
    END

    -- IP-4128
    SET @v_old_cip = NULL;
    SELECT @v_old_cip = m.codigo_cip
    FROM mapeo_cip m
    JOIN lotes l ON m.lote_id = l.id
    WHERE l.ip = 'IP-4128' AND (m.codigo_cip LIKE 'R4%' OR m.tipo_muestra LIKE 'RECUPERACION%');

    IF @v_old_cip IS NOT NULL
    BEGIN
        UPDATE mapeo_cip SET codigo_cip = 'IP-4128' WHERE codigo_cip = @v_old_cip;
        UPDATE analisis_recuperacion SET cip = 'IP-4128' WHERE cip = @v_old_cip;
        UPDATE analisis_ley SET cip = 'IP-4128' WHERE cip = @v_old_cip;
    END

ALTER TABLE analisis_recuperacion CHECK CONSTRAINT ALL;
ALTER TABLE analisis_ley CHECK CONSTRAINT ALL;

COMMIT TRANSACTION;
