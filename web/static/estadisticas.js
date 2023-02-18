
function estadisticagenerica(datos,id,y) {

    let lista = crearListaStat(JSON.parse(datos.stats),id);

    let margin = {top: 10, right: 30, bottom: 40, left: 60},
        width = 850 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;


    let statsvg = d3.select("#"+id)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .style("display", "block")
        .style("margin", "auto");

    let statx = d3.scaleLinear()
        .domain([0, maxit])
        .range([0, width]);

    let staty = d3.scaleLinear()
        .domain([0, 1])
        .range([height, 0]);

    statsvg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(statx));
    statsvg.append("g")
        .call(d3.axisLeft(staty));

    //Etiqueta eje X
    statsvg.append("text")
        .attr("class", "cx")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom)
        .text("Iteración");

    //Etiqueta eje Y
    statsvg.append("text")
        .attr("class", "cy")
        .attr("text-anchor", "middle")
        .attr("y", -margin.left)
        .attr("x", -height / 2)
        .attr("dy", "1em")
        .attr("transform", "rotate(-90)")
        .text(y);

    let pts = statsvg.selectAll("dot")
        .data(lista)
        .enter()
        .append("circle")
        .attr("cx", function (d) { return statx(d[0]); } )
        .attr("cy", function (d) { return staty(d[1]); } )
        .attr("r", 5)
        .attr("fill", "#69b3a2")
        .style("visibility", function (d) {
            if (d[0] <= cont){
                return "visible";
            }else{
                return "hidden";
            }
        })

    for (let i = 0; i < lista.length - 1; i++) {
        statsvg.append("line")
            .data([i+1])
            .attr("id", "nueva")
            .attr("x1", statx(i))
            .attr("y1", staty(lista[i][1]))
            .attr("x2", statx(i + 1))
            .attr("y2", staty(lista[i + 1][1]))
            .attr("stroke", "#69b3a2")
            .attr("stroke-width", 1.5)
            .style("display", "none");
    }

    let lineas = statsvg.selectAll('line[id="nueva"]');

    document.addEventListener('next', next);
    document.addEventListener('prev', prev);


    function next() {
        pts.filter(function(d) {
            return d[0] === cont;
        })
            .style("opacity", 0)
            .transition()
            .duration(600)
            .style("opacity", 1)
            .style("visibility", "visible")

        lineas.filter(function (d) {
            return d === cont;
        })
            .attr("stroke-width", 0)
            .transition()
            .duration(600)
            .attr("stroke-width", 1.5)
            .style("display", "block");


    }

    function prev() {
        pts.filter(function(d) {
            return d[0] > cont;
        })
            .style("visibility", "hidden")

        lineas.filter(function (d) {
            return d > cont;
        })
            .style("display", "none");
    }

}


function crearListaStat(stats,stat){
    let lista = [];
    let aux = stats[stat];

    for (let i = 0; i <= maxit; i++) {
        lista.push([i,aux[i]]);
    }

    return lista;
}