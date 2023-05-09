/**
 *
 * Realiza la inicialización del gráfico con una petición
 * al backend (es una nueva ejecución)
 *
 * @param rutadatos - ruta del backend
 * @param elementos - elementos del formulario
 * @param preparadataset - referencia a función que prepara el conjunto de datos
 * @param grafico - referencia a función que genera el gráfico
 * @param flag_especificas - indica si también deben generarse estadísticas específicas
 */
function inicializar_con_peticion(rutadatos,elementos, preparadataset, grafico, flag_especificas=false) {
    inicializar(rutadatos, elementos).then(function (datos) {
        inicializarGrafico(datos, preparadataset,grafico);

        let stats = Object.keys(JSON.parse(datos.stats));
        generargraficoestadistico("estadisticas_generales", JSON.parse(datos.stats), stats);

        if (flag_especificas) {
            generarespecificas(datos.specific_stats);
        }
    })
        .catch(error => {console.log(error)});
}

/**
 *
 * Realiza la inicialización del gráfico sin petición
 * (los datos provienen de una ejecución previa)
 *
 * @param datos - datos de una ejecución almacenada
 * @param preparadataset - referencia a función que prepara el conjunto de datos
 * @param grafico - referencia a función que genera el gráfico
 * @param flag_especificas - indica si también deben generarse estadísticas específicas
 */
function inicializar_sin_peticion(datos, preparadataset, grafico, flag_especificas=false) {
    document.getElementById("div_cargando").remove();
    document.getElementById("visualizacion").style.visibility = 'visible';
    document.getElementById("titulo_visualizacion").style.visibility = 'visible';
    inicializarGrafico(datos, preparadataset,grafico);

    let stats = Object.keys(JSON.parse(datos.stats));
    generargraficoestadistico("estadisticas_generales", JSON.parse(datos.stats), stats);

    if (flag_especificas) {
        generarespecificas(datos.specific_stats);
    }
}