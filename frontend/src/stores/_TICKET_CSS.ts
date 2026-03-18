export const _TICKET_CSS = `
/* ── Pantalla: vista previa con fondo blanco ─────────────── */
@media screen {
  html, body {
    background: #e0e0e0;
    margin: 0;
    padding: 20px;
  }
  .ticket-page {
    background: #fff;
    width: 210mm;
    min-height: 148mm;
    margin: 0 auto;
    padding: 1.0cm 1.5cm 0.8cm 1.5cm;
    box-shadow: 0 2px 12px rgba(0,0,0,.25);
    box-sizing: border-box;
  }
}

/* ── Impresión: A5 landscape exacto ─────────────────────── */
@media print {
  @page {
    size: A5 landscape;
    margin: 1.0cm 1.5cm 0.8cm 1.5cm;
  }
  html, body {
    margin: 0;
    padding: 0;
    background: #fff;
    width: 210mm;
    height: 148mm;
  }
  .ticket-page {
    width: 100%;
    padding: 0;
    box-shadow: none;
  }
  .ticket { page-break-after: always; break-after: page; }
  .ticket:last-child { page-break-after: avoid; break-after: avoid; }
}

/* ── Contenido (igual que ticket_balanza.html del servidor) ─ */
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Courier New', Courier, monospace;
  font-size: 9.5pt;
  color: #000;
  line-height: 1.55;
}
.emp-nombre { font-size: 13pt; font-weight: bold; }
.emp-sub    { font-size: 9pt; }
.hr { border: none; border-top: 1px solid #000; margin: 4px 0; }
.fila-placa { width: 100%; border-collapse: collapse; }
.fila-placa td { padding: 0; vertical-align: middle; }
.td-placa { font-size: 9.5pt; }
.td-ticket { text-align: right; font-size: 11pt; font-weight: bold; white-space: nowrap; }
.datos { width: 100%; border-collapse: collapse; }
.datos td { padding: 0; vertical-align: top; font-size: 9.5pt; line-height: 1.5; }
.lbl { width: 100px; white-space: nowrap; }
.sep { width: 10px; }
.seccion { width: 100%; border-collapse: collapse; margin-top: 1px; }
.seccion td { vertical-align: top; padding: 0; }
.col-fechas { width: 54%; }
.col-pesos  { width: 46%; }
.tabla-pesos { width: 100%; border-collapse: collapse; }
.tabla-pesos td { padding: 0; font-size: 9.5pt; line-height: 1.5; }
.p-sep { width: 10px; }
.p-val { text-align: right; font-size: 12pt; font-weight: bold; padding-right: 2px; }
.p-neto { font-size: 13.5pt; }
.p-unit { font-size: 8pt; white-space: nowrap; }
`;

export const _TICKET_CSS_MULTI = `
/* ── Pantalla: tarjetas apiladas para previsualizar ─────── */
@media screen {
  html, body { background: #e0e0e0; margin: 0; padding: 20px; }
  .ticket { margin-bottom: 16px; }
  .ticket-page {
    background: #fff;
    width: 210mm;
    min-height: 148mm;
    margin: 0 auto;
    padding: 1.0cm 1.5cm 0.8cm 1.5cm;
    box-shadow: 0 2px 12px rgba(0,0,0,.25);
    box-sizing: border-box;
  }
}

/* ── Impresión: A4 portrait — 2 tickets por hoja ────────── */
@media print {
  @page { size: A4 portrait; margin: 5mm 8mm; }
  html, body { margin: 0; padding: 0; background: #fff; }
  .ticket {
    height: 143mm;
    page-break-inside: avoid;
    break-inside: avoid;
  }
  .ticket:nth-child(2n)    { page-break-after: always; break-after: page; }
  .ticket:last-child       { page-break-after: avoid;  break-after: avoid; }
  .ticket-page {
    width: 100%;
    height: 140mm;
    overflow: hidden;
    padding: 3mm 0 0 0;
    box-shadow: none;
    box-sizing: border-box;
  }
}

/* ── Contenido (igual que _TICKET_CSS) ─────────────────── */
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Courier New', Courier, monospace; font-size: 9.5pt; color: #000; line-height: 1.55; }
.emp-nombre { font-size: 13pt; font-weight: bold; }
.emp-sub    { font-size: 9pt; }
.hr { border: none; border-top: 1px solid #000; margin: 4px 0; }
.fila-placa { width: 100%; border-collapse: collapse; }
.fila-placa td { padding: 0; vertical-align: middle; }
.td-placa  { font-size: 9.5pt; }
.td-ticket { text-align: right; font-size: 11pt; font-weight: bold; white-space: nowrap; }
.datos { width: 100%; border-collapse: collapse; }
.datos td { padding: 0; vertical-align: top; font-size: 9.5pt; line-height: 1.5; }
.lbl { width: 100px; white-space: nowrap; }
.sep { width: 10px; }
.seccion { width: 100%; border-collapse: collapse; margin-top: 1px; }
.seccion td { vertical-align: top; padding: 0; }
.col-fechas { width: 54%; }
.col-pesos  { width: 46%; }
.tabla-pesos { width: 100%; border-collapse: collapse; }
.tabla-pesos td { padding: 0; font-size: 9.5pt; line-height: 1.5; }
.p-sep { width: 10px; }
.p-val { text-align: right; font-size: 12pt; font-weight: bold; padding-right: 2px; }
.p-neto { font-size: 13.5pt; }
.p-unit { font-size: 8pt; white-space: nowrap; }
`
