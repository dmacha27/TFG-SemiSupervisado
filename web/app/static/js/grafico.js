const simbolos = d3.symbol();

let nexit, previt, rep;

let graficosvg, gx, gy, maxit, color, mapa, puntos;


/**
 *
 * Genera el SVG del gráfico principal.
 *
 * @param datos - todos los datos generados por el algoritmo
 * @param preparar - función que prepara el conjunto de datos particular del algoritmo
 * @param binding - función que grafica los puntos con base en la anterior
 */
function inicializarGrafico(datos, preparar, binding) {
    nexit = d3.select("#nextit");
    previt = d3.select("#previt");
    rep = d3.select("#reproducir");

    let margin = {top: 10, right: 0, bottom: 60, left: 45},
        width = 750 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    maxit = datos.iterations;
    let dataset = preparar(JSON.parse(datos.log));
    mapa = JSON.parse(datos.mapa);
    document.getElementById("progreso").max = maxit;

    color = d3.scaleOrdinal()
        .domain(Object.keys(mapa))
        .range(d3.schemeCategory10);

    let svg = d3.select("#visualizacion_principal")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .style("margin", "auto");

    //Etiqueta eje X
    svg.append("text")
        .attr("class", "cx")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom / 2)
        .text(cx);

    //Etiqueta eje Y
    svg.append("text")
        .attr("class", "cy")
        .attr("text-anchor", "middle")
        .attr("y", -margin.left)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .text(cy);

    let leyenda = document.getElementById("leyenda_visualizacion");

    leyenda.innerHTML = "";

    for (const clase of Object.keys(mapa)) {
        let span = document.createElement("span");
        span.style.color = color(parseInt(clase));
        span.innerHTML = mapa[clase];
        leyenda.appendChild(span);
    }

    gx = d3.scaleLinear()
        .domain([d3.min(dataset, d => d[0]), d3.max(dataset, d => d[0])])
        .range([0, width]);
    gy = d3.scaleLinear()
        .domain([d3.min(dataset, d => d[1]), d3.max(dataset, d => d[1])])
        .range([height, 0]);

    let xAxis = svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(gx));
    let yAxis = svg.append("g")
        .call(d3.axisLeft(gy));

    svg.append("defs").append("SVG:clipPath")
        .attr("id", "clip")
        .append("SVG:rect")
        .attr("width", width )
        .attr("height", height )
        .attr("x", 0)
        .attr("y", 0);

    graficosvg = svg.append('g')
        .attr("clip-path", "url(#clip)")

    //Basado en https://d3-graph-gallery.com/graph/interactivity_tooltip.html#template
    d3.select("#visualizacion_principal")
        .append("div")
        .style("opacity", 0)
        .attr("class", "tooltip")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "2px")
        .style("border-radius", "5px")
        .style("padding", "5px")
        .style("position", "absolute")

    binding(dataset);

    const zoom = d3.zoom()
        .scaleExtent([1, 8])
        .extent([[0, 0], [width, height]])
        .on("zoom", updateChart);

    d3.select("#visualizacion_principal svg").call(zoom);

    /**
     *
     * Se encarga de redimensionar los ejes y mover los puntos a las posiciones correctas
     * ante los eventos de zoom.
     *
     * @param e - evento
     */
    function updateChart(e) {

        // recover the new scale
        let newX = e.transform.rescaleX(gx);
        let newY = e.transform.rescaleY(gy);

        // update axes with these new boundaries
        xAxis.call(d3.axisBottom(newX))
        yAxis.call(d3.axisLeft(newY))

        // update circle position
        graficosvg
            .selectAll("path")
            .attr("transform", function (d) {
                return "translate(" + newX(d[0]) + "," + newY(d[1]) + ")";
            });
    }

    // Botón de reiniciar zoom
    document.querySelector("#reiniciar_zoom").addEventListener("click", function (){
        d3.select("#visualizacion_principal svg")
            .transition()
            .duration(750)
            .call(zoom.transform, d3.zoomIdentity);
    })


}

