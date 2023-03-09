const simbolos = d3.symbol();

let nexit, previt, rep;

let graficosvg, gx, gy, maxit, color, mapa, puntos;

function inicializarGrafico(datos, preparar, binding) {
    nexit = d3.select("#nextit");
    previt = d3.select("#previt");
    rep = d3.select("#reproducir");

    let margin = {top: 80, right: 90, bottom: 60, left: 45},
        width = 850 - margin.left - margin.right,
        height = 700 - margin.top - margin.bottom;

    maxit = datos.iterations;
    let dataset = preparar(JSON.parse(datos.log));
    mapa = JSON.parse(datos.mapa);
    document.getElementById("progreso").max = maxit;

    color = d3.scaleOrdinal()
        .domain(Object.keys(mapa))
        .range(d3.schemeCategory10);

    graficosvg = d3.select("#semisupervisedchart")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .style("display", "block")
        .style("margin", "auto");

    //Etiqueta eje X
    graficosvg.append("text")
        .attr("class", "cx")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom / 2)
        .text(cx);

    //Etiqueta eje Y
    graficosvg.append("text")
        .attr("class", "cy")
        .attr("text-anchor", "middle")
        .attr("y", -margin.left)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .text(cy);

    //Leyenda
    graficosvg.append('g')
        .attr("id","leyenda")
        .selectAll("target")
        .data(Object.keys(mapa))
        .enter()
        .append("text")
        .attr("x", 120)
        .attr("y", function(d,i){ return 100 + i*25;})
        .style("fill", function(d){ return color(parseInt(d));})
        .text(function(d){ return mapa[d];})
        .style("alignment-baseline", "middle")
        .attr("transform", "translate(" + (width -110) + "," + -120 + ")");

    // Nombre del dataset
    graficosvg.append("text")
        .attr("x", width/2)
        .attr("y", -margin.top/2)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text(traducir('Dataset') + ": " + fichero);


    gx = d3.scaleLinear()
        .domain([d3.min(dataset, d => d[0]), d3.max(dataset, d => d[0])])
        .range([0, width]);

    gy = d3.scaleLinear()
        .domain([d3.min(dataset, d => d[1]), d3.max(dataset, d => d[1])])
        .range([height, 0]);

    graficosvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(gx));
    graficosvg.append("g")
        .call(d3.axisLeft(gy));

    //Basado en https://d3-graph-gallery.com/graph/interactivity_tooltip.html#template
    d3.select("#semisupervisedchart")
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

}

const mouseover = function (d) {
    d3.select(".tooltip")
        .style("opacity", 1)
        .style("display", "block")

};

const mouseleave = function (d) {
    d3.select(".tooltip")
        .style("stroke", "none")
        .style("display", "none")
};

function actualizaProgreso(paso){
    document.getElementById("progreso").value=cont;
    document.getElementById("iteracion").innerHTML = cont;
    if (paso === "next"){
        document.dispatchEvent(new Event('next'));
    }else{
        document.dispatchEvent(new Event('prev'));
    }
}

