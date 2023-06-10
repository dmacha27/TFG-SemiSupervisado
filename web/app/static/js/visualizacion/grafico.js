const simbolos = d3.symbol();

let nexit, previt, rep;

let graficosvg, gx, gy, maxit, color, mapa, puntos;

let duplicados = {}

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

    color = d3.scaleOrdinal()
        .domain(Object.keys(mapa))
        .range(d3.schemeSet3);

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
        .attr("class", "tooltip")
        .style("pointer-events", "none")
        .style("background-color", "white")
        .style("border", "solid")
        .style("border-width", "2px")
        .style("border-radius", "5px")
        .style("padding", "5px")
        .style("position", "absolute")
        .style("display", "none")

    binding(dataset);

    const zoom = d3.zoom()
        .scaleExtent([0.5, Infinity])
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
    let porcentaje = (cont/maxit)*100;
    document.getElementById("progreso").style.width = porcentaje.toString() +"%";
    document.getElementById("progreso").setAttribute("aria-valuenow", porcentaje.toString());
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
        document.getElementById("reproducir").innerHTML = "<i class='bi bi-stop-fill'></i>";
        intervalo = setInterval(function () {
            if (cont >= maxit){
                document.getElementById("reproducir").innerHTML = "<i class='bi bi-play-fill'></i>";
                clearInterval(intervalo);
                intervalo = null;
            }
            document.dispatchEvent(new Event('next_reproducir'));
        }, 750)
    } else {
        document.getElementById("reproducir").innerHTML = "<i class='bi bi-play-fill'></i>";
        clearInterval(intervalo);
        intervalo = null;
    }
}

/**
 *
 * Posiciona el tooltip correctamente a una pequeña
 * distancia del ratón
 *
 * @param e - evento
 */