/**
 *
 * Función anónima como variable para asignarla como gestor de evento "mouseleave".
 * Cuando el mouse abandona la zona en cuestión se esconde el tooltip.
 *
 */
const mouseleave = function () {
    d3.select(".tooltip")
        .style("stroke", "none")
        .style("display", "none")
};

/**
 * Actualiza el progreso en la barra de progreso e iteración.
 * Además, lanza un evento en global para que el resto de elementos
 * que dependan del progreso puedan actualizarse.
 *
 * @param paso - indica el paso realizado (next o previous)
 */
function actualizaProgreso(paso){
    document.getElementById("progreso").value=cont;
    document.getElementById("iteracion").innerHTML = cont.toString();
    if (paso === "next"){
        document.dispatchEvent(new Event('next'));
    }else{
        document.dispatchEvent(new Event('prev'));
    }
}

let intervalo = null;

/**
 *
 * Se encarga de la reproducción automática de la visualización al
 * pulsar dicho botón.
 *
 * Tiempo: 0.75 segundos por iteración.
 *
 */
function reproducir(){
    if (!intervalo){
        document.getElementById("reproducir").innerHTML = traducir('Pause');
        intervalo = setInterval(function () {
            if (cont >= maxit){
                document.getElementById("reproducir").innerHTML = traducir('Play');
                clearInterval(intervalo);
                intervalo = null;
            }
            document.dispatchEvent(new Event('next_reproducir'));
        }, 750)
    } else {
        document.getElementById("reproducir").innerHTML = traducir('Play');
        clearInterval(intervalo);
        intervalo = null;
    }
}

/**
 *
 * Prepara el conjunto de datos conforme al formato
 * de Self-Training
 *
 * @param datos - datos de la visualización principal
 * @returns {*[]} - array de arrays
 */
function preparardataset_selftraining(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['target'];
    let iter = datos['iter'];

    for (const key in xs){
        dataset.push([xs[key],ys[key],etiq[key],iter[key]])
    }

    return dataset;
}

/**
 *
 * Genera los puntos dentro del gráfico SVG, exclusivo
 * para Self-Training
 *
 */
