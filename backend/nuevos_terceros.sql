-- SQL INSERTS PARA NUEVOS TERCEROS
BEGIN;

-- Proveedor nuevo: SOTOMAYOR CORAZAO MORAYMA
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10421580605', 'SOTOMAYOR CORAZAO MORAYMA', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10421580605'), 7, true);
-- Proveedor nuevo: SOTOMAYOR CORAZAO WISTHERMUNDO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10416085884', 'SOTOMAYOR CORAZAO WISTHERMUNDO', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10416085884'), 7, true);
-- Proveedor nuevo: EXPLORACIONES CLAUDIA Y KAREN E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20601620147', 'EXPLORACIONES CLAUDIA Y KAREN E.I.R.L.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20601620147'), 7, true);
-- Proveedor nuevo: INVERSIONES Y SERVICIOS MULTIPLES SANTA LUCIA E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20610873309', 'INVERSIONES Y SERVICIOS MULTIPLES SANTA LUCIA E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20610873309'), 7, true);
-- Proveedor nuevo: INVERSIONES Y SERVICIOS MULTIPLES SANTA LUCÍA EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20610873309', 'INVERSIONES Y SERVICIOS MULTIPLES SANTA LUCÍA EIRL', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20610873309'), 7, true);
-- Proveedor nuevo: SOTOMAYOR PEÑA DERMILUZ
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10315432397', 'SOTOMAYOR PEÑA DERMILUZ', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10315432397'), 7, true);
-- Proveedor nuevo: SOTOMAYOR CORAZAO JHONATAN
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10473108823', 'SOTOMAYOR CORAZAO JHONATAN', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10473108823'), 7, true);
-- Proveedor nuevo: SOTOMAYOR CORAZAO JHONATHAN
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10473108823', 'SOTOMAYOR CORAZAO JHONATHAN', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10473108823'), 7, true);
-- Proveedor nuevo: MULTISERVICIOS Y Y NEGOCIACIONES ROGOHUA
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612275603', 'MULTISERVICIOS Y Y NEGOCIACIONES ROGOHUA', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612275603'), 7, true);
-- Proveedor nuevo: INV STEFANY EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20535021563', 'INV STEFANY EIRL', 'CONCESIÓN MINERA: EL INGE 2006-OTOCA-LUCANAS-AYACUCHO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20535021563'), 7, true);
-- Proveedor nuevo: BEDIA FERRO FELICIANO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10239291240', 'BEDIA FERRO FELICIANO', 'CONCESIÓN MINERA DELICIA - CURPAHUASI-GRAU-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10239291240'), 7, true);
-- Proveedor nuevo: PEÑA HUILLCARA GONZALO OLIVER
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10768340108', 'PEÑA HUILLCARA GONZALO OLIVER', 'CONCESIÓN MINERA: SA3002 - COLQUEMARCA-CHUMBIVILCAS-CUSCO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10768340108'), 7, true);
-- Proveedor nuevo: PELAYO VARGAS MIGUEL ANGEL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10770876970', 'PELAYO VARGAS MIGUEL ANGEL', 'CONCESIÓN MINERA: DELICIA - CURPAHUASI-GRAU-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10770876970'), 7, true);
-- Proveedor nuevo: MELCHOR AGUSTIN VERA PACHECO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10082235774', 'MELCHOR AGUSTIN VERA PACHECO', 'C.M. THE FUTURE AQP III LOS MOLLES', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10082235774'), 7, true);
-- Proveedor nuevo: COMPAÑÍA MINERA CIKAM PERU SAC
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20517242919', 'COMPAÑÍA MINERA CIKAM PERU SAC', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20517242919'), 7, true);
-- Proveedor nuevo: QUISPE MARTINEZ IZEQUIEL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10457401928', 'QUISPE MARTINEZ IZEQUIEL', 'CONCESIÓN MINERA: NUEVA ALICIA Nº 2 - PAMPACHIRI -ANDAHUAYLAS - APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10457401928'), 7, true);
-- Proveedor nuevo: TAMAYO BELLIDO ROBERTO CARLOS
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10761932735', 'TAMAYO BELLIDO ROBERTO CARLOS', 'CONCESIÓN MINERA: SAÑAICA I - PAMPACHIRI-ANDAHUAYLAS-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10761932735'), 7, true);
-- Proveedor nuevo: CHOCCARE HUAMANI JULIO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10408856049', 'CHOCCARE HUAMANI JULIO', 'CONCESIÓN MINERA: NUEVA ALICIA Nº 1 - SAÑAYCA-AYMARAES-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10408856049'), 7, true);
-- Proveedor nuevo: LLACCTEO GOLD E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606333219', 'LLACCTEO GOLD E.I.R.L', 'CONCESIÓN MINERA: DOMITILA I - EL ORO-ANTABAMBA-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606333219'), 7, true);
-- Proveedor nuevo: CALLER VALDERRAMA SERAPIO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10414969564', 'CALLER VALDERRAMA SERAPIO', 'CONCESIÓN MINERA: DOMITILA I - EL ORO-ANTABAMBA-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10414969564'), 7, true);
-- Proveedor nuevo: INVERSIONES QORI SONQO E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20613105621', 'INVERSIONES QORI SONQO E.I.R.L', 'CONCESIÓN MINERA: DOMITILA I - EL ORO-ANTABAMBA-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20613105621'), 7, true);
-- Proveedor nuevo: FLORES HUAMANI ROBERS
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10473594281', 'FLORES HUAMANI ROBERS', 'CONCESIÓN MINERA: CHAUPI 3 2017 - PAMPACHIRI-ANDAHUAYLAS-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10473594281'), 7, true);
-- Proveedor nuevo: MENDOZA CHALQUE WILLIAN
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10422176905', 'MENDOZA CHALQUE WILLIAN', 'CONCESIÓN MINERA: DOMITILA I - EL ORO-ANTABAMBA-APURIMAC', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10422176905'), 7, true);
-- Proveedor nuevo: MINERA SEBASTIAN E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20614635101', 'MINERA SEBASTIAN E.I.R.L.', 'CONCESIÓN MINERA MARIA AUXILIADORA - HUANUHUANU-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20614635101'), 7, true);
-- Proveedor nuevo: COMUNIDAD CAMPESINA DE UNTUCA
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20169040231', 'COMUNIDAD CAMPESINA DE UNTUCA', 'CONCESIÓN MINERA SAN MIGUEL DE UNTUCA -QUIACA-SANDIA-PUNO- C.U: 13006826X01', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20169040231'), 7, true);
-- Proveedor nuevo: MACC GOLD PERU EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20608774000', 'MACC GOLD PERU EIRL', 'CONCESIÓN MINERA ACUMULACION LOS ROSALES  - VILQUE-PUNO-PUNO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20608774000'), 7, true);
-- Proveedor nuevo: CORPORACIÓN SANTA NANCY EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20610807004', 'CORPORACIÓN SANTA NANCY EIRL', 'CONCESIÓN MINERA: MINA SANTA NANCY-CABANILLA-LAMPA-PUNO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20610807004'), 7, true);
-- Proveedor nuevo: EMPRESA MINERA SAYMED E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606562480', 'EMPRESA MINERA SAYMED E.I.R.L.', 'CONCESION MINERA: CERRO VERDE BL - PUNO - SANDIA - PHARA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606562480'), 7, true);
-- Proveedor nuevo: CONSORCIO MINERO RENACER DEL SUR E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20601769396', 'CONSORCIO MINERO RENACER DEL SUR E.I.R.L.', 'CONCESIÓN MINERA: COLONIA 1 - RIO GRANDE-CONDESUYOS-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20601769396'), 7, true);
-- Proveedor nuevo: MULTISERVICIOS Y MINERA HUANUHUANU E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612937096', 'MULTISERVICIOS Y MINERA HUANUHUANU E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612937096'), 7, true);
-- Proveedor nuevo: EXPLORACION G & M EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612719757', 'EXPLORACION G & M EIRL', 'CONCESIÓN MINERA:  JULISSA VI PULLO-PARINACOCHAS-AYACUCHO -CU 010198104', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612719757'), 7, true);
-- Proveedor nuevo: J_M SOLUCIONES MINERAS E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611329556', 'J_M SOLUCIONES MINERAS E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611329556'), 7, true);
-- Proveedor nuevo: MINERA CORDOVA FGA EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606102519', 'MINERA CORDOVA FGA EIRL', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606102519'), 7, true);
-- Proveedor nuevo: GRUPO EL CAZADOR GOLD E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606094010', 'GRUPO EL CAZADOR GOLD E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606094010'), 7, true);
-- Proveedor nuevo: GRUPO LINKOS NGLK E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611748486', 'GRUPO LINKOS NGLK E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611748486'), 7, true);
-- Proveedor nuevo: LIMBER EDISON MONTALVO QUISPE
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10479968131', 'LIMBER EDISON MONTALVO QUISPE', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10479968131'), 7, true);
-- Proveedor nuevo: EMPRESA MINERA MARKATA CAS S.A.C.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606526599', 'EMPRESA MINERA MARKATA CAS S.A.C.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606526599'), 7, true);
-- Proveedor nuevo: NEGOCIOS CARRILLO LANDA EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20604990000', 'NEGOCIOS CARRILLO LANDA EIRL', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20604990000'), 7, true);
-- Proveedor nuevo: MINERA PUAQ NAV E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611739509', 'MINERA PUAQ NAV E.I.R.L.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611739509'), 7, true);
-- Proveedor nuevo: MINERA DOS DE DICIEMBRE S.A. MIDDERSA
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20609542722', 'MINERA DOS DE DICIEMBRE S.A. MIDDERSA', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20609542722'), 7, true);
-- Proveedor nuevo: PIMENTEL BATALLANOS JUAN CRISOSTOMO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10306762465', 'PIMENTEL BATALLANOS JUAN CRISOSTOMO', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10306762465'), 7, true);
-- Proveedor nuevo: MINERA SOFI GOLD S.A.C.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20548542422', 'MINERA SOFI GOLD S.A.C.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20548542422'), 7, true);
-- Proveedor nuevo: NEGOCIOS CARRILLO LANDA E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20604990000', 'NEGOCIOS CARRILLO LANDA E.I.R.L.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20604990000'), 7, true);
-- Proveedor nuevo: MINERA CORDOVA FGA E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606102519', 'MINERA CORDOVA FGA E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606102519'), 7, true);
-- Proveedor nuevo: JRJAJN E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611000350', 'JRJAJN E.I.R.L.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611000350'), 7, true);
-- Proveedor nuevo: MENDOZA MENDOZA JULIO CESAR
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10756747652', 'MENDOZA MENDOZA JULIO CESAR', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10756747652'), 7, true);
-- Proveedor nuevo: MINERA HNOS DANEDCE MONTOYA E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20609578786', 'MINERA HNOS DANEDCE MONTOYA E.I.R.L.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20609578786'), 7, true);
-- Proveedor nuevo: HUAYHUA YUNQUE JOSE MELVIN
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10424767285', 'HUAYHUA YUNQUE JOSE MELVIN', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10424767285'), 7, true);
-- Proveedor nuevo: SAN ANDRES - CHALA GOLD MINING EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612791148', 'SAN ANDRES - CHALA GOLD MINING EIRL', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612791148'), 7, true);
-- Proveedor nuevo: AGUSTIN MENDIVIL VELASQUE
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10445192410', 'AGUSTIN MENDIVIL VELASQUE', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10445192410'), 7, true);
-- Proveedor nuevo: ACS MINERA KORICANCHAQ I E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20603329059', 'ACS MINERA KORICANCHAQ I E.I.R.L', 'KORI APUS I - APLAO-CASTILLA-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20603329059'), 7, true);
-- Proveedor nuevo: METAL EXTRACTION COMPANY S.A.C.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606527439', 'METAL EXTRACTION COMPANY S.A.C.', 'CONCESIÓN MINERA: TRACIA II - JAQUI-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606527439'), 7, true);
-- Proveedor nuevo: INVERSIONES MAMA COCO EIRL*
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20614284740', 'INVERSIONES MAMA COCO EIRL*', 'CONCESIÓN MINERA:  VANGUARDIA-HUANUHUANU-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20614284740'), 7, true);
-- Proveedor nuevo: GRUPO JEMALU E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20614031698', 'GRUPO JEMALU E.I.R.L.', 'CONCESIÓN ZORRO 5 - SANCOS-LUCANAS-AYACUCHO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20614031698'), 7, true);
-- Proveedor nuevo: MINERA LA VIRTUOSA DEL SUR E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606480840', 'MINERA LA VIRTUOSA DEL SUR E.I.R.L.', 'CONCESIÓN SAN ALEJANDRO I - MARIANO NICOLAS VALCARCEL-CAMANA-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606480840'), 7, true);
-- Proveedor nuevo: J & M SOLUCIONES MINERAS EIRL*
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611329556', 'J & M SOLUCIONES MINERAS EIRL*', 'CONCESIÓN SALCOCHA 101 - HUANUHUANU-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611329556'), 7, true);
-- Proveedor nuevo: INVERSIONES LAS GEMELAS LM E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20613170848', 'INVERSIONES LAS GEMELAS LM E.I.R.L.', 'CONCESIÓN POSCO-MARIANO NICOLAS VALCARCEL-CAMANA-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20613170848'), 7, true);
-- Proveedor nuevo: MINERA MARQUEZ NMU SERVICIOS MULTIPLES E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20603162812', 'MINERA MARQUEZ NMU SERVICIOS MULTIPLES E.I.R.L.', 'CONCESIÓN MINERA: LA MINA AS DE ORO-NASCA-NASCA-ICA - CODIGO UNICO 010110501', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20603162812'), 7, true);
-- Proveedor nuevo: INVERSIONES MANAURY F E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20609653036', 'INVERSIONES MANAURY F E.I.R.L.', 'CONCESION MINERA SANTA ROSA DE SOPHIA-OCAÑA-LUCANAS-AYACUCHO - C.U. 010022399', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20609653036'), 7, true);
-- Proveedor nuevo: GRUPO EMPRESARIAL FARFAN EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20614329646', 'GRUPO EMPRESARIAL FARFAN EIRL', 'CONCESION MINERA SANTIAGO 3-PAUSA-PAUCAR DEL SARA SARA-AYACUCHO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20614329646'), 7, true);
-- Proveedor nuevo: SERVICIOS GENERALES SAN ANDRES SH & T E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612223395', 'SERVICIOS GENERALES SAN ANDRES SH & T E.I.R.L.', 'CONCESION MINERA ISHIHUINCA- CARAVELI-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612223395'), 7, true);
-- Proveedor nuevo: INVERSIONES GENERALES PACHEKITO EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612554863', 'INVERSIONES GENERALES PACHEKITO EIRL', 'CONCESION MINERA ISHIHUINCA- CARAVELI-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612554863'), 7, true);
-- Proveedor nuevo: MAMANI SONCCO EDUARDO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10470098142', 'MAMANI SONCCO EDUARDO', 'CONCESION MINERA ISHIHUINCA- CARAVELI-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10470098142'), 7, true);
-- Proveedor nuevo: CORPORACIÓN SANTA NANCY E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20610807004', 'CORPORACIÓN SANTA NANCY E.I.R.L.', 'CONCESIÓN MINERA: MINA SANTA NANCY-CABANILLA-LAMPA-PUNO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20610807004'), 7, true);
-- Proveedor nuevo: MINERA CHAMACKA E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20613935151', 'MINERA CHAMACKA E.I.R.L.', 'CONCESIÓN MINERA: ADMIRABLE-HUANUHUANU-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20613935151'), 7, true);
-- Proveedor nuevo: INVERSIONES MAMA COCO EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20614284740', 'INVERSIONES MAMA COCO EIRL', 'CONCESIÓN MINERA: VANGUARDIA-HUANUHUANU-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20614284740'), 7, true);
-- Proveedor nuevo: PAUCARA INCACUTIPA OSMAR FREDY
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10404377324', 'PAUCARA INCACUTIPA OSMAR FREDY', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10404377324'), 7, true);
-- Proveedor nuevo: INVERMIN VOLCAL DEL SUR E.R.I.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20612137502', 'INVERMIN VOLCAL DEL SUR E.R.I.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20612137502'), 7, true);
-- Proveedor nuevo: JAWASA S.A. (AT)
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20601463173', 'JAWASA S.A. (AT)', 'JAWASA I -APLAO-CASTILLA-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20601463173'), 7, true);
-- Proveedor nuevo: ATAUCUSI ARIAS FRANK PAOLO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10486077447', 'ATAUCUSI ARIAS FRANK PAOLO', 'CONCESIÓN MINERA: EL REY NUEVO-CHAPARRA-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10486077447'), 7, true);
-- Proveedor nuevo: RETAMOZO ARIAS KARINA JUDITH
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10737057025', 'RETAMOZO ARIAS KARINA JUDITH', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10737057025'), 7, true);
-- Proveedor nuevo: INVERSIONES MAMA COCO E.I.R.L.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20614284740', 'INVERSIONES MAMA COCO E.I.R.L.', 'VANGUARDIA-HUANUHUANU-CARAVELI-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20614284740'), 7, true);
-- Proveedor nuevo: CRUCES CHIPANA CEFERINO EVARISTO
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10304932789', 'CRUCES CHIPANA CEFERINO EVARISTO', 'JULISSA VII-PULLO - PARINACOCHAS-AYACUCHO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10304932789'), 7, true);
-- Proveedor nuevo: CONSORCIO MINERO RENACER DEL SUR E.I.R.L.*
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20601769396', 'CONSORCIO MINERO RENACER DEL SUR E.I.R.L.*', 'CONCESION MINERO: COLONIA 1 - RIO GRANDE-CONDESUYOS-AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20601769396'), 7, true);
-- Proveedor nuevo: ENLACES MINEROS Y OBRAS CIVILES S.A.C
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20506072248', 'ENLACES MINEROS Y OBRAS CIVILES S.A.C', 'CON.MIN.MET.MARIA.LUZ.II.2006  - VITOR - AREQUIPA - AREQUIPA', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20506072248'), 7, true);
-- Proveedor nuevo: Valorizacion
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20000000001', 'Valorizacion', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20000000001'), 7, true);
-- Proveedor nuevo: CRUZ DE LA CRUZ DENNIS DARWIN
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10602688050', 'CRUZ DE LA CRUZ DENNIS DARWIN', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10602688050'), 7, true);
-- Proveedor nuevo: INVERSIONES LUCERO DE LOS ANDES E.I.R.L
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611795794', 'INVERSIONES LUCERO DE LOS ANDES E.I.R.L', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611795794'), 7, true);
-- Proveedor nuevo: LOPEZ ROCCA SANTOS
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10800995405', 'LOPEZ ROCCA SANTOS', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10800995405'), 7, true);
-- Proveedor nuevo: VISTA GOLD SAC
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20554057862', 'VISTA GOLD SAC', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20554057862'), 7, true);
-- Proveedor nuevo: CACERES RAMOS JESUS RUBEN
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('10403381361', 'CACERES RAMOS JESUS RUBEN', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '10403381361'), 7, true);
-- Proveedor nuevo: EMPRESA MINERA KHALEF EIRL
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20609745372', 'EMPRESA MINERA KHALEF EIRL', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20609745372'), 7, true);
-- Proveedor nuevo: ZICAMP S.A.C.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20606534923', 'ZICAMP S.A.C.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20606534923'), 7, true);
-- Proveedor nuevo: SAMANCO MINING S.A.C.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20611424541', 'SAMANCO MINING S.A.C.', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20611424541'), 7, true);
-- Proveedor nuevo: EXPLORER MINING APAZA S.A.C.
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20603169094', 'EXPLORER MINING APAZA S.A.C.', 'CONCESION MINERA: PAQUITA DOS 2004 VELILLE-CHUMBIVILCAS-CUSCO', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20603169094'), 7, true);
-- Proveedor nuevo: PEPAS
INSERT INTO entidades (ruc, razon_social, referencia, tipo, activo) VALUES ('20000000000', 'PEPAS', '', 'EMPRESA', true);
INSERT INTO entidades_roles (entidad_id, rol_id, activo) VALUES ((SELECT id FROM entidades WHERE ruc = '20000000000'), 7, true);

COMMIT;