function posicionartooltip(e) {

    let margin = {top: 10, right: 0, bottom: 60, left: 45},
        width = 750 - margin.left - margin.right,
        height = 600 - margin.top - margin.bottom;

    let real_this = document.getElementById('visualizacion_principal');
    const [mouseX, mouseY] = d3.pointer(e, real_this);

    d3.select(".tooltip")
        .style("opacity", 1)
        .style("display", "block")
        //Extraido de https://observablehq.com/@clhenrick/tooltip-d3-convention
        .style(
            "top",
            mouseY < height / 2 ? `${mouseY + 20}px` : "initial"
        )
        .style(
            "right",
            mouseX > width / 2
                ? `${width - mouseX + 45}px`
                : "initial"
        )
        .style(
            "bottom",
            mouseY > height / 2
                ? `${height - mouseY + 75}px`
                : "initial"
        )
        .style(
            "left",
            mouseX < width / 2 ? `${mouseX + 15}px` : "initial"
        );
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
        dataset.push([xs[key], ys[key], etiq[key], iter[key], generar_id_duplicado(xs[key], ys[key])]);

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
            .html(function() {
                let puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];
                let cadena_tooltip = "<strong>" + traducir('Position') + "</strong><br>"
                    + cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br><br>";
                if (cuantos_duplicados(dot[0], dot[1]) > 1) {
                    cadena_tooltip += "<strong>" +
                        cuantos_duplicados(dot[0], dot[1]).toString() + " " + traducir("overlapping points") +
                        ":</strong><br>";
                }
                for (let i = 0; i < puntos_posicion.length; i++) {
                    let p_data = puntos_posicion[i].__data__;
                    if (p_data[3] <= cont && p_data[2] !== -1) {
                        if (p_data[3] === 0){
                            cadena_tooltip += tooltip_dato_inicial(p_data);
                        }else {
                            cadena_tooltip += escribir_duplicados(p_data[0],p_data[1], p_data[p_data.length-1]) +
                                traducir('Label') + ": " +
                                "<span style='color:"+ color(parseInt(p_data[2])) +"'>" + mapa[p_data[2]] + "</span>"+
                                "<span> ("+ traducir('Iteration') + ": " + p_data[3] +")</span>";
                        }
                    } else{
                        cadena_tooltip += escribir_duplicados(p_data[0],p_data[1], p_data[p_data.length-1]) +
                            un_clasificador_return_no_clasificado(false);
                    }
                    if (i < puntos_posicion.length -1) {
                        cadena_tooltip += "<br>-------<br>";
                    }
                }
                return cadena_tooltip
            })

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
            posicionartooltip(e);
            mousemove_selftraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave);

    // Los iniciales llevarlos al frente
    puntos.filter(function (d) {
        return d[3] === 0;
    }).each(function (){
        this.parentNode.appendChild(this);
    })

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

            puntos.filter(function (d) {
                return d[3] <= cont;
            }).each(function() {
                this.parentNode.appendChild(this);
            });

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
            let recien_clasificados = puntos.filter(function (d) {
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

            // LLevar al frente a los recién clasificados
            recien_clasificados.each(function (){
                this.parentNode.appendChild(this);
            });

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

        puntos.filter(function (d) {
            return d[3] <= cont;
        }).each(function() {
            this.parentNode.appendChild(this);
        });
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
        let recien_clasificados = puntos.filter(function (d) {
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

        recien_clasificados.each(function (){
            this.parentNode.appendChild(this);
        });

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
        dataset.push([xs[key],ys[key],etiq[key],iter[key],clfs[key], generar_id_duplicado(xs[key], ys[key])]);
    }

    let clasificadores = new Set();

    for (let dato of dataset){
        clasificadores.add(dato[4]);
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
            .html(function() {
                let puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];
                let cadena_tooltip = "<strong>" + traducir('Position') + "</strong><br>"
                    + cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br><br>";
                if (cuantos_duplicados(dot[0], dot[1]) > 1) {
                    cadena_tooltip += "<strong>" + cuantos_duplicados(dot[0], dot[1]).toString() +
                        " " + traducir("overlapping points") + ":</strong><br>";
                }
                for (let i = 0; i < puntos_posicion.length; i++) {
                    let p_data = puntos_posicion[i].__data__
                    if (p_data[3] <= cont && p_data[2] !== -1) {
                        if (p_data[3] === 0){
                            cadena_tooltip += tooltip_dato_inicial(p_data);
                        }else {
                            cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length-1]) +
                                traducir('Classifier') + ": " + obtenerSimboloUnicode(p_data[4]) + p_data[4] +
                                "<br>" + traducir('Label') + ": " +
                                "<span style='color:"+ color(parseInt(p_data[2])) +"'>" + mapa[p_data[2]] + "</span>"+
                                "<span> ("+ traducir('Iteration') + ": " + p_data[3] +")</span>";
                        }
                    } else{
                        cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length-1]) +
                            un_clasificador_return_no_clasificado();
                    }

                    if (i < puntos_posicion.length -1) {
                        cadena_tooltip += "<br>-------<br>";
                    }
                }
                return cadena_tooltip
            })
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
            posicionartooltip(e);
            mousemove_cotraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave);

    // Los iniciales llevarlos al frente
    puntos.filter(function (d) {
        return d[3] === 0;
    }).each(function (){
        this.parentNode.appendChild(this);
    })

    document.addEventListener('next_reproducir', next_co);
}

/**
 *
 * Prepara el conjunto de datos conforme al formato
 * de Democratic Co-Learning.
 *
 * @param datos - datos de la visualización principal
 * @returns {*[]} - array de arrays
 */
