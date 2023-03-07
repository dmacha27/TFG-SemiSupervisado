nexit.on("click", next);
previt.on("click", prev);
rep.on("click",reproducir);

let clf_forma;
let puntos;

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

function puntos_en_x_y(x,y) {
    return puntos.filter(function(d) {
        return d[0] === x && d[1] === y;
    })
}

const mousemove = function(e, dot) {
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

const mouseleave_democratic = function(e, dot) {
    d3.select(".tooltip")
        .style("stroke", "none")
        .style("display", "none")
};

function preparardataset(datos) {
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
            if (d[4] === "inicio") {
                return color(d[2]);
            } else {
                return "grey";
            }
        })
        .on("mouseover", mouseover)
        .on("mousemove", function(e) { mousemove(e, d3.select(this).datum()); })
        .on("mouseleave", function(e) { mouseleave_democratic(e, d3.select(this).datum()); })
}


function prev(){
    if (cont > 0){
        cont--;
        puntos.filter(function(d) {
            return d[3] > cont;
        })
            .attr("d", simbolos.type(d3.symbolCircle).size(35))
            .style("fill", "grey");
        actualizaProgreso("prev");
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
            .attr("d", simbolos.type(function(d){return obtenerSimbolo(d[4])}).size(35))
            .transition()
            .duration(300)
            .attr("d", simbolos.size(125))
            .transition()
            .duration(300)
            .attr("d", simbolos.size(35));

        actualizaProgreso("next");
    }
}


