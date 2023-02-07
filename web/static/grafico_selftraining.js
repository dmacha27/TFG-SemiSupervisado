nexit.on("click", next);
previt.on("click", prev);
rep.on("click",reproducir);

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

function databinding(){
    svg.append('g')
        .selectAll("dot")
        .data(dataset)
        .enter()
        .append("circle")
        .attr("cx", function (d) { return x(d[0]); } )
        .attr("cy", function (d) { return y(d[1]); } )
        .attr("r", 3)
        .style("fill", function (d) {
            if (d[3] <= cont) {
                return color(d[2]);
            } else {
                return "grey";
            }
        });

    // Marcar los de la iteración 0
    svg.selectAll("circle")
        .filter(function(d) {
            return d[3] === 0;})
        .style("stroke","yellow");

}

function prev(){
    if (cont > 0){
        cont--;
        svg.selectAll("circle")
            .filter(function(d) {
                return d[3] > cont;
            })
            .style("fill", "grey");
        actualizaProgreso();
    }
}

function next(){
    if (cont < maxit){
        cont++;
        svg.selectAll("circle")
            .filter(function(d) {
                return d[3] === cont;
            })
            .style("fill", function(d){ return color(d[2]);})
            .transition()
            .duration(300)
            .attr("r", 5)
            .transition()
            .duration(300)
            .attr("r", 3);
        actualizaProgreso();
    }
}

function reproducir(){
    // Si vuelve a clickear que pare
    var intervalo = setInterval(function () {
        if (cont >= maxit){
            clearInterval(intervalo);
        }
        next();
    }, 750)
}