function preparardataset_democraticcolearning(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['targets'];
    let iter = datos['iters'];
    let clfs = datos['clfs'];

    let clasificadores = new Set()
    for (const key in xs){
        let id_duplicado = generar_id_duplicado(xs[key], ys[key]);
        if (iter[key].every(function(elemento) {
            return elemento === -1;
        })){
            dataset.push([xs[key], ys[key], -1, maxit+1, -1, id_duplicado])
        }else{
            for (let i = 0; i < clfs[key].length; i++) {
                if (iter[key][i] !== -1) {
                    clasificadores.add(clfs[key][i])
                    dataset.push([xs[key],ys[key],etiq[key][i],iter[key][i],clfs[key][i], id_duplicado])
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

    function alguno_clasificado(puntos_posicion) {
        for (let punto_posicion of puntos_posicion) {
            if (punto_posicion.__data__[3] <= cont){
                return true;
            }
        }
        return false;
    }

    function alguno_clasificado_con_id(puntos_posicion, id_duplicado) {
        for (let punto_posicion of puntos_posicion) {
            if (punto_posicion.__data__[3] <= cont &&
                punto_posicion.__data__[punto_posicion.__data__.length-1] === id_duplicado){
                return true;
            }
        }
        return false;
    }

    const mousemove_democraticcolearning = function(e, dot) {
        d3.select(".tooltip")
            .html(function() {
                let puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];
                let cadena_tooltip = "<strong>" + traducir('Position') + "</strong><br>"
                    + cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br><br>";
                if (cuantos_duplicados(dot[0], dot[1]) > 1) {
                    cadena_tooltip += "<strong>" + cuantos_duplicados(dot[0], dot[1]).toString() + " " + traducir("overlapping points") + ":</strong><br>";
                }

                if (alguno_clasificado(puntos_posicion)) {
                    let puntos_vistos = new Set();
                    for (let i = 0; i < puntos_posicion.length; i++) {
                        let p_data = puntos_posicion[i].__data__;
                        if (p_data[3] <= cont && p_data[2] !== -1) {
                            if (puntos_vistos.size > 0) {
                                cadena_tooltip += "<br>-------<br>";
                            }
                            puntos_vistos.add(p_data[p_data.length - 1]);
                            if (p_data[3] === 0) {
                                cadena_tooltip += tooltip_dato_inicial(p_data);
                            } else {
                                cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length - 1]) +
                                    tooltip_dato_no_inicial(p_data) +
                                    "<span style='color:" + color(parseInt(p_data[2])) + "'>" + mapa[p_data[2]] + "</span>" +
                                    "<span> (" + traducir('Iteration') + ": " + p_data[3] + ")</span>";
                            }
                        } else { // Aquellos que no están etiquetados todavía o nunca (maxit+1)
                            if ((!(puntos_vistos.has(p_data[p_data.length - 1])) && //Que no se haya visto
                                    !alguno_clasificado_con_id(puntos_posicion, p_data[p_data.length - 1])) //Y que no haya uno con misma id que ya esté clasificado
                                || p_data[3] === maxit+1) {
                                if (puntos_vistos.size > 0) {
                                    cadena_tooltip += "<br>-------<br>";
                                }
                                puntos_vistos.add(p_data[p_data.length - 1]);
                                cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length - 1]) +
                                    un_clasificador_return_no_clasificado();
                            }
                        }
                    }
                } else { // No hay ningún punto etiquetado
                    // Solo debe mostrarse un único texto exponiendo esa información
                    let puntos_vistos = new Set();
                    for (let i = 0; i < puntos_posicion.length; i++) {
                        let p_data = puntos_posicion[i].__data__;
                        if (!(puntos_vistos.has(p_data[p_data.length-1]))) {
                            if (puntos_vistos.size > 0) {
                                cadena_tooltip += "<br>-------<br>";
                            }
                            puntos_vistos.add(p_data[p_data.length-1]);
                            cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length - 1]) +
                                un_clasificador_return_no_clasificado();
                        }
                    }
                }
                return cadena_tooltip;
            })
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
            posicionartooltip(e);
            mousemove_democraticcolearning(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave)

    // Los iniciales llevarlos al frente
    puntos.filter(function (d) {
        return d[4] === "inicio";
    }).each(function (){
        this.parentNode.appendChild(this);
    })

    document.addEventListener('next_reproducir', next_co);
}

/**
 *
 * Prepara el conjunto de datos conforme al formato
 * de Tri-Training.
 *
 * @param datos - datos de la visualización principal
 * @returns {*[]} - array de arrays
 */
function preparardataset_tritraining(datos) {
    let dataset = [];
    let xs = datos[cx];
    let ys = datos[cy];
    let etiq = datos['targets'];
    let iter = datos['iters'];
    let clfs = datos['clfs'];

    let clasificadores = new Set()
    for (const key in xs){
        let id_duplicado = generar_id_duplicado(xs[key], ys[key]);
        if (iter[key].every(function(lista_iters) {
            return lista_iters.length === 0;
        })){
            dataset.push([xs[key], ys[key], -1, maxit+1, -1, id_duplicado])
        }else{
            for (let i = 0; i < clfs[key].length; i++) {
                if (iter[key][i].length !== 0) {
                    clasificadores.add(clfs[key][i])
                    dataset.push([xs[key],ys[key],etiq[key][i],iter[key][i],clfs[key][i], id_duplicado])
                }
            }
        }
    }

    clf_forma = Array.from(clasificadores)
    return dataset;
}

function escribir_iteraciones_clasificado(iteraciones) {
    let cadena =  "<span> ("+ traducir('Iteration') + ": ";
    let algo = false;
    for (let i = 0; i < iteraciones.length; i++) {
        if (iteraciones[i] === cont) {
            cadena += iteraciones[i].toString();
            return cadena + ")</span>";
        }
        if (iteraciones[i] < cont) {
            algo = true;
            cadena += iteraciones[i].toString();
        }
        if (i < iteraciones.length - 1){
            cadena += ",";
        }
    }
    if (!algo) return "";
    return cadena + ")</span>"
}

