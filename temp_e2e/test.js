import puppeteer from 'puppeteer';

(async () => {
    console.log("Iniciando prueba e2e...");
    const browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();
    
    try {
        console.log("1. Navegando a localhost:5173");
        await page.goto('http://localhost:5173', { waitUntil: 'networkidle2' });
        
        console.log("2. Verificando redirección a login...");
        await page.waitForSelector('input[type="text"]', { timeout: 5000 });
        
        console.log("3. Iniciando sesión con operador1...");
        const inputs = await page.$$('input');
        if(inputs.length >= 2) {
            await inputs[0].type('operador1');
            await inputs[1].type('operador1234');
            const buttons = await page.$$('button');
            for(let btn of buttons) {
                const text = await page.evaluate(el => el.textContent, btn);
                if(text.toLowerCase().includes('iniciar') || text.toLowerCase().includes('login')) {
                    await btn.click();
                    break;
                }
            }
        }
        
        // Wait for login to complete
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => console.log("No hubo evento de navegación, esperando selectores..."));
        
        console.log("4. Sesión iniciada. Verificando UI...");
        const html = await page.content();
        if(html.toLowerCase().includes('error')) {
            console.log("⚠️ Hubo un error de inicio de sesión o UI.");
        } else {
            console.log("✅ Inicio de sesión exitoso.");
        }

        console.log("5. Simulando modo Offline...");
        await page.setOfflineMode(true);
        console.log("Modo offline activado. Intentando recargar o navegar...");
        
        try {
            await page.reload({ waitUntil: 'networkidle2', timeout: 5000 });
        } catch (e) {
            console.log("Recarga falló o tardó demasiado en offline (esperado si no hay Service Worker activo para el documento principal).");
        }

        const offlineHtml = await page.content();
        if(offlineHtml.toLowerCase().includes('offline') || offlineHtml.toLowerCase().includes('sin conexión')) {
            console.log("✅ El sistema muestra correctamente un estado o indicador offline.");
        } else {
            console.log("⚠️ No se detectó un indicador obvio de offline en la UI después de recargar, o la página no cargó desde caché.");
        }

        // Test balanza interaction if possible
        console.log("6. Verificando sección Balanza...");
        const balanzaBtn = await page.$x("//a[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'balanza')]");
        if(balanzaBtn.length > 0) {
            console.log("✅ Se encontró botón de navegación a Balanza.");
        }

    } catch (e) {
        console.error("Error durante la prueba:", e);
    } finally {
        await browser.close();
        console.log("Prueba finalizada.");
    }
})();
