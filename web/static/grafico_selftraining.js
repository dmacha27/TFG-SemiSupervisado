nexit.on("click", next);
previt.on("click", prev);
rep.on("click",reproducir);

let puntos;

const mousemove = function(e, dot) {
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


function preparardataset(datos) {
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

function databinding(dataset){
    puntos = graficosvg.selectAll("dot")
        .data(dataset)
        .enter()
        .append("path")
        .attr("d", simbolos.type(function(d){
            if (d[3] === 0){
                return d3.symbolCircle; // Dato inicial
            }else{
                return d3.symbolCross;
            }
        }).size(35))
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
        .style("stroke", "transparent")
        .style("stroke-width", "3px")
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