/**
 *
 * Genera los puntos dentro del gráfico SVG, exclusivo
 * para Tri-Training
 *
 */
function grafico_tritaining(dataset) {
    nexit.on("click", next);
    previt.on("click", prev);
    rep.on("click", reproducir);

    function alguno_clasificado(puntos_posicion) {
        for (let punto_posicion of puntos_posicion) {
            if (punto_posicion.__data__[3] === 0){
                return true;
            }
            if (Array.isArray(punto_posicion.__data__[3]) && punto_posicion.__data__[3].indexOf(cont) >= 0) {
                return true;
            }
        }
        return false;
    }

    function alguno_clasificado_con_id(puntos_posicion, id_duplicado) {
        for (let punto_posicion of puntos_posicion) {
            if (Array.isArray(punto_posicion.__data__[3]) && punto_posicion.__data__[3].indexOf(cont) >= 0
                && punto_posicion.__data__[punto_posicion.__data__.length-1] === id_duplicado) {
                return true;
            }
        }
        return false;
    }


    const mousemove_tritraining = function(e, dot) {
        d3.select(".tooltip")
            .html(function() {
                let puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];
                let cadena_tooltip = "<strong>" + traducir('Position') + "</strong><br>"
                    + cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br><br>";
                if (cuantos_duplicados(dot[0], dot[1]) > 1) {
                    cadena_tooltip += "<strong>" + cuantos_duplicados(dot[0], dot[1]).toString() +
                        " " + traducir("overlapping points") + ":</strong><br>";
                }

                if (alguno_clasificado(puntos_posicion)) {
                    let puntos_vistos = new Set();
                    for (let i = 0; i < puntos_posicion.length; i++) {
                        let p_data = puntos_posicion[i].__data__;
                        let id_cont = null;
                        if (typeof p_data[3] === "number") {
                            if (p_data[2] !== -1) {
                                id_cont = 0;
                            } else {
                                id_cont = -1;
                            }
                        } else {
                            id_cont = p_data[3].indexOf(cont);
                        }
                        if (id_cont >= 0) { // Si es -1 esto indica que ese punto no se clasifica en esta iteración
                            if (puntos_vistos.size > 0) {
                                cadena_tooltip += "<br>-------<br>";
                            }
                            puntos_vistos.add(p_data[p_data.length - 1]);
                            if (p_data[3] === 0) {
                                cadena_tooltip += tooltip_dato_inicial(p_data);
                            } else {
                                cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length - 1]) +
                                    tooltip_dato_no_inicial(p_data) +
                                    "<span style='color:" + color(parseInt(p_data[2][id_cont])) + "'>" +
                                    mapa[p_data[2][id_cont]] + "</span>" +
                                    escribir_iteraciones_clasificado(p_data[3]);
                            }
                        } else {
                            if ((!(puntos_vistos.has(p_data[p_data.length - 1])) && //Que no se haya visto
                                    !alguno_clasificado_con_id(puntos_posicion, p_data[p_data.length - 1])) //Y que no haya uno con misma id que ya esté clasificado
                                || p_data[3] === maxit+1) {
                                if (puntos_vistos.size > 0) {
                                    cadena_tooltip += "<br>-------<br>";
                                }
                                puntos_vistos.add(p_data[p_data.length - 1]);
                                cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length - 1]) +
                                    un_clasificador_return_no_clasificado() +
                                    escribir_iteraciones_clasificado(p_data[3]);
                            }
                        }
                    }
                } else { // No hay ningún punto etiquetado
                    // Solo debe mostrarse un único texto exponiendo esa información
                    let puntos_vistos = new Set();
                    for (let i = 0; i < puntos_posicion.length; i++) {
                        let p_data = puntos_posicion[i].__data__;
                        if (!(puntos_vistos.has(p_data[p_data.length-1]))) {
                            if (puntos_vistos.size > 0) {
                                cadena_tooltip += "<br>-------<br>";
                            }
                            puntos_vistos.add(p_data[p_data.length-1]);
                            cadena_tooltip += escribir_duplicados(p_data[0], p_data[1], p_data[p_data.length - 1]) +
                                un_clasificador_return_no_clasificado() +
                                escribir_iteraciones_clasificado(p_data[3]);
                        }
                    }
                }
                return cadena_tooltip
            })
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
            posicionartooltip(e);
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

            // Los que sí están clasificados deben estar en el frente
            // para que no haya superposiciones de grises
            recien_clasificados.each(function() {
                this.parentNode.appendChild(this);
            });

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

            recien_clasificados.each(function (){
                this.parentNode.appendChild(this);
            });

            actualizaProgreso("next");
        }
    }
}


