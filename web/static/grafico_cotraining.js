nexit.on("click", next);
previt.on("click", prev);
rep.on("click",reproducir);

let clf_forma;
let puntos;

const mousemove = function(e, dot) {
    d3.select(".tooltip")
        .html(function() {
            if (dot[3] <= cont && dot[2] !== -1) {
                if (dot[3] === 0){
                    return "DATO INICIAL<br>" + cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] + "<br>Etiqueta: " + mapa[dot[2]];
                }else {
                    return cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] +"<br>Clasificador: " + dot[4] + "<br>Etiqueta: " + mapa[dot[2]];
                }
            } else {
                return cx +": " + dot[0] +"<br>" + cy + ": " + dot[1] +"<br>Clasificador: Sin clasificar" + "<br>Etiqueta: Sin clasificar";
            }
        })
        .style("left", (e.pageX + 10) + "px")
        .style("top", (e.pageY + 5 ) + "px");
};

function preparardataset(datos) {
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

function databinding(dataset){
    puntos = graficosvg.selectAll("dot")
        .data(dataset)
        .enter()
        .append("path")
        .attr("d", simbolos.type(d3.symbolCircle).size(35))
        .attr("transform", function(d) {
            return "translate(" + gx(d[0]) + "," + gy(d[1]) + ")";
        })
        .style("fill", function (d) {
            if (d[3] <= cont) {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .on("mouseover", mouseover)
        .on("mousemove", function(e) { mousemove(e, d3.select(this).datum()); })
        .on("mouseleave", mouseleave);
}


function prev(){
    if (cont > 0){
        cont--;
        puntos.filter(function(d) {
            return d[3] > cont;
        })
            .attr("d", simbolos.type(d3.symbolCircle).size(35))
            .style("fill", "grey");
        actualizaProgreso();
    }
}

function next(){
    if (cont < maxit){
        cont++;
        puntos.filter(function(d) {
            return d[3] === cont && d[2] !== -1;
        })
            .style("fill", function(d){ return color(d[2]);})
            .transition()
            .duration(0)
            .attr("d", simbolos.type(function(d){return obtenerSimbolo(d)}).size(35))
            .transition()
            .duration(300)
            .attr("d", simbolos.size(125))
            .transition()
            .duration(300)
            .attr("d", simbolos.size(35));

        actualizaProgreso();
    }
}

function obtenerSimbolo(d){
    if(clf_forma.indexOf(d[4]) === 0){ return d3.symbolCircle // Dato inicial
    } else if (clf_forma.indexOf(d[4]) === 1){ return d3.symbolCross
    } else if (clf_forma.indexOf(d[4]) === 2){ return d3.symbolTriangle
    }}