function grafico_selftraining(dataset) {
    nexit.on("click", next);
    previt.on("click", prev);
    rep.on("click",reproducir);

    const mousemove_selftraining = function(e, dot) {
        d3.select(".tooltip")
            .style("opacity", 1)
            .style("display", "block");

        d3.select(".tooltip")
            .html(function() {
                if (dot[3] <= cont && dot[2] !== -1) {
                    if (dot[3] === 0){
                        return tooltip_dato_inicial(dot);
                    }else {
                        return cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br>" + traducir('Label') + ": " +
                            "<span style='color:"+ color(parseInt(dot[2])) +"'>" + mapa[dot[2]] + "</span>";
                    }
                } else {
                    return un_clasificador_return_no_clasificado(dot);
                }
            })
            .style("left", (e.offsetX + 60) + "px")
            .style("top", (e.offsetY + 60) + "px");

    };

    puntos = graficosvg.selectAll("dot")
        .data(dataset)
        .enter()
        .append("path")
        .attr("d", simbolos.type(function (d) {
            if (d[3] === 0) {
                return d3.symbolCircle; // Dato inicial
            } else {
                return d3.symbolCross;
            }
        }).size(35))
        .attr("transform", function (d) {
            return "translate(" + gx(d[0]) + "," + gy(d[1]) + ")";
        })
        .style("fill", function (d) {
            if (d[3] <= cont) {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .style("stroke", "transparent")
        .style("stroke-width", "3px")
        .on("mousemove", function (e) {
            mousemove_selftraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave);

    document.addEventListener('next_reproducir', next);

    /**
     *
     * Gestiona el evento de iteración previa,
     * desclasificando (gris) los puntos específicos.
     *
     */
    function prev() {
        if (cont > 0) {
            cont--;
            puntos.filter(function (d) {
                return d[3] > cont;
            })
                .style("fill", "grey");
            actualizaProgreso("prev");
        }
    }

    /**
     *
     * Gestiona el evento de iteración siguiente,
     * clasificando (color concreto) los puntos específicos.
     *
     */
    function next() {
        if (cont < maxit) {
            cont++;
            puntos.filter(function (d) {
                return d[3] === cont && d[2] !== -1;
            })
                .style("fill", function (d) {
                    return color(d[2]);
                })
                .transition()
                .duration(0)
                //Como solo hay un clasificador base, se le asigna la forma de cruz
                .attr("d", simbolos.type(d3.symbolCross).size(35))
                .transition()
                .duration(300)
                .attr("d", simbolos.size(125))
                .transition()
                .duration(300)
                .attr("d", simbolos.size(35));
            actualizaProgreso("next");
        }
    }
}

let clf_forma;

/**
 *
 * Para los algoritmos con varios clasificadores base.
 * A partir de la posición del nombre de un clasificador
 * dentro de un array (que contiene todos los clasificadores en esa ejecución)
 * determina una figura (escogida arbitrariamente y de forma fija).
 *
 * @param clf - nombre del clasificador
 * @returns {{draw(*, *): void}} - figura de D3
 */
function obtenerSimbolo(clf){
    let indice = clf_forma.indexOf(clf);
    if(clf === -1 || indice === 0){ return d3.symbolCircle
    } else if (indice === 1){ return d3.symbolCross
    } else if (indice === 2){ return d3.symbolTriangle
    } else if (indice === 3){ return d3.symbolSquare
    }}


/**
 *
 * Para los algoritmos con varios clasificadores base.
 * A partir de la posición del nombre de un clasificador
 * dentro de un array (que contiene todos los clasificadores en esa ejecución)
 * determina un símbolo para HTML (escogido arbitrariamente y de forma fija).
 *
 * @param clf - nombre del clasificador
 * @returns {string} - símbolo HTML
 */
function obtenerSimboloUnicode(clf){
    let indice = clf_forma.indexOf(clf);
    if(clf === -1 || indice === 0){ return "&#9679"
    } else if (indice === 1){ return "&#128934"
    } else if (indice === 2){ return "&#9650"
    } else if (indice === 3){ return "&#9632"
    }}

/**
 *
 * Gestiona el evento de iteración previa exlusivamente
 * para CO-Training y Democratic CO-Learning,
 * desclasificando (gris) los puntos específicos.
 *
 */
function prev_co() {
    if (cont > 0) {
        cont--;
        puntos.filter(function (d) {
            return d[3] > cont;
        })
            .attr("d", simbolos.type(d3.symbolCircle).size(35))
            .style("fill", "grey");
        actualizaProgreso("prev");
    }
}

/**
 *
 * Gestiona el evento de iteración siguiente exlusivamente
 * para CO-Training y Democratic CO-Learning,
 * clasificando (color concreto y forma concreta) los puntos específicos.
 *
 */
function next_co() {
    if (cont < maxit) {
        cont++;
        puntos.filter(function (d) {
            return d[3] === cont && d[2] !== -1;
        })
            .style("fill", function (d) {
                return color(d[2]);
            })
            .transition()
            .duration(0)
            .attr("d", simbolos.type(function (d) {
                return obtenerSimbolo(d[4])
            }).size(35))
            .transition()
            .duration(300)
            .attr("d", simbolos.size(125))
            .transition()
            .duration(300)
            .attr("d", simbolos.size(35));

        actualizaProgreso("next");
    }
}

/**
 *
 * Prepara el conjunto de datos conforme al formato
 * de Co-Training
 *
 * @param datos - datos de la visualización principal
 * @returns {*[]} - array de arrays
 */
function preparardataset_cotraining(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['target'];
    let iter = datos['iter'];
    let clfs = datos['clf'];

    for (const key in xs){
        dataset.push([xs[key],ys[key],etiq[key],iter[key],clfs[key]])
    }

    let clasificadores = new Set();

    for (let i = 0; i < dataset.length; i++){
        clasificadores.add(dataset[i][4]);
    }
    clf_forma = Array.from(clasificadores);

    return dataset;
}

/**
 *
 * Genera los puntos dentro del gráfico SVG, exclusivo
 * para Co-Training
 *
 */
function grafico_cotraining(dataset) {
    nexit.on("click", next_co);
    previt.on("click", prev_co);
    rep.on("click", reproducir);

    const mousemove_cotraining = function (e, dot) {
        d3.select(".tooltip")
            .style("opacity", 1)
            .style("display", "block");

        d3.select(".tooltip")
            .html(function () {
                if (dot[3] <= cont && dot[2] !== -1) {
                    if (dot[3] === 0) {
                        return tooltip_dato_inicial(dot);
                    } else {
                        return cx + ": " + dot[0] + "<br>" + cy + ": " + dot[1] + "<br>" +
                            traducir('Classifier') + ": " + obtenerSimboloUnicode(dot[4]) + dot[4] +
                            "<br>" + traducir('Label') + ": " +
                            "<span style='color:"+ color(parseInt(dot[2])) +"'>" + mapa[dot[2]] + "</span>";
                    }
                } else {
                    return un_clasificador_return_no_clasificado(dot);
                }
            })
            .style("left", (e.offsetX + 60) + "px")
            .style("top", (e.offsetY + 60) + "px");
    };

    puntos = declarar_puntos_svg(dataset)
        .style("fill", function (d) {
            if (d[3] <= cont) {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .style("stroke", "transparent")
        .style("stroke-width", "3px")
        .on("mousemove", function (e) {
            mousemove_cotraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave);


    document.addEventListener('next_reproducir', next_co);
}

/**
 *
 * A partir de una posición concreta (x,y), obtiene
 * los puntos que ocupan esa posición (pueden ser varios)
 *
 * @param x - posición x
 * @param y - posición y
 * @returns {*} - puntos
 */
function puntos_en_x_y(x,y) {
    return puntos.filter(function(d) {
        return d[0] === x && d[1] === y;
    })
}

/**
 *
 * Prepara el conjunto de datos conforme al formato
 * de Democratic Co-Learning y Tri-Training (el proceso es
 * exactamente el mismo).
 *
 * @param datos - datos de la visualización principal
 * @returns {*[]} - array de arrays
 */
function preparardataset_democraticcolearning_tritraining(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['targets'];
    let iter = datos['iters'];
    let clfs = datos['clfs'];

    let clasificadores = new Set()
    for (const key in xs){
        if (iter[key].every(function(elemento) {
            return elemento === -1;
        })){
            dataset.push([xs[key],ys[key],-1,maxit+1,-1])
        }else{
            for (let i = 0; i < clfs[key].length; i++) {
                if (iter[key][i] !== -1) {
                    clasificadores.add(clfs[key][i])
                    dataset.push([xs[key],ys[key],etiq[key][i],iter[key][i],clfs[key][i]])
                }
            }
        }
    }
    clf_forma = Array.from(clasificadores)
    return dataset;
}


/**
 *
 * Genera los puntos dentro del gráfico SVG, exclusivo
 * para Democratic Co-Learning
 *
 */
function grafico_democraticcolearning(dataset) {
    nexit.on("click", next_co);
    previt.on("click", prev_co);
    rep.on("click", reproducir);

    const mousemove_democraticcolearning = function(e, dot) {
        d3.select(".tooltip")
            .style("opacity", 1)
            .style("display", "block");

        function alguno_clasificado(puntos_posicion) {
            for (let i = 0; i < puntos_posicion.length; i++) {
                if (puntos_posicion[i].__data__[3] <= cont){
                    return true;
                }
            }
            return false;
        }

        d3.select(".tooltip")
            .html(function() {
                let puntos_posicion;
                puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];

                let cadena_tooltip = "";

                for (let i = 0; i < puntos_posicion.length; i++) {

                    let p_data = puntos_posicion[i].__data__
                    if (p_data[3] <= cont && p_data[2] !== -1) {
                        if (p_data[3] === 0){
                            cadena_tooltip += tooltip_dato_inicial(p_data);
                        }else {
                            cadena_tooltip += tooltip_dato_no_inicial(p_data) +
                                "<span style='color:"+ color(parseInt(p_data[2])) +"'>" + mapa[p_data[2]] + "</span>";
                        }
                        cadena_tooltip += "<br>-------<br>";
                    } else{
                        cadena_tooltip += tooltip_ninguno_clasificado(alguno_clasificado,puntos_posicion,i,p_data);
                    }
                }
                return cadena_tooltip
            })
            .style("left", (e.offsetX + 60) + "px")
            .style("top", (e.offsetY + 60) + "px");
    };

    puntos = declarar_puntos_svg(dataset)
        .style("fill", function (d) {
            if (d[4] === "inicio") {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .on("mousemove", function (e) {
            mousemove_democraticcolearning(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave)

    document.addEventListener('next_reproducir', next_co);
}


/**
 *
 * Genera los puntos dentro del gráfico SVG, exclusivo
 * para Tri-Training
 *
 */
function databinding_tritaining(dataset) {
    nexit.on("click", next);
    previt.on("click", prev);
    rep.on("click", reproducir);

    const mousemove_tritraining = function(e, dot) {
        d3.select(".tooltip")
            .style("opacity", 1)
            .style("display", "block");

        function alguno_clasificado(puntos_posicion) {
            for (let i = 0; i < puntos_posicion.length; i++) {
                if (puntos_posicion[i].__data__[3].indexOf(cont) >= 0){
                    return true;
                }
            }
            return false;
        }

        d3.select(".tooltip")
            .html(function() {
                let puntos_posicion;
                puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];

                let cadena_tooltip = "";

                for (let i = 0; i < puntos_posicion.length; i++) {

                    let p_data = puntos_posicion[i].__data__
                    let id_cont = null;
                    if (typeof p_data[3] === "number"){
                        id_cont = 0;
                    }else {
                        id_cont = p_data[3].indexOf(cont);
                    }
                    if (id_cont >= 0) { // Si es -1 esto indica que ese punto no se clasifica en esta iteración
                        if (p_data[3] === 0) {
                            cadena_tooltip += tooltip_dato_inicial(p_data);
                        } else {
                            cadena_tooltip += tooltip_dato_no_inicial(p_data) +
                                "<span style='color:"+ color(parseInt(p_data[2][id_cont])) + "'>" +
                                mapa[p_data[2][id_cont]] + "</span>";
                        }
                        cadena_tooltip += "<br>-------<br>";
                    } else{
                        cadena_tooltip += tooltip_ninguno_clasificado(alguno_clasificado,puntos_posicion,i,p_data);
                    }
                }
                return cadena_tooltip
            })
            .style("left", (e.offsetX + 60) + "px")
            .style("top", (e.offsetY + 60) + "px");
    };

    puntos = declarar_puntos_svg(dataset)
        .style("fill", function (d) {
            if (d[4] === "inicio") {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .on("mousemove", function (e) {
            mousemove_tritraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave)

    document.addEventListener('next_reproducir', next_co);

    function prev() {
        if (cont > 0) {
            puntos_a_gris();

            cont--;

            let recien_clasificados = puntos.filter(function (d) {
                if (typeof d[3] === "number"){
                    return false;
                }else {
                    return d[3].indexOf(cont) >= 0;
                }
            })
                .transition()
                .duration(500)
                .transition()
                .duration(0)
                .attr("d", simbolos.type(function (d) {
                    return obtenerSimbolo(d[4])
                }).size(35))
                .style("fill", function (d) {
                    return color(d[2][d[3].indexOf(cont)]);
                })
                .transition()
                .duration(300)
                .attr("d", simbolos.size(125))
                .transition()
                .duration(300)
                .attr("d", simbolos.size(35));

            ocultar_no_recien_clasificados(recien_clasificados);

            actualizaProgreso("prev");
        }
    }

    function next() {
        if (cont < maxit) {
            puntos_a_gris();

            cont++;
            // Colorear los puntos de esa iteración
            let recien_clasificados = puntos.filter(function (d) {
                if (typeof d[3] === "number"){
                    return false;
                }else {
                    return d[3].indexOf(cont) >= 0;
                }
            })
                .transition()
                .duration(function (){
                    //Si es la primera iteración no es necesario
                    // hacer esperar al usuario pues la primera parte
                    // no tiene efecto
                    if (cont - 1 === 0){
                        return 0;
                    }else{
                        // Este valor hace perder tiempo y permite
                        //al usuario ver la transición
                        return 500;
                    }
                })
                .transition()
                .duration(0)
                .style("fill", function (d) {
                    return color(d[2][d[3].indexOf(cont)]);
                })
                .transition()
                .duration(0)
                .attr("d", simbolos.type(function (d) {
                    return obtenerSimbolo(d[4])
                }).size(35))
                .transition()
                .duration(300)
                .attr("d", simbolos.size(125))
                .transition()
                .duration(300)
                .attr("d", simbolos.size(50));

            // Los puntos que estén en la misma posición que los recién clasificados
            // deben no mostrarse (algunos se superponen)
            ocultar_no_recien_clasificados(recien_clasificados);

            actualizaProgreso("next");
        }
    }
}


/*
###############################    
#       MÉTODOS COMUNES       #
###############################
 */

function declarar_puntos_svg(dataset) {
    return graficosvg.selectAll("dot")
        .data(dataset)
        .enter()
        .append("path")
        .attr("d", simbolos.type(d3.symbolCircle).size(35))
        .attr("transform", function (d) {
            return "translate(" + gx(d[0]) + "," + gy(d[1]) + ")";
        })
}

function puntos_a_gris() {
    puntos.style("visibility", "visible");

    // Hacer que los puntos anteriores pasen a gris rápido
    // hará que el usuario percibirá el cambio.
    puntos.filter(function (d) {
        if (typeof d[3] === "number"){
            return false;
        }else {
            return d[3].indexOf(cont) >= 0;
        }
    })
        .transition()
        .duration(0)
        .style("fill", "grey")
        .attr("d", simbolos.type(d3.symbolCircle).size(35))
        .attr("d", simbolos.size(35))
        .transition()
        .duration(500);
}

function tooltip_dato_inicial(dot) {
    return traducir('Initial data') + "<br>" + cx +": " + dot[0] +"<br>" + cy + ": " +
        dot[1] + "<br>" + traducir('Label') + ": " +
        "<span style='color:"+ color(parseInt(dot[2])) +"'>" + mapa[dot[2]] + "</span>";
}

function un_clasificador_return_no_clasificado(dot) {
    return cx + ": " + dot[0] + "<br>" + cy + ": " + dot[1] + "<br>" + traducir('Classifier: Not classified') +
        "<br>" + traducir('Label: Not classified');
}

function tooltip_dato_no_inicial(p_data) {
    return cx +": " + p_data[0] +"<br>" + cy + ": " + p_data[1] +
        "<br>" + traducir('Classifier') + ": " + obtenerSimboloUnicode(p_data[4]) +
        p_data[4] + "<br>" + traducir('Label') + ": ";
}

function tooltip_ninguno_clasificado(alguno_clasificado, puntos_posicion, i, p_data) {
    let cadena_aux = "";
    if (i === 0 && !alguno_clasificado(puntos_posicion)) {
        cadena_aux += cx + ": " + p_data[0] + "<br>" + cy + ": " + p_data[1] +
            "<br>" + traducir('Classifier: Not classified') + "<br>" +
            traducir('Label: Not classified');
        cadena_aux += "<br>-------<br>";
    }
    return cadena_aux;
}

function ocultar_no_recien_clasificados(recien_clasificados) {
    recien_clasificados.each(function (d_reciente){
        puntos.filter(function (d) {
            if (typeof d[3] === "number"){
                return false; // REVISAR BUG PORQUE CUANDO SE CLASIFICA UN PUNTO INICIAL APARECE TAMBIEN EN TOOLTIP
            }else {
                return d[0] === d_reciente[0] && d[1] === d_reciente[1] && d[3].indexOf(cont) === -1;
            }
        }).style("visibility", "hidden")
    });
}