let intervalo = null;
function reproducir(next){
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

function grafico_selftraining(dataset) {
    nexit.on("click", next);
    previt.on("click", prev);
    rep.on("click",reproducir);

    const mousemove_selftraining = function(e, dot) {
        d3.select(".tooltip")
            .html(function() {
                if (dot[3] <= cont && dot[2] !== -1) {
                    if (dot[3] === 0){
                        return "DATO INICIAL<br>" + cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br>Etiqueta: " + mapa[dot[2]];
                    }else {
                        return cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br>Etiqueta: " + mapa[dot[2]];
                    }
                } else {
                    return cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br>Etiqueta: Sin clasificar";
                }
            })
            .style("left", (e.clientX + 10) + "px")
            .style("top", (e.clientY - 75) + "px");
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
        .on("mouseover", mouseover)
        .on("mousemove", function (e) {
            mousemove_selftraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave);

    document.addEventListener('next_reproducir', next);

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

function obtenerSimbolo(clf){
    if(clf === -1 || clf_forma.indexOf(clf) === 0){ return d3.symbolCircle
    } else if (clf_forma.indexOf(clf) === 1){ return d3.symbolCross
    } else if (clf_forma.indexOf(clf) === 2){ return d3.symbolTriangle
    } else if (clf_forma.indexOf(clf) === 3){ return d3.symbolSquare
    }}

function obtenerSimboloUnicode(clf){
    if(clf === -1 || clf_forma.indexOf(clf) === 0){ return "&#9679"
    } else if (clf_forma.indexOf(clf) === 1){ return "&#128934"
    } else if (clf_forma.indexOf(clf) === 2){ return "&#9650"
    } else if (clf_forma.indexOf(clf) === 3){ return "&#9632"
    }}

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

    for (var i = 0; i < dataset.length; i++){
        clasificadores.add(dataset[i][4]);
    }
    clf_forma = Array.from(clasificadores);

    return dataset;
}

function databinding_cotraining(dataset) {
    nexit.on("click", next_co);
    previt.on("click", prev_co);
    rep.on("click", reproducir);

    const mousemove_cotraining = function (e, dot) {
        d3.select(".tooltip")
            .html(function () {
                if (dot[3] <= cont && dot[2] !== -1) {
                    if (dot[3] === 0) {
                        return traducir('Initial data') + "<br>" + cx + ": " + dot[0] + "<br>" + cy + ": " + dot[1] + "<br>" + traducir('Label') + ": " + mapa[dot[2]];
                    } else {
                        return cx + ": " + dot[0] + "<br>" + cy + ": " + dot[1] + "<br>" + traducir('Classifier') + ": " + obtenerSimboloUnicode(dot[4]) + dot[4] + "<br>" + traducir('Label') + ": " + mapa[dot[2]];
                    }
                } else {
                    return cx + ": " + dot[0] + "<br>" + cy + ": " + dot[1] + "<br>" + traducir('Classifier: Not classified') + "<br>" + traducir('Label: Not classified');
                }
            })
            .style("left", (e.clientX + 10) + "px")
            .style("top", (e.clientY - 75) + "px");
    };

    puntos = graficosvg.selectAll("dot")
        .data(dataset)
        .enter()
        .append("path")
        .attr("d", simbolos.type(d3.symbolCircle).size(35))
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
        .on("mouseover", mouseover)
        .on("mousemove", function (e) {
            mousemove_cotraining(e, d3.select(this).datum());
        })
        .on("mouseleave", mouseleave);


    document.addEventListener('next_reproducir', next_co);
}

function puntos_en_x_y(x,y) {
    return puntos.filter(function(d) {
        return d[0] === x && d[1] === y;
    })
}

function preparardataset_democraticcolearning(datos) {
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
            for (var i = 0; i < clfs[key].length; i++) {
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

function databinding_democraticcolearning(dataset) {
    nexit.on("click", next_co);
    previt.on("click", prev_co);
    rep.on("click", reproducir);

    const mousemove_democraticcolearning = function(e, dot) {
        d3.select(".tooltip")
            .html(function() {
                let puntos_posicion = []
                puntos_posicion = puntos_en_x_y(dot[0], dot[1])._groups[0];

                let cadena_tooltip = "";

                for (let i = 0; i < puntos_posicion.length; i++) {

                    let p_data = puntos_posicion[i].__data__

                    if (p_data[3] <= cont && p_data[2] !== -1) {
                        if (p_data[3] === 0){
                            cadena_tooltip += traducir('Initial data') + "<br>" + cx +": " + p_data[0] +"<br>" + cy + ": " + p_data[1] + "<br>" + traducir('Label') + ": " + mapa[p_data[2]];
                        }else {
                            cadena_tooltip += cx +": " + p_data[0] +"<br>" + cy + ": " + p_data[1] +"<br>" + traducir('Classifier') + ": " + obtenerSimboloUnicode(p_data[4]) + p_data[4] + "<br>" + traducir('Label') + ": " + mapa[p_data[2]];
                        }
                        cadena_tooltip += "<br>-------<br>";
                    } else if (p_data[2] === -1){
                        cadena_tooltip += cx + ": " + p_data[0] + "<br>" + cy + ": " + p_data[1] + "<br>" + traducir('Classifier: Not classified') + "<br>" + traducir('Label: Not classified');
                        cadena_tooltip += "<br>-------<br>";
                    }

                }
                return cadena_tooltip
            })
            .style("left", (e.clientX + 10) + "px")
            .style("top", (e.clientY - 75) + "px");
    };

    const mouseleave_democraticcolearning = function(e, dot) {
        d3.select(".tooltip")
            .style("stroke", "none")
            .style("display", "none")
    };

    puntos = graficosvg.selectAll("dot")
        .data(dataset)
        .enter()
        .append("path")
        .attr("d", simbolos.type(d3.symbolCircle).size(35))
        .attr("transform", function (d) {
            return "translate(" + gx(d[0]) + "," + gy(d[1]) + ")";
        })
        .style("fill", function (d) {
            if (d[4] === "inicio") {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .on("mouseover", mouseover)
        .on("mousemove", function (e) {
            mousemove_democraticcolearning(e, d3.select(this).datum());
        })
        .on("mouseleave", function (e) {
            mouseleave_democraticcolearning(e, d3.select(this).datum());
        })

    document.addEventListener('next_reproducir', next_co);
}