/*
###############################
#       MÉTODOS COMUNES       #
###############################
 */
/**
 *
 * Obtiene el número de puntos duplicados en un punto del gráfico.
 *
 * @param x - posición x
 * @param y - posición y
 * @returns {*} - número de duplicados
 */
function cuantos_duplicados(x,y) {
    return duplicados[String([x,y])];
}

/**
 *
 * Devuelve una cadena indicando que es un punto duplicado
 * solo si realmente hay puntos duplicados en esa posición.
 * Los paréntesis aparecen si es un dato inicial.
 *
 * @param x - posición x
 * @param y - posición y
 * @param id_duplicado
 * @param parentesis - flag que indica si envolver los duplicados entre paréntesis
 * @returns {string} - cadena indicando el número de duplicado que es
 */
function escribir_duplicados(x,y, id_duplicado, parentesis=false) {
    if(duplicados[String([x,y])] > 1) {
        let cadena = "";
        if (parentesis) {
            cadena += " (";
        } else {
            cadena += "<strong>";
        }
        cadena += traducir("Point") + " " + id_duplicado.toString();
        if (parentesis) {
            cadena += ")";
        } else {
            cadena += "</strong><br>";
        }

        return cadena;
    } else {
        return ""
    }
}

/**
 *
 * Genera un identificador para los puntos de forma creciente.
 * Los puntos que pertenezcan al mismo dato del conjunto de datos
 * original, tendrán el mismo identificador.
 *
 * Cuando detecta que ya hay un punto aumenta el identificador actual.
 *
 * @param x - posición x
 * @param y - posición y
 * @returns {number|*} - identificador generado
 */
function generar_id_duplicado(x,y) {
    if (!(String([x, y]) in duplicados)) {
        duplicados[String([x, y])] = 1;
        return 1;
    } else {
        duplicados[String([x, y])] += 1;
        return duplicados[String([x, y])];
    }
}

/**
 *
 * Declara los puntos en el SVG principal.
 *
 * @param dataset - datos con todos los puntos
 * @returns {*}
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

/**
 *
 * Para Tri-Training, todos los puntos clasificados
 * en la iteración actual pasen a gris. Así se conseguirá
 * un cambio brusco para que el usuario pueda apreciar después
 * el reetiquetado.
 *
 */
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

/**
 *
 * Genera una porción del tooltip cuando
 * el punto/dato es inicial.
 *
 * @param dot - punto del gráfico (con su información)
 * @returns {string} - porción del tooltip como cadena de caracteres
 */
function tooltip_dato_inicial(dot) {
    return "<strong>" + traducir('Initial data') + "</strong>" + escribir_duplicados(dot[0],dot[1], dot[dot.length-1], true) + "<br>" + traducir('Label') + ": " +
        "<span style='color:"+ color(parseInt(dot[2])) +"'>" + mapa[dot[2]] + "</span>";
}

/**
 *
 * Genera una porción del tooltip cuando
 * el punto/dato no ha sido clasificado.
 * Mediante "mostrar_clasificado" se controla
 * que para Self-Training no hace falta indicar un clasificador
 * (solo hay uno).
 *
 * @param mostrar_clasificador - flag para indicar si se necesita indicar el clasificador
 * @returns {string} - porción del tooltip como cadena de caracteres
 */
function un_clasificador_return_no_clasificado(mostrar_clasificador=true) {
    let cadena = "";

    if (mostrar_clasificador) {
        cadena += traducir('Classifier: Not classified') +
        "<br>";
    }

    return  cadena + traducir('Label: Not classified');
}

/**
 *
 * Genera una porción del tooltip cuando
 * el punto/dato ha sido clasificado
 * indicando el clasificador.
 *
 * @param p_data - punto del gráfico (con su información)
 * @returns {string} - porción del tooltip como cadena de caracteres
 */
function tooltip_dato_no_inicial(p_data) {
    return traducir('Classifier') + ": " + obtenerSimboloUnicode(p_data[4]) +
        p_data[4] + "<br>" + traducir('Label') + ": ";
}
