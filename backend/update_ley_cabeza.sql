USE paititi;
GO

BEGIN TRANSACTION;

UPDATE r
SET r.ley_cabeza = sub.ley_promedio
FROM analisis_recuperacion r
INNER JOIN (
    SELECT lote_id, ROUND(AVG(ley_final), 3) AS ley_promedio
    FROM analisis_ley
    WHERE vigente = 1 AND tipo_analisis IN ('planta', 'externo') AND material = 'Au'
    GROUP BY lote_id
) sub ON r.lote_id = sub.lote_id
WHERE r.ley_cabeza IS NULL AND r.lote_id IS NOT NULL;

COMMIT TRANSACTION